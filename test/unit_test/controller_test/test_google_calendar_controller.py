from types import SimpleNamespace
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from config.db import get_session
from controller.google_calendar_controller import router
from controller import google_calendar_controller as google_calendar_controller_module


app = FastAPI()
app.include_router(router)
app.dependency_overrides[get_session] = lambda: SimpleNamespace()


def test_get_authorization_url_returns_payload(monkeypatch):
    establishment_id = uuid4()
    monkeypatch.setattr(
        google_calendar_controller_module.GoogleCalendarService,
        "build_authorization_url",
        staticmethod(lambda establishment_uuid: f"https://google.example/auth?state={establishment_uuid}"),
    )

    client = TestClient(app)
    response = client.get(f"/google-calendar/connect/{establishment_id}")

    assert response.status_code == 200
    assert response.json()["authorization_url"].endswith(str(establishment_id))


def test_callback_returns_connected(monkeypatch):
    establishment_id = uuid4()

    fake_establishment = SimpleNamespace(
        id=establishment_id,
        google_calendar_id="primary",
    )

    async def fake_connect_establishment(establishment_uuid, code, db):
        return fake_establishment

    monkeypatch.setattr(
        google_calendar_controller_module.GoogleCalendarService,
        "connect_establishment",
        staticmethod(fake_connect_establishment),
    )

    client = TestClient(app)
    response = client.get(f"/google-calendar/callback?code=code-123&state={establishment_id}")

    assert response.status_code == 200
    assert response.json() == {
        "status": "connected",
        "establishment_id": str(establishment_id),
        "google_calendar_id": "primary",
    }


def test_disconnect_returns_disconnected(monkeypatch):
    establishment_id = uuid4()

    async def fake_disconnect_establishment(establishment_uuid, db):
        return {
            "establishment_id": str(establishment_uuid),
            "disconnected": True,
            "revoked": True,
        }

    monkeypatch.setattr(
        google_calendar_controller_module.GoogleCalendarService,
        "disconnect_establishment",
        staticmethod(fake_disconnect_establishment),
    )

    client = TestClient(app)
    response = client.delete(f"/google-calendar/disconnect/{establishment_id}")

    assert response.status_code == 200
    assert response.json() == {
        "status": "disconnected",
        "result": {
            "establishment_id": str(establishment_id),
            "disconnected": True,
            "revoked": True,
        },
    }