from __future__ import annotations

from dataclasses import dataclass
import random
import time
from typing import Any, Callable

import httplib2
from google.auth.exceptions import TransportError
from googleapiclient.errors import HttpError


_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class GoogleCalendarAdapterError(RuntimeError):
    def __init__(self, message: str, *, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


@dataclass
class BackoffPolicy:
    max_attempts: int = 5
    base_delay: float = 0.5
    max_delay: float = 8.0
    jitter_ratio: float = 0.1

    def execute(self, func: Callable[[], Any]) -> Any:
        last_exc: Exception | None = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                return func()
            except HttpError as exc:
                status = getattr(exc.resp, "status", None)
                if status not in _RETRYABLE_STATUS_CODES:
                    raise GoogleCalendarAdapterError(self._format_http_error(exc), status_code=status) from exc
                last_exc = exc
            except (TransportError, httplib2.HttpLib2Error, OSError, TimeoutError) as exc:
                last_exc = exc

            if attempt == self.max_attempts:
                break

            time.sleep(self._compute_delay(attempt))

        raise GoogleCalendarAdapterError(self._format_retry_error(last_exc)) from last_exc

    def _compute_delay(self, attempt: int) -> float:
        delay = min(self.max_delay, self.base_delay * (2 ** (attempt - 1)))
        jitter = delay * self.jitter_ratio
        return delay + random.uniform(0, jitter)

    def _format_http_error(self, exc: HttpError) -> str:
        status = getattr(exc.resp, "status", "unknown")
        reason = getattr(exc.resp, "reason", "") or ""
        reason = f" reason={reason}" if reason else ""
        return f"Google Calendar API error: status={status}{reason}"

    def _format_retry_error(self, exc: Exception | None) -> str:
        if isinstance(exc, HttpError):
            return self._format_http_error(exc)
        if exc is None:
            return "Google Calendar API request failed after retries"
        return f"Google Calendar API request failed after retries: {exc}"


class GoogleCalendarAdapter:
    DEFAULT_FIELDS = "items(id,summary,description,start,end,status,updated),nextPageToken"

    def __init__(self, service, *, backoff_policy: BackoffPolicy | None = None):
        self._service = service
        self._backoff = backoff_policy or BackoffPolicy()

    def create_event(self, *, calendar_id: str, payload: dict) -> dict:
        request = self._service.events().insert(calendarId=calendar_id, body=payload)
        response = self._backoff.execute(request.execute)
        return response or {}

    def update_event(self, *, calendar_id: str, event_id: str, payload: dict) -> dict:
        request = self._service.events().patch(calendarId=calendar_id, eventId=event_id, body=payload)
        response = self._backoff.execute(request.execute)
        return response or {}

    def delete_event(self, *, calendar_id: str, event_id: str) -> None:
        request = self._service.events().delete(calendarId=calendar_id, eventId=event_id)
        self._backoff.execute(request.execute)

    def list_events(
        self,
        *,
        calendar_id: str,
        time_min: str | None = None,
        time_max: str | None = None,
        page_size: int = 250,
        fields: str | None = None,
        single_events: bool = True,
        order_by: str = "startTime",
    ) -> list[dict]:
        events: list[dict] = []
        request = self._service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=page_size,
            fields=fields or self.DEFAULT_FIELDS,
            singleEvents=single_events,
            orderBy=order_by,
        )

        while request is not None:
            response = self._backoff.execute(request.execute)
            events.extend(response.get("items", []))
            request = self._service.events().list_next(previous_request=request, previous_response=response)

        return events
