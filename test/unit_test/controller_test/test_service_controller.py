from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from config.db import get_session
from controller import service_controller as service_controller_module
from controller.service_controller import router
from domain.entities import Client, Establishment, Plan, Service, User
from middleware.auth import get_current_user
from utils.enum import TypePlan, UserRole


def build_client_entities():
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
        max_employee=2,
        allow_stock=True,
        allow_advanced_analysis=True,
    )
    client = Client(
        id=1,
        user=user,
        plan=plan,
        stripe_customer_id=None,
    )
    establishment = Establishment(
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
    return user, client, establishment


def build_service(establishment: Establishment, *, service_id=None):
    return Service(
        id=service_id or uuid4(),
        establishment=establishment,
        service_name="Corte",
        time_duration=30,
        price=Decimal("50.00"),
        description_service="Descricao",
        active=True,
    )


def build_client(monkeypatch, *, user_id=None, role=UserRole.CLIENT):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_session] = lambda: SimpleNamespace()
    resolved_user_id = user_id or uuid4()
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=resolved_user_id, role=role)
    return TestClient(app)


def test_list_services_success(monkeypatch):
    client_user, client_entity, establishment = build_client_entities()
    service = build_service(establishment)

    class FakeClientRepo:
        def __init__(self, db):
            self.db = db

        def get_by_user_id(self, user_id):
            return client_entity if str(user_id) == str(client_user.id) else None

    class FakeEstablishmentRepo:
        def __init__(self, db):
            self.db = db

        def get_by_client_id(self, client_id):
            return establishment if client_id == client_entity.id else None

    class FakeServiceRepo:
        def __init__(self, db):
            self.db = db

        def list_by_establishment_id(self, establishment_id, cursor=None, limit=15):
            return SimpleNamespace(data=[service], cursor=None, has_more=False, total_count=None)

    monkeypatch.setattr(service_controller_module, "ClientRepository", FakeClientRepo)
    monkeypatch.setattr(service_controller_module, "EstablishmentRepository", FakeEstablishmentRepo)
    monkeypatch.setattr(service_controller_module, "ServiceRepository", FakeServiceRepo)

    api = build_client(monkeypatch, user_id=client_user.id)
    response = api.get(f"/services?establishment_id={establishment.id}")

    assert response.status_code == 200
    assert response.json()["data"][0]["id"] == str(service.id)


def test_list_services_active_query(monkeypatch):
    client_user, client_entity, establishment = build_client_entities()
    service = build_service(establishment)
    calls = {"active": None}

    class FakeClientRepo:
        def __init__(self, db):
            self.db = db

        def get_by_user_id(self, user_id):
            return client_entity if str(user_id) == str(client_user.id) else None

    class FakeEstablishmentRepo:
        def __init__(self, db):
            self.db = db

        def get_by_client_id(self, client_id):
            return establishment if client_id == client_entity.id else None

    class FakeServiceRepo:
        def __init__(self, db):
            self.db = db

        def list_by_establishment_id(self, establishment_id, cursor=None, limit=15):
            return SimpleNamespace(data=[], cursor=None, has_more=False, total_count=None)

        def list_active_by_establishment_id(self, active, establishment_id, cursor=None, limit=15):
            calls["active"] = active
            return SimpleNamespace(data=[service], cursor=None, has_more=False, total_count=None)

    monkeypatch.setattr(service_controller_module, "ClientRepository", FakeClientRepo)
    monkeypatch.setattr(service_controller_module, "EstablishmentRepository", FakeEstablishmentRepo)
    monkeypatch.setattr(service_controller_module, "ServiceRepository", FakeServiceRepo)

    api = build_client(monkeypatch, user_id=client_user.id)
    response = api.get(f"/services?establishment_id={establishment.id}&active=true")

    assert response.status_code == 200
    assert calls["active"] is True
    assert response.json()["data"][0]["id"] == str(service.id)


def test_create_service_success(monkeypatch):
    client_user, client_entity, establishment = build_client_entities()
    service = build_service(establishment)

    class FakeClientRepo:
        def __init__(self, db):
            self.db = db

        def get_by_user_id(self, user_id):
            return client_entity if str(user_id) == str(client_user.id) else None

    class FakeEstablishmentRepo:
        def __init__(self, db):
            self.db = db

        def get_by_client_id(self, client_id):
            return establishment if client_id == client_entity.id else None

    class FakeServiceRepo:
        def __init__(self, db):
            self.db = db

        def create(self, service_to_create):
            service_to_create.id = service.id
            return service_to_create

    monkeypatch.setattr(service_controller_module, "ClientRepository", FakeClientRepo)
    monkeypatch.setattr(service_controller_module, "EstablishmentRepository", FakeEstablishmentRepo)
    monkeypatch.setattr(service_controller_module, "ServiceRepository", FakeServiceRepo)

    api = build_client(monkeypatch, user_id=client_user.id)
    response = api.post(
        f"/services?establishment_id={establishment.id}",
        json={
            "service_name": "Corte",
            "description_service": "Descricao",
            "time_duration": 30,
            "price": 50.0,
            "active": True,
        },
    )

    assert response.status_code == 201
    assert response.json()["id"] == str(service.id)


def test_update_service_success(monkeypatch):
    client_user, client_entity, establishment = build_client_entities()
    service = build_service(establishment)

    class FakeClientRepo:
        def __init__(self, db):
            self.db = db

        def get_by_user_id(self, user_id):
            return client_entity if str(user_id) == str(client_user.id) else None

    class FakeEstablishmentRepo:
        def __init__(self, db):
            self.db = db

        def get_by_client_id(self, client_id):
            return establishment if client_id == client_entity.id else None

    class FakeServiceRepo:
        def __init__(self, db):
            self.db = db

        def get_by_id(self, service_id):
            return service if str(service_id) == str(service.id) else None

        def update(self, service_to_update):
            return service_to_update

    monkeypatch.setattr(service_controller_module, "ClientRepository", FakeClientRepo)
    monkeypatch.setattr(service_controller_module, "EstablishmentRepository", FakeEstablishmentRepo)
    monkeypatch.setattr(service_controller_module, "ServiceRepository", FakeServiceRepo)

    api = build_client(monkeypatch, user_id=client_user.id)
    response = api.put(
        f"/services/{service.id}",
        json={"price": 60.0},
    )

    assert response.status_code == 200
    assert response.json()["price"] == "60.0"


def test_delete_service_success(monkeypatch):
    client_user, client_entity, establishment = build_client_entities()
    service = build_service(establishment)

    class FakeClientRepo:
        def __init__(self, db):
            self.db = db

        def get_by_user_id(self, user_id):
            return client_entity if str(user_id) == str(client_user.id) else None

    class FakeEstablishmentRepo:
        def __init__(self, db):
            self.db = db

        def get_by_client_id(self, client_id):
            return establishment if client_id == client_entity.id else None

    class FakeServiceRepo:
        def __init__(self, db):
            self.db = db

        def get_by_id(self, service_id):
            return service if str(service_id) == str(service.id) else None

        def delete(self, service_id):
            return True

    monkeypatch.setattr(service_controller_module, "ClientRepository", FakeClientRepo)
    monkeypatch.setattr(service_controller_module, "EstablishmentRepository", FakeEstablishmentRepo)
    monkeypatch.setattr(service_controller_module, "ServiceRepository", FakeServiceRepo)

    api = build_client(monkeypatch, user_id=client_user.id)
    response = api.delete(f"/services/{service.id}")

    assert response.status_code == 200
    assert response.json()["deleted_id"] == str(service.id)
