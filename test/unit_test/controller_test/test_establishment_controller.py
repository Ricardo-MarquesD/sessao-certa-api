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
from middleware.auth import get_current_user
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


def build_client(monkeypatch, *, user_id=None, role=UserRole.CLIENT):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_session] = lambda: SimpleNamespace()
    resolved_user_id = user_id or uuid4()
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=resolved_user_id, role=role)
    return TestClient(app)


def test_get_establishment_success(monkeypatch):
    establishment = build_establishment()

    class FakeClientRepo:
        def __init__(self, db):
            self.db = db

        def get_by_user_id(self, user_id):
            return establishment.client if str(user_id) == str(establishment.client.user.id) else None

    class FakeEstablishmentRepo:
        def __init__(self, db):
            self.db = db

        def get_by_client_id(self, client_id):
            return establishment if client_id == establishment.client.id else None

    monkeypatch.setattr(establishment_controller_module, "ClientRepository", FakeClientRepo)
    monkeypatch.setattr(establishment_controller_module, "EstablishmentRepository", FakeEstablishmentRepo)

    client = build_client(monkeypatch, user_id=establishment.client.user.id)
    response = client.get("/establishments")

    assert response.status_code == 200
    assert response.json()["id"] == str(establishment.id)


def test_get_establishment_returns_404_when_not_found(monkeypatch):
    establishment = build_establishment()

    class FakeClientRepo:
        def __init__(self, db):
            self.db = db

        def get_by_user_id(self, user_id):
            return establishment.client if str(user_id) == str(establishment.client.user.id) else None

    class FakeEstablishmentRepo:
        def __init__(self, db):
            self.db = db

        def get_by_client_id(self, client_id):
            return None

    monkeypatch.setattr(establishment_controller_module, "ClientRepository", FakeClientRepo)
    monkeypatch.setattr(establishment_controller_module, "EstablishmentRepository", FakeEstablishmentRepo)

    client = build_client(monkeypatch, user_id=establishment.client.user.id)
    response = client.get("/establishments")

    assert response.status_code == 404
    assert response.json()["detail"] == "Establishment not found"


def test_update_establishment_success(monkeypatch):
    establishment = build_establishment()

    class FakeClientRepo:
        def __init__(self, db):
            self.db = db

        def get_by_user_id(self, user_id):
            return establishment.client if str(user_id) == str(establishment.client.user.id) else None

    class FakeEstablishmentRepo:
        def __init__(self, db):
            self.db = db

        def get_by_client_id(self, client_id):
            return establishment if client_id == establishment.client.id else None

        def update(self, establishment_to_update):
            return establishment_to_update

    monkeypatch.setattr(establishment_controller_module, "ClientRepository", FakeClientRepo)
    monkeypatch.setattr(establishment_controller_module, "EstablishmentRepository", FakeEstablishmentRepo)

    client = build_client(monkeypatch, user_id=establishment.client.user.id)
    response = client.put(
        "/establishments",
        json={"establishment_name": "Nova Barbearia", "address": "Rua B"},
    )

    assert response.status_code == 200
    assert response.json()["establishment_name"] == "Nova Barbearia"
    assert response.json()["address"] == "Rua B"


def test_update_establishment_rejects_subscription_fields(monkeypatch):
    establishment = build_establishment()
    client = build_client(monkeypatch, user_id=establishment.client.user.id)
    response = client.put(
        "/establishments",
        json={"trial_active": False},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Sem permissao para alterar dados de assinatura"


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

    client = build_client(monkeypatch, user_id=establishment.client.user.id)
    response = client.put(
        f"/establishments/{establishment.id}/image",
        json={"img_url": "https://example.com/img/est.png"},
    )

    assert response.status_code == 200
    assert response.json()["img_url"] == "https://example.com/img/est.png"


def test_update_establishment_image_returns_403_for_other_user(monkeypatch):
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

    assert response.status_code == 403
    assert response.json()["detail"] == "Sem permissao para alterar este estabelecimento"


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
