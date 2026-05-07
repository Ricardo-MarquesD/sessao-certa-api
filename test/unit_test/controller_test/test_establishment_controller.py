from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from config.db import get_session
from controller import establishment_controller as establishment_controller_module
from controller.establishment_controller import router
from domain.entities import Client, Establishment, Plan, User
from utils.enum import TypePlan, UserRole


def build_establishment():
    user = User(
        id=uuid4(),
        user_name="Client",
        email="client@example.com",
        phone_number="11999990000",
        password_hash="hash",
        role=UserRole.CLIENT,
        active_status=True,
        img_url=None,
        created_at=None,
        updated_at=None,
    )
    plan = Plan(
        id=1,
        type_plan=TypePlan.GOLD,
        basic_price=Decimal("99.90"),
        max_employee=10,
        allow_stock=True,
        allow_advanced_analysis=True,
    )
    client = Client(
        id=1,
        user=user,
        plan=plan,
        stripe_customer_id=None,
    )
    return Establishment(
        id=uuid4(),
        client=client,
        stripe_subscription_id=None,
        waba_id=None,
        whatsapp_business_token=None,
        google_calendar_access_token=None,
        google_calendar_refresh_token=None,
        google_calendar_expiry=None,
        google_calendar_id=None,
        establishment_name="Barbearia Central",
        cnpj="12345678901234",
        chatbot_phone_number=None,
        address="Rua A",
        img_url=None,
        subscription_date=None,
        due_date=None,
        trial_active=True,
        available_hours=None,
    )


def build_client(monkeypatch):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_session] = lambda: SimpleNamespace()
    return TestClient(app)


def test_update_establishment_image_success(monkeypatch):
    establishment = build_establishment()

    class FakeRepo:
        def __init__(self, db):
            self.db = db

        def get_by_id(self, establishment_id):
            return establishment if str(establishment_id) == str(establishment.id) else None

        def update(self, establishment_to_update):
            return establishment_to_update

    monkeypatch.setattr(establishment_controller_module, "EstablishmentRepository", FakeRepo)

    client = build_client(monkeypatch)
    response = client.put(
        f"/establishments/{establishment.id}/image",
        json={"img_url": "https://example.com/img/est.png"},
    )

    assert response.status_code == 200
    assert response.json()["img_url"] == "https://example.com/img/est.png"


def test_update_establishment_image_returns_404(monkeypatch):
    class FakeRepo:
        def __init__(self, db):
            self.db = db

        def get_by_id(self, establishment_id):
            return None

        def update(self, establishment_to_update):
            return establishment_to_update

    monkeypatch.setattr(establishment_controller_module, "EstablishmentRepository", FakeRepo)

    client = build_client(monkeypatch)
    response = client.put(
        f"/establishments/{uuid4()}/image",
        json={"img_url": "https://example.com/img/est.png"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Establishment not found"
