from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from config.db import get_session
from controller import employee_controller as employee_controller_module
from controller.employee_controller import router
from domain.entities import Client, Employee, Establishment, Plan, User
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


def build_employee(establishment: Establishment, *, employee_id: int = 1, user_id=None):
    user = User(
        id=user_id or uuid4(),
        user_name="Employee",
        email="employee@example.com",
        phone_number="11999998888",
        password_hash="hash",
        role=UserRole.EMPLOYEE,
        active_status=True,
        img_url=None,
        created_at=None,
        updated_at=None,
    )
    return Employee(
        id=employee_id,
        user=user,
        establishment=establishment,
        percentage_commission=Decimal("10.0"),
        available_hours=None,
    )


def build_client(monkeypatch, *, user_id=None, role=UserRole.CLIENT):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_session] = lambda: SimpleNamespace()
    resolved_user_id = user_id or uuid4()
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=resolved_user_id, role=role)
    return TestClient(app)


def test_list_employees_success(monkeypatch):
    client_user, client_entity, establishment = build_client_entities()
    employee = build_employee(establishment, employee_id=1)

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

    class FakeEmployeeRepo:
        def __init__(self, db):
            self.db = db

        def list_by_establishment_id(self, establishment_id, cursor=None, limit=15):
            return SimpleNamespace(data=[employee], cursor=None, has_more=False, total_count=None)

    monkeypatch.setattr(employee_controller_module, "ClientRepository", FakeClientRepo)
    monkeypatch.setattr(employee_controller_module, "EstablishmentRepository", FakeEstablishmentRepo)
    monkeypatch.setattr(employee_controller_module, "EmployeeRepository", FakeEmployeeRepo)

    api = build_client(monkeypatch, user_id=client_user.id)
    response = api.get("/employees")

    assert response.status_code == 200
    assert response.json()["data"][0]["id"] == employee.id


def test_get_employee_as_client_success(monkeypatch):
    client_user, client_entity, establishment = build_client_entities()
    employee = build_employee(establishment, employee_id=2)

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

    class FakeEmployeeRepo:
        def __init__(self, db):
            self.db = db

        def get_by_id(self, employee_id):
            return employee if employee_id == employee.id else None

    monkeypatch.setattr(employee_controller_module, "ClientRepository", FakeClientRepo)
    monkeypatch.setattr(employee_controller_module, "EstablishmentRepository", FakeEstablishmentRepo)
    monkeypatch.setattr(employee_controller_module, "EmployeeRepository", FakeEmployeeRepo)

    api = build_client(monkeypatch, user_id=client_user.id)
    response = api.get(f"/employees/{employee.id}")

    assert response.status_code == 200
    assert response.json()["id"] == employee.id


def test_get_employee_as_employee_forbidden(monkeypatch):
    _, _, establishment = build_client_entities()
    employee = build_employee(establishment, employee_id=1)

    class FakeEmployeeRepo:
        def __init__(self, db):
            self.db = db

        def get_by_user_id(self, user_id):
            return employee if str(user_id) == str(employee.user.id) else None

        def get_by_id(self, employee_id):
            return employee if employee_id == employee.id else None

    monkeypatch.setattr(employee_controller_module, "EmployeeRepository", FakeEmployeeRepo)

    api = build_client(monkeypatch, user_id=employee.user.id, role=UserRole.EMPLOYEE)
    response = api.get("/employees/2")

    assert response.status_code == 403
    assert response.json()["detail"] == "Sem permissao para acessar este funcionario"


