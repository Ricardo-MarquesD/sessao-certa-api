from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import lru_cache

import httplib2
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_httplib2 import AuthorizedHttp
from sqlalchemy.orm import Session

from config import settings
from domain.entities import Establishment
from infra.repository import EstablishmentRepository

from .adapter import GoogleCalendarAdapter


@dataclass
class GoogleCalendarClientFactory:
    http: httplib2.Http
    token_refresh_buffer_seconds: int = 60

    def build_adapter(self, *, establishment: Establishment, db: Session) -> GoogleCalendarAdapter:
        self._validate_settings()
        credentials = self._build_credentials(establishment)
        credentials = self._refresh_if_needed(credentials, establishment, db)
        service = self._build_service(credentials)
        return GoogleCalendarAdapter(service)

    def _validate_settings(self) -> None:
        if not settings.google_client_id:
            raise ValueError("GOOGLE_CLIENT_ID is required")
        if not settings.google_client_secret:
            raise ValueError("GOOGLE_CLIENT_SECRET is required")
        if not settings.google_token_uri:
            raise ValueError("GOOGLE_TOKEN_URI is required")

    def _build_credentials(self, establishment: Establishment) -> Credentials:
        access_token = establishment.google_calendar_access_token
        refresh_token = establishment.google_calendar_refresh_token

        if not access_token and not refresh_token:
            raise ValueError("Google Calendar access token or refresh token is required")

        return Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri=settings.google_token_uri,
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
            scopes=self._split_scopes(settings.google_calendar_scopes),
            expiry=establishment.google_calendar_expiry,
        )

    def _refresh_if_needed(self, credentials: Credentials, establishment: Establishment, db: Session) -> Credentials:
        if not self._needs_refresh(credentials):
            return credentials

        if not credentials.refresh_token:
            raise ValueError("Google Calendar refresh token is required")

        credentials.refresh(Request())

        if not credentials.token:
            raise ValueError("Google OAuth did not return an access token")

        establishment.google_calendar_access_token = credentials.token
        if credentials.refresh_token:
            establishment.google_calendar_refresh_token = credentials.refresh_token
        establishment.google_calendar_expiry = self._normalize_expiry(credentials.expiry)
        EstablishmentRepository(db).update(establishment)
        return credentials

    def _needs_refresh(self, credentials: Credentials) -> bool:
        expiry = credentials.expiry
        if expiry is None:
            return False

        now = datetime.now(expiry.tzinfo) if expiry.tzinfo else datetime.now()
        buffer_window = timedelta(seconds=self.token_refresh_buffer_seconds)
        return expiry <= now + buffer_window

    def _normalize_expiry(self, expiry: datetime | None) -> datetime | None:
        if expiry is None:
            return None
        if expiry.tzinfo is not None:
            return expiry.replace(tzinfo=None)
        return expiry

    def _build_service(self, credentials: Credentials):
        authorized_http = AuthorizedHttp(credentials, http=self.http)
        return build("calendar", "v3", http=authorized_http, cache_discovery=False)

    def _split_scopes(self, value: str) -> list[str]:
        return [scope for scope in value.split() if scope]


@lru_cache(maxsize=1)
def get_google_calendar_client_factory() -> GoogleCalendarClientFactory:
    http = httplib2.Http(timeout=30)
    return GoogleCalendarClientFactory(http=http)
