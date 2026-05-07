from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from config.db import get_session
from controller import user_controller as user_controller_module
from controller.user_controller import router
from domain.entities import User
from utils.enum import UserRole


def build_user():
    return User(
        id=uuid4(),
        user_name="User Test",
        email="user@example.com",
        phone_number="+5511999990000",
        password_hash="hash",
        role=UserRole.CLIENT,
        active_status=True,
        img_url=None,
        created_at=None,
        updated_at=None,
    )


def build_client(monkeypatch):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_session] = lambda: SimpleNamespace()
    return TestClient(app)


def test_update_user_image_success(monkeypatch):
    user = build_user()

    class FakeRepo:
        def __init__(self, db):
            self.db = db

        def get_by_id(self, user_id):
            return user if str(user_id) == str(user.id) else None

        def update(self, user_to_update):
            return user_to_update

    monkeypatch.setattr(user_controller_module, "UserRepository", FakeRepo)

    client = build_client(monkeypatch)
    response = client.put(f"/users/{user.id}/image", json={"img_url": "https://example.com/img/user.png"})

    assert response.status_code == 200
    assert response.json()["img_url"] == "https://example.com/img/user.png"


def test_update_user_image_returns_404(monkeypatch):
    class FakeRepo:
        def __init__(self, db):
            self.db = db

        def get_by_id(self, user_id):
            return None

        def update(self, user_to_update):
            return user_to_update

    monkeypatch.setattr(user_controller_module, "UserRepository", FakeRepo)

    client = build_client(monkeypatch)
    response = client.put(f"/users/{uuid4()}/image", json={"img_url": "https://example.com/img/user.png"})

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
