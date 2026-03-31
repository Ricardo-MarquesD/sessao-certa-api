import asyncio
from types import SimpleNamespace
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from domain.service import google_calendar_service as google_calendar_service_module
from domain.service.google_calendar_service import GoogleCalendarService


@pytest.fixture
def google_settings(monkeypatch):
    monkeypatch.setattr(google_calendar_service_module.settings, "google_client_id", "client-id-123")
    monkeypatch.setattr(google_calendar_service_module.settings, "google_client_secret", "client-secret-123")
    monkeypatch.setattr(google_calendar_service_module.settings, "google_redirect_uri", "http://localhost:8000/google-calendar/callback")
    monkeypatch.setattr(google_calendar_service_module.settings, "google_auth_uri", "https://accounts.google.com/o/oauth2/v2/auth")
    monkeypatch.setattr(google_calendar_service_module.settings, "google_token_uri", "https://oauth2.googleapis.com/token")
    monkeypatch.setattr(google_calendar_service_module.settings, "google_calendar_scopes", "https://www.googleapis.com/auth/calendar.events")


def test_build_authorization_url_contains_state_and_redirect_uri(google_settings):
    establishment_id = uuid4()

    url = GoogleCalendarService.build_authorization_url(establishment_id)

    assert "client_id=client-id-123" in url
    assert "redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fgoogle-calendar%2Fcallback" in url
    assert f"state={establishment_id}" in url
    assert "scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcalendar.events" in url


def test_connect_establishment_updates_google_fields(monkeypatch, google_settings):
    establishment_id = uuid4()
    fake_establishment = SimpleNamespace(
        id=establishment_id,
        google_calendar_access_token=None,
        google_calendar_refresh_token=None,
        google_calendar_expiry=None,
        google_calendar_id=None,
    )

    class FakeRepository:
        def __init__(self, db):
            self.db = db

        def get_by_id(self, establishment_uuid):
            return fake_establishment if establishment_uuid == establishment_id else None

        def update(self, establishment):
            return establishment

    async def fake_exchange_code_for_tokens(code):
        return {
            "access_token": "access-123",
            "refresh_token": "refresh-123",
            "expires_in": 3600,
        }

    monkeypatch.setattr(google_calendar_service_module, "EstablishmentRepository", FakeRepository)
    monkeypatch.setattr(GoogleCalendarService, "exchange_code_for_tokens", staticmethod(fake_exchange_code_for_tokens))

    result = asyncio.run(GoogleCalendarService.connect_establishment(establishment_id, "code-123", db=object()))

    assert result.google_calendar_access_token == "access-123"
    assert result.google_calendar_refresh_token == "refresh-123"
    assert result.google_calendar_id == "primary"


def test_sync_scheduling_creates_google_event_and_persists_event_id(monkeypatch, google_settings):
    scheduling_id = uuid4()
    appointment_date = datetime(2026, 3, 27, 10, 30, tzinfo=timezone.utc)
    establishment = SimpleNamespace(
        google_calendar_access_token="access-123",
        google_calendar_refresh_token="refresh-123",
        google_calendar_expiry=None,
        google_calendar_id="primary",
        establishment_name="Barbearia Central",
    )
    fake_scheduling = SimpleNamespace(
        id=scheduling_id,
        establishment=establishment,
        employee=SimpleNamespace(user=SimpleNamespace(user_name="João")),
        customer=SimpleNamespace(customer_name="Maria", phone_number="11999999999"),
        service=SimpleNamespace(service_name="Corte", time_duration=30),
        appointment_date=appointment_date,
        google_calendar_event_id=None,
        calculate_end_time=lambda: appointment_date + timedelta(minutes=30),
    )

    created_events = []

    class FakeSchedulingRepository:
        def __init__(self, db):
            self.db = db

        def get_by_id(self, scheduling_uuid):
            return fake_scheduling if scheduling_uuid == scheduling_id else None

        def update(self, scheduling):
            created_events.append(scheduling.google_calendar_event_id)
            return scheduling

    async def fake_get_access_token(establishment_arg, db):
        return "access-123", establishment_arg

    async def fake_request_json(*, method, url, token, json_payload=None):
        assert method == "POST"
        assert token == "access-123"
        assert json_payload["summary"] == "Corte - Maria (11999999999)"
        return {"id": "event-123"}

    monkeypatch.setattr(google_calendar_service_module, "SchedulingRepository", FakeSchedulingRepository)
    monkeypatch.setattr(GoogleCalendarService, "_get_access_token", staticmethod(fake_get_access_token))
    monkeypatch.setattr(GoogleCalendarService, "_request_json", staticmethod(fake_request_json))

    result = asyncio.run(GoogleCalendarService.sync_scheduling(scheduling_id, "create", db=object()))

    assert result["status"] == "synced"
    assert result["event_id"] == "event-123"
    assert created_events == ["event-123"]


def test_sync_scheduling_refreshes_expired_token(monkeypatch, google_settings):
    establishment = SimpleNamespace(
        google_calendar_access_token="old-token",
        google_calendar_refresh_token="refresh-123",
        google_calendar_expiry=None,
        google_calendar_id="primary",
        establishment_name="Barbearia Central",
    )

    async def fake_refresh_access_token(establishment_arg, db):
        establishment_arg.google_calendar_access_token = "new-token"
        return establishment_arg

    monkeypatch.setattr(GoogleCalendarService, "_has_valid_token", staticmethod(lambda establishment_arg: False))
    monkeypatch.setattr(GoogleCalendarService, "_refresh_access_token", staticmethod(fake_refresh_access_token))

    access_token, refreshed = asyncio.run(GoogleCalendarService._get_access_token(establishment, db=object()))

    assert access_token == "new-token"
    assert refreshed.google_calendar_access_token == "new-token"