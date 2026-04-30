from types import SimpleNamespace
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from config.db import get_session
from controller.google_calendar_controller import router, get_google_calendar_service


app = FastAPI()
app.include_router(router)
app.dependency_overrides[get_session] = lambda: SimpleNamespace()


def test_get_authorization_url_returns_payload(monkeypatch):
    establishment_id = uuid4()

    class FakeService:
        def build_authorization_url(self, establishment_uuid):
            return f"https://google.example/auth?state={establishment_uuid}"

    app.dependency_overrides[get_google_calendar_service] = lambda: FakeService()

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

    class FakeService:
        async def connect_establishment(self, establishment_uuid, code, db):
            return fake_establishment

    app.dependency_overrides[get_google_calendar_service] = lambda: FakeService()

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

    class FakeService:
        async def disconnect_establishment(self, establishment_uuid, db):
            return {
                "establishment_id": str(establishment_uuid),
                "disconnected": True,
                "revoked": True,
            }

    app.dependency_overrides[get_google_calendar_service] = lambda: FakeService()

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