def test_create_employee_limit_reached(monkeypatch):
    client_user, client_entity, establishment = build_client_entities()

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

    class FakeEmployeeRepo:
        def __init__(self, db):
            self.db = db

        def count_by_establishment_id(self, establishment_id):
            return client_entity.plan.max_employee

    monkeypatch.setattr(employee_controller_module, "ClientRepository", FakeClientRepo)
    monkeypatch.setattr(employee_controller_module, "EstablishmentRepository", FakeEstablishmentRepo)
    monkeypatch.setattr(employee_controller_module, "EmployeeRepository", FakeEmployeeRepo)

    api = build_client(monkeypatch, user_id=client_user.id)
    response = api.post(
        "/employees",
        json={
            "user_name": "Funcionario",
            "email": "funcionario@example.com",
            "phone_number": "+5511999999999",
            "password": "senha123",
            "percentage_commission": 10.0,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Limite de funcionarios atingido"


def test_create_employee_success(monkeypatch):
    client_user, client_entity, establishment = build_client_entities()
    employee = build_employee(establishment, employee_id=3)

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

    class FakeEmployeeRepo:
        def __init__(self, db):
            self.db = db

        def count_by_establishment_id(self, establishment_id):
            return 0

        def create(self, employee_to_create):
            employee_to_create.id = employee.id
            return employee_to_create

    class FakeUserRepo:
        def __init__(self, db):
            self.db = db

        def create(self, user_to_create):
            user_to_create.id = employee.user.id
            return user_to_create

    monkeypatch.setattr(employee_controller_module, "ClientRepository", FakeClientRepo)
    monkeypatch.setattr(employee_controller_module, "EstablishmentRepository", FakeEstablishmentRepo)
    monkeypatch.setattr(employee_controller_module, "EmployeeRepository", FakeEmployeeRepo)
    monkeypatch.setattr(employee_controller_module, "UserRepository", FakeUserRepo)

    api = build_client(monkeypatch, user_id=client_user.id)
    response = api.post(
        "/employees",
        json={
            "user_name": "Funcionario",
            "email": "funcionario@example.com",
            "phone_number": "+5511999999999",
            "password": "senha123",
            "percentage_commission": 10.0,
        },
    )

    assert response.status_code == 201
    assert response.json()["id"] == employee.id


def test_update_employee_as_employee_success(monkeypatch):
    _, _, establishment = build_client_entities()
    employee = build_employee(establishment, employee_id=4)

    class FakeEmployeeRepo:
        def __init__(self, db):
            self.db = db

        def get_by_user_id(self, user_id):
            return employee if str(user_id) == str(employee.user.id) else None

        def get_by_id(self, employee_id):
            return employee if employee_id == employee.id else None

        def update(self, employee_to_update):
            return employee_to_update

    monkeypatch.setattr(employee_controller_module, "EmployeeRepository", FakeEmployeeRepo)

    api = build_client(monkeypatch, user_id=employee.user.id, role=UserRole.EMPLOYEE)
    response = api.put(
        f"/employees/{employee.id}",
        json={"percentage_commission": 15.0},
    )

    assert response.status_code == 200
    assert response.json()["percentage_commission"] == "15.0"


def test_delete_employee_success(monkeypatch):
    client_user, client_entity, establishment = build_client_entities()
    employee = build_employee(establishment, employee_id=5)
    captured = {}

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

    class FakeEmployeeRepo:
        def __init__(self, db):
            self.db = db

        def get_by_id(self, employee_id):
            return employee if employee_id == employee.id else None

        def delete(self, employee_id):
            return True

    class FakeUserRepo:
        def __init__(self, db):
            self.db = db

        def update(self, user_to_update):
            captured["active_status"] = user_to_update.active_status
            return user_to_update

    monkeypatch.setattr(employee_controller_module, "ClientRepository", FakeClientRepo)
    monkeypatch.setattr(employee_controller_module, "EstablishmentRepository", FakeEstablishmentRepo)
    monkeypatch.setattr(employee_controller_module, "EmployeeRepository", FakeEmployeeRepo)
    monkeypatch.setattr(employee_controller_module, "UserRepository", FakeUserRepo)

    api = build_client(monkeypatch, user_id=client_user.id)
    response = api.delete(f"/employees/{employee.id}")

    assert response.status_code == 200
    assert response.json()["deleted_id"] == employee.id
    assert captured["active_status"] is False
