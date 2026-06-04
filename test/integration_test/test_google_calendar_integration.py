import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from infra.google_calendar.adapter import GoogleCalendarAdapter
from utils.value_object import GoogleCalendarHelper


REQUIRED_ENV_VARS = (
    "GOOGLE_TEST_CLIENT_ID",
    "GOOGLE_TEST_CLIENT_SECRET",
    "GOOGLE_TEST_REFRESH_TOKEN",
    "GOOGLE_TEST_CALENDAR_ID",
)


def _missing_env_vars():
    return [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]


@pytest.mark.integration
@pytest.mark.skipif(_missing_env_vars(), reason="Missing Google sandbox credentials")
def test_calendar_create_update_delete():
    client_id = os.getenv("GOOGLE_TEST_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_TEST_CLIENT_SECRET")
    refresh_token = os.getenv("GOOGLE_TEST_REFRESH_TOKEN")
    calendar_id = os.getenv("GOOGLE_TEST_CALENDAR_ID")

    credentials = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/calendar.events"],
    )
    credentials.refresh(Request())

    service = build("calendar", "v3", credentials=credentials, cache_discovery=False)
    adapter = GoogleCalendarAdapter(service)

    start = datetime.now(timezone.utc) + timedelta(minutes=10)
    end = start + timedelta(minutes=30)
    unique_tag = f"SessaoCertaTest-{uuid4()}"

    payload = GoogleCalendarHelper.build_event_payload(
        summary=f"{unique_tag} - Criado",
        start=start,
        end=end,
        description="Evento de teste da integracao",
    )

    created = adapter.create_event(calendar_id=calendar_id, payload=payload)
    event_id = created.get("id")
    assert event_id

    try:
        updated_payload = GoogleCalendarHelper.build_event_payload(
            summary=f"{unique_tag} - Atualizado",
            start=start,
            end=end,
            description="Evento de teste atualizado",
        )
        updated = adapter.update_event(
            calendar_id=calendar_id,
            event_id=event_id,
            payload=updated_payload,
        )
        assert updated.get("id") == event_id
    finally:
        adapter.delete_event(calendar_id=calendar_id, event_id=event_id)
