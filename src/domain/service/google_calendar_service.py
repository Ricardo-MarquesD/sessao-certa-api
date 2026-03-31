from __future__ import annotations

from datetime import datetime, timedelta
from urllib.parse import urlencode
from uuid import UUID

import aiohttp
from sqlalchemy.orm import Session

from config import settings
from domain.entities import Establishment, Scheduling
from infra.repository import EstablishmentRepository, SchedulingRepository
from utils.value_object import GoogleCalendarHelper


class GoogleCalendarService:
    API_BASE_URI = "https://www.googleapis.com/calendar/v3"
    TOKEN_REFRESH_BUFFER_SECONDS = 60

    @staticmethod
    def _calendar_id(establishment: Establishment) -> str:
        return establishment.google_calendar_id or "primary"

    @staticmethod
    def _has_valid_token(establishment: Establishment) -> bool:
        if not establishment.google_calendar_access_token:
            return False

        if establishment.google_calendar_expiry is None:
            return True

        return establishment.google_calendar_expiry > datetime.now() + timedelta(seconds=GoogleCalendarService.TOKEN_REFRESH_BUFFER_SECONDS)

    @staticmethod
    async def _refresh_access_token(establishment: Establishment, db: Session) -> Establishment:
        if not establishment.google_calendar_refresh_token:
            raise ValueError("Google Calendar refresh token is required")

        payload = {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "refresh_token": establishment.google_calendar_refresh_token,
            "grant_type": "refresh_token",
        }

        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(settings.google_token_uri, data=payload) as response:
                response.raise_for_status()
                data = await response.json()

        if "error" in data:
            error = data["error"]
            message = error.get("message") if isinstance(error, dict) else str(error)
            raise ValueError(f"Google OAuth error: {message}")

        access_token = data.get("access_token")
        if not access_token:
            raise ValueError("Google OAuth did not return an access_token")

        establishment.google_calendar_access_token = access_token
        if data.get("refresh_token"):
            establishment.google_calendar_refresh_token = data["refresh_token"]

        expires_in = int(data.get("expires_in", 0) or 0)
        establishment.google_calendar_expiry = datetime.now() + timedelta(seconds=expires_in) if expires_in else None

        return EstablishmentRepository(db).update(establishment)

    @staticmethod
    async def _get_access_token(establishment: Establishment, db: Session) -> tuple[str, Establishment]:
        if GoogleCalendarService._has_valid_token(establishment):
            return establishment.google_calendar_access_token or "", establishment

        refreshed = await GoogleCalendarService._refresh_access_token(establishment, db)
        access_token = refreshed.google_calendar_access_token or ""

        if not access_token:
            raise ValueError("Google Calendar access token is required")

        return access_token, refreshed

    @staticmethod
    async def _request_json(
        *,
        method: str,
        url: str,
        token: str,
        json_payload: dict | None = None,
    ) -> dict | None:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.request(method, url, headers=headers, json=json_payload) as response:
                response.raise_for_status()
                if response.status == 204 or response.content_length == 0:
                    return None
                return await response.json()

    @staticmethod
    def _build_schedule_payload(scheduling: Scheduling) -> dict:
        if scheduling.appointment_date is None:
            raise ValueError("Scheduling appointment_date is required")

        end_date = scheduling.calculate_end_time()
        summary = GoogleCalendarHelper.build_event_summary(
            service_name=scheduling.service.service_name,
            customer_name=scheduling.customer.customer_name,
            phone_number=scheduling.customer.phone_number,
        )
        description = GoogleCalendarHelper.build_description(
            establishment_name=scheduling.establishment.establishment_name,
            employee_name=getattr(getattr(scheduling.employee, "user", None), "user_name", None),
            service_name=scheduling.service.service_name,
            customer_name=scheduling.customer.customer_name,
            phone_number=scheduling.customer.phone_number,
        )

        return GoogleCalendarHelper.build_event_payload(
            summary=summary,
            start=scheduling.appointment_date,
            end=end_date,
            description=description,
        )

    @staticmethod
    def build_authorization_url(establishment_id: UUID) -> str:
        if not settings.google_redirect_uri:
            raise ValueError("GOOGLE_REDIRECT_URI is required")

        params = {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": settings.google_calendar_scopes,
            "access_type": "offline",
            "prompt": "consent",
            "include_granted_scopes": "true",
            "state": str(establishment_id),
        }

        return f"{settings.google_auth_uri}?{urlencode(params)}"

    @staticmethod
    async def exchange_code_for_tokens(code: str) -> dict:
        if not settings.google_redirect_uri:
            raise ValueError("GOOGLE_REDIRECT_URI is required")

        payload = {
            "code": code,
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri": settings.google_redirect_uri,
            "grant_type": "authorization_code",
        }

        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(settings.google_token_uri, data=payload) as response:
                response.raise_for_status()
                data = await response.json()

        if "error" in data:
            error = data["error"]
            message = error.get("message") if isinstance(error, dict) else str(error)
            raise ValueError(f"Google OAuth error: {message}")

        if not data.get("access_token"):
            raise ValueError("Google OAuth did not return an access_token")

        return data

    @staticmethod
    async def connect_establishment(establishment_id: UUID, code: str, db: Session) -> Establishment:
        repository = EstablishmentRepository(db)
        establishment = repository.get_by_id(establishment_id)

        if establishment is None:
            raise ValueError("Establishment not found")

        token_data = await GoogleCalendarService.exchange_code_for_tokens(code)
        expires_in = int(token_data.get("expires_in", 0) or 0)
        expiry_at = datetime.now() + timedelta(seconds=expires_in) if expires_in else None

        establishment.google_calendar_access_token = token_data.get("access_token")
        establishment.google_calendar_refresh_token = token_data.get("refresh_token")
        establishment.google_calendar_expiry = expiry_at
        establishment.google_calendar_id = token_data.get("google_calendar_id") or "primary"

        return repository.update(establishment)

    @staticmethod
    async def sync_scheduling(scheduling_id: UUID, action: str, db: Session) -> dict:
        scheduling_repository = SchedulingRepository(db)
        scheduling = scheduling_repository.get_by_id(scheduling_id)

        if scheduling is None:
            raise ValueError("Scheduling not found")

        establishment = scheduling.establishment
        if establishment is None:
            raise ValueError("Establishment not found for scheduling")

        access_token, _ = await GoogleCalendarService._get_access_token(establishment, db)
        calendar_id = GoogleCalendarService._calendar_id(establishment)
        event_id = scheduling.google_calendar_event_id
        base_url = f"{GoogleCalendarService.API_BASE_URI}/calendars/{calendar_id}/events"

        if action == "cancel":
            if not event_id:
                return {
                    "scheduling_id": str(scheduling.id),
                    "action": action,
                    "status": "skipped_no_event_id",
                }

            await GoogleCalendarService._request_json(
                method="DELETE",
                url=f"{base_url}/{event_id}",
                token=access_token,
            )

            scheduling.google_calendar_event_id = None
            scheduling_repository.update(scheduling)

            return {
                "scheduling_id": str(scheduling.id),
                "action": action,
                "status": "deleted",
            }

        payload = GoogleCalendarService._build_schedule_payload(scheduling)

        if event_id:
            result = await GoogleCalendarService._request_json(
                method="PATCH",
                url=f"{base_url}/{event_id}",
                token=access_token,
                json_payload=payload,
            )
        else:
            result = await GoogleCalendarService._request_json(
                method="POST",
                url=base_url,
                token=access_token,
                json_payload=payload,
            )

        if isinstance(result, dict) and result.get("id"):
            scheduling.google_calendar_event_id = result["id"]
            scheduling_repository.update(scheduling)

        return {
            "scheduling_id": str(scheduling.id),
            "action": action,
            "status": "synced",
            "event_id": scheduling.google_calendar_event_id,
        }