from __future__ import annotations

import asyncio
from datetime import datetime
from uuid import UUID

import aiohttp
from google.auth.exceptions import GoogleAuthError
from google_auth_oauthlib.flow import Flow
from sqlalchemy.orm import Session

from config import settings
from domain.entities import Establishment, Scheduling
from infra.google_calendar import GoogleCalendarClientFactory, GoogleCalendarAdapterError
from infra.repository import EstablishmentRepository, SchedulingRepository
from utils.value_object import GoogleCalendarHelper


class GoogleCalendarService:
    TOKEN_REVOKE_URI = "https://oauth2.googleapis.com/revoke"
    DEFAULT_CALENDAR_ID = "primary"

    def __init__(self, client_factory: GoogleCalendarClientFactory):
        self._client_factory = client_factory

    @staticmethod
    def _calendar_id(establishment: Establishment) -> str:
        return establishment.google_calendar_id or GoogleCalendarService.DEFAULT_CALENDAR_ID

    @staticmethod
    def _normalize_expiry(expiry: datetime | None) -> datetime | None:
        if expiry is None:
            return None
        if expiry.tzinfo is not None:
            return expiry.replace(tzinfo=None)
        return expiry

    @staticmethod
    def _split_scopes(value: str) -> list[str]:
        return [scope for scope in value.split() if scope]

    def _build_flow(self) -> Flow:
        if not settings.google_client_id:
            raise ValueError("GOOGLE_CLIENT_ID is required")
        if not settings.google_client_secret:
            raise ValueError("GOOGLE_CLIENT_SECRET is required")
        if not settings.google_redirect_uri:
            raise ValueError("GOOGLE_REDIRECT_URI is required")

        client_config = {
            "web": {
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "auth_uri": settings.google_auth_uri,
                "token_uri": settings.google_token_uri,
                "redirect_uris": [settings.google_redirect_uri],
            }
        }

        flow = Flow.from_client_config(
            client_config,
            scopes=self._split_scopes(settings.google_calendar_scopes),
        )
        flow.redirect_uri = settings.google_redirect_uri
        return flow

    def build_authorization_url(self, establishment_id: UUID) -> str:
        flow = self._build_flow()
        authorization_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
            state=str(establishment_id),
        )
        return authorization_url

    def _exchange_code_for_tokens(self, code: str):
        flow = self._build_flow()
        flow.fetch_token(code=code)
        credentials = flow.credentials

        if not credentials or not credentials.token:
            raise ValueError("Google OAuth did not return an access token")

        return credentials

    async def connect_establishment(self, establishment_id: UUID, code: str, db: Session) -> Establishment:
        repository = EstablishmentRepository(db)
        establishment = repository.get_by_id(establishment_id)

        if establishment is None:
            raise ValueError("Establishment not found")

        try:
            credentials = await asyncio.to_thread(self._exchange_code_for_tokens, code)
        except GoogleAuthError as exc:
            raise ValueError(f"Google OAuth error: {exc}") from exc

        establishment.google_calendar_access_token = credentials.token
        if credentials.refresh_token:
            establishment.google_calendar_refresh_token = credentials.refresh_token
        establishment.google_calendar_expiry = self._normalize_expiry(credentials.expiry)
        if not establishment.google_calendar_id:
            establishment.google_calendar_id = self.DEFAULT_CALENDAR_ID

        return repository.update(establishment)

    async def disconnect_establishment(self, establishment_id: UUID, db: Session) -> dict:
        repository = EstablishmentRepository(db)
        establishment = repository.get_by_id(establishment_id)

        if establishment is None:
            raise ValueError("Establishment not found")

        token_to_revoke = establishment.google_calendar_refresh_token or establishment.google_calendar_access_token
        revoked = False

        if token_to_revoke:
            try:
                await self._revoke_token(token_to_revoke)
                revoked = True
            except Exception:
                revoked = False

        establishment.google_calendar_access_token = None
        establishment.google_calendar_refresh_token = None
        establishment.google_calendar_expiry = None
        establishment.google_calendar_id = None
        repository.update(establishment)

        return {
            "establishment_id": str(establishment.id),
            "disconnected": True,
            "revoked": revoked,
        }

    async def sync_scheduling(self, scheduling_id: UUID, action: str, db: Session) -> dict:
        scheduling_repository = SchedulingRepository(db)
        scheduling = scheduling_repository.get_by_id(scheduling_id)

        if scheduling is None:
            raise ValueError("Scheduling not found")

        establishment = scheduling.establishment
        if establishment is None:
            raise ValueError("Establishment not found for scheduling")

        adapter = self._client_factory.build_adapter(establishment=establishment, db=db)
        calendar_id = self._calendar_id(establishment)
        event_id = scheduling.google_calendar_event_id

        try:
            if action == "cancel":
                if not event_id:
                    return {
                        "scheduling_id": str(scheduling.id),
                        "action": action,
                        "status": "skipped_no_event_id",
                    }

                await asyncio.to_thread(adapter.delete_event, calendar_id=calendar_id, event_id=event_id)

                scheduling.google_calendar_event_id = None
                scheduling_repository.update(scheduling)

                return {
                    "scheduling_id": str(scheduling.id),
                    "action": action,
                    "status": "deleted",
                }

            payload = self._build_schedule_payload(scheduling)

            if event_id:
                result = await asyncio.to_thread(
                    adapter.update_event,
                    calendar_id=calendar_id,
                    event_id=event_id,
                    payload=payload,
                )
            else:
                result = await asyncio.to_thread(
                    adapter.create_event,
                    calendar_id=calendar_id,
                    payload=payload,
                )
        except GoogleCalendarAdapterError as exc:
            raise ValueError(str(exc)) from exc

        if isinstance(result, dict) and result.get("id"):
            scheduling.google_calendar_event_id = result["id"]
            scheduling_repository.update(scheduling)

        return {
            "scheduling_id": str(scheduling.id),
            "action": action,
            "status": "synced",
            "event_id": scheduling.google_calendar_event_id,
        }

    @staticmethod
    async def _revoke_token(token: str) -> None:
        payload = {"token": token}

        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(GoogleCalendarService.TOKEN_REVOKE_URI, data=payload) as response:
                response.raise_for_status()

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