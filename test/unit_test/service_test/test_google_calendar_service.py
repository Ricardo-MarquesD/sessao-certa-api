import asyncio
from types import SimpleNamespace
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse
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

    service = GoogleCalendarService(client_factory=SimpleNamespace())
    url = service.build_authorization_url(establishment_id)
    query = parse_qs(urlparse(url).query)

    assert query["client_id"] == ["client-id-123"]
    assert query["redirect_uri"] == ["http://localhost:8000/google-calendar/callback"]
    assert query["state"] == [str(establishment_id)]
    assert query["scope"] == ["https://www.googleapis.com/auth/calendar.events"]


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

    async def fake_to_thread(func, *args, **kwargs):
        return func(*args, **kwargs)

    fake_credentials = SimpleNamespace(
        token="access-123",
        refresh_token="refresh-123",
        expiry=datetime(2026, 3, 27, 10, 30),
    )

    monkeypatch.setattr(google_calendar_service_module, "EstablishmentRepository", FakeRepository)
    monkeypatch.setattr(google_calendar_service_module.asyncio, "to_thread", fake_to_thread)
    monkeypatch.setattr(GoogleCalendarService, "_exchange_code_for_tokens", lambda self, code: fake_credentials)

    service = GoogleCalendarService(client_factory=SimpleNamespace())
    result = asyncio.run(service.connect_establishment(establishment_id, "code-123", db=object()))

    assert result.google_calendar_access_token == "access-123"
    assert result.google_calendar_refresh_token == "refresh-123"
    assert result.google_calendar_id == "primary"


def test_disconnect_establishment_revokes_and_clears_tokens(monkeypatch, google_settings):
    establishment_id = uuid4()
    fake_establishment = SimpleNamespace(
        id=establishment_id,
        google_calendar_access_token="access-123",
        google_calendar_refresh_token="refresh-123",
        google_calendar_expiry=datetime(2026, 3, 27, 10, 30),
        google_calendar_id="primary",
    )

    class FakeRepository:
        def __init__(self, db):
            self.db = db

        def get_by_id(self, establishment_uuid):
            return fake_establishment if establishment_uuid == establishment_id else None

        def update(self, establishment):
            return establishment

    revoked_tokens = []

    async def fake_revoke_token(token):
        revoked_tokens.append(token)

    monkeypatch.setattr(google_calendar_service_module, "EstablishmentRepository", FakeRepository)
    monkeypatch.setattr(GoogleCalendarService, "_revoke_token", staticmethod(fake_revoke_token))

    service = GoogleCalendarService(client_factory=SimpleNamespace())
    result = asyncio.run(service.disconnect_establishment(establishment_id, db=object()))

    assert result["disconnected"] is True
    assert result["revoked"] is True
    assert revoked_tokens == ["refresh-123"]
    assert fake_establishment.google_calendar_access_token is None
    assert fake_establishment.google_calendar_refresh_token is None
    assert fake_establishment.google_calendar_expiry is None
    assert fake_establishment.google_calendar_id is None


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

    async def fake_to_thread(func, *args, **kwargs):
        return func(*args, **kwargs)

    class FakeAdapter:
        def create_event(self, *, calendar_id, payload):
            assert calendar_id == "primary"
            assert payload["summary"] == "Corte - Maria (11999999999)"
            return {"id": "event-123"}

    class FakeFactory:
        def build_adapter(self, *, establishment, db):
            return FakeAdapter()

    monkeypatch.setattr(google_calendar_service_module, "SchedulingRepository", FakeSchedulingRepository)
    monkeypatch.setattr(google_calendar_service_module.asyncio, "to_thread", fake_to_thread)

    service = GoogleCalendarService(client_factory=FakeFactory())
    result = asyncio.run(service.sync_scheduling(scheduling_id, "create", db=object()))

    assert result["status"] == "synced"
    assert result["event_id"] == "event-123"
    assert created_events == ["event-123"]