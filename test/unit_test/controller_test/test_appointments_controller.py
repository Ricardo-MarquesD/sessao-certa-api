from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from config.db import get_session
from controller import appointments_controller as appointments_controller_module
from controller.appointments_controller import router
from domain.entities import Client, Customer, Employee, Establishment, Plan, Scheduling, Service, User
from utils.enum import AppointmentStatus
from utils.enum import TypePlan, UserRole


class FakeSchedulingRepository:
    schedules: dict = {}

    def __init__(self, session):
        self.session = session

    @classmethod
    def seed(cls, schedules: dict):
        cls.schedules = schedules

    def create(self, scheduling):
        self.schedules[scheduling.id] = scheduling
        return scheduling

    def update(self, scheduling):
        self.schedules[scheduling.id] = scheduling
        return scheduling

    def get_by_id(self, scheduling_id):
        return self.schedules.get(scheduling_id)

    def list_by_establishment_id(self, establishment_id, cursor=None, limit=15):
        data = [item for item in self.schedules.values() if item.establishment.id == establishment_id]
        return type("Paginated", (), {"data": data, "cursor": None, "has_more": False, "total_count": None})()

    def list_active_by_day_and_scope(self, day, establishment_internal_id, employee_id=None):
        result = []
        for item in self.schedules.values():
            if item.appointment_date.date() != day:
                continue
            if employee_id is not None and item.employee.id != employee_id:
                continue
            if item.appointment_status not in {AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED}:
                continue
            result.append(item)
        return result


def build_scheduling(*, scheduling_id, status=AppointmentStatus.SCHEDULED, event_id="event-1"):
    client = Client(
        id=1,
        user=User(
            id=uuid4(),
            user_name="Cliente",
            email="cliente@example.com",
            phone_number="11999990000",
            password_hash="hash",
            role=UserRole.CLIENT,
            active_status=True,
            img_url=None,
            created_at=None,
            updated_at=None,
        ),
        plan=Plan(
            id=1,
            type_plan=TypePlan.GOLD,
            basic_price=Decimal("99.90"),
            max_employee=10,
            allow_stock=True,
            allow_advanced_analysis=True,
        ),
        stripe_customer_id=None,
    )

    establishment = Establishment(
        id=uuid4(),
        client=client,
        stripe_subscription_id=None,
        waba_id="waba-1",
        whatsapp_business_token="whatsapp-token",
        google_calendar_access_token="google-access-token",
        google_calendar_refresh_token="google-refresh-token",
        google_calendar_expiry=None,
        google_calendar_id="primary",
        establishment_name="Barbearia Central",
        cnpj="12345678901234",
        chatbot_phone_number="5511999990000",
        address="Rua A, 123",
        img_url=None,
        subscription_date=None,
        due_date=None,
        trial_active=True,
        available_hours={"monday": ["09:00", "18:00"]},
    )

    employee = Employee(
        id=7,
        user=User(
            id=uuid4(),
            user_name="Ana",
            email="ana@example.com",
            phone_number="11988880000",
            password_hash="hash",
            role=UserRole.EMPLOYEE,
            active_status=True,
            img_url=None,
            created_at=None,
            updated_at=None,
        ),
        establishment=establishment,
        percentage_commission=Decimal("10.00"),
        available_hours=establishment.available_hours,
    )

    customer = Customer(
        id=uuid4(),
        establishment=establishment,
        customer_name="João",
        phone_number="11977770000",
        wa_id=None,
    )

    service = Service(
        id=uuid4(),
        establishment=establishment,
        service_name="Corte",
        time_duration=30,
        price=Decimal("50.00"),
        description_service="Serviço de teste",
        active=True,
    )

    appointment_date = datetime(2026, 4, 1, 10, 0, 0)
    return Scheduling(
        id=scheduling_id,
        establishment=establishment,
        employee=employee,
        customer=customer,
        service=service,
        appointment_status=status,
        appointment_date=appointment_date,
        notification_sent=False,
        created_at=appointment_date,
        google_calendar_event_id=event_id,
    )


def build_client_app(monkeypatch):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_session] = lambda: SimpleNamespace()

    monkeypatch.setattr(appointments_controller_module, "AppointmentsService", FakeAppointmentsService)

    return TestClient(app)


class FakeAppointmentsService:
    create_result = None
    update_result = None
    delete_result = None
    list_result = []
    get_result = None
    create_exception = None
    update_exception = None
    delete_exception = None
    get_exception = None
    list_exception = None

    @classmethod
    def reset(cls):
        cls.create_result = build_scheduling(scheduling_id=uuid4())
        cls.update_result = build_scheduling(scheduling_id=uuid4())
        cls.delete_result = build_scheduling(scheduling_id=uuid4(), status=AppointmentStatus.CANCELED)
        cls.get_result = build_scheduling(scheduling_id=uuid4())
        cls.list_result = [cls.get_result]
        cls.create_exception = None
        cls.update_exception = None
        cls.delete_exception = None
        cls.get_exception = None
        cls.list_exception = None

    @classmethod
    def list_appointments(cls, **kwargs):
        if cls.list_exception:
            raise cls.list_exception
        return cls.list_result

    @classmethod
    def get_appointment(cls, **kwargs):
        if cls.get_exception:
            raise cls.get_exception
        return cls.get_result

    @classmethod
    def create_appointment(cls, **kwargs):
        if cls.create_exception:
            raise cls.create_exception
        return cls.create_result

    @classmethod
    def update_appointment(cls, **kwargs):
        if cls.update_exception:
            raise cls.update_exception
        return cls.update_result

    @classmethod
    def delete_appointment(cls, **kwargs):
        if cls.delete_exception:
            raise cls.delete_exception
        return cls.delete_result


def seed_stores():
    FakeAppointmentsService.reset()


def test_create_appointment_enqueues_calendar_sync(monkeypatch):
    seed_stores()
    client = build_client_app(monkeypatch)
    payload = {"establishment_id": str(uuid4()), "employee_id": 7, "customer_id": str(uuid4()), "service_id": str(uuid4()), "appointment_date": "2026-04-01T10:00:00"}

    response = client.post("/appointments", json=payload)

    assert response.status_code == 201
    assert response.json()["appointment_status"] == "SCHEDULED"


def test_create_appointment_returns_404_on_service_error(monkeypatch):
    seed_stores()
    FakeAppointmentsService.create_exception = ValueError("Establishment not found")

    client = build_client_app(monkeypatch)
    response = client.post("/appointments", json={"establishment_id": str(uuid4()), "employee_id": 7, "customer_id": str(uuid4()), "service_id": str(uuid4()), "appointment_date": "2026-04-01T10:00:00"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Establishment not found"


def test_update_appointment_enqueues_calendar_update(monkeypatch):
    seed_stores()
    client = build_client_app(monkeypatch)
    existing_id = str(uuid4())
    response = client.put(f"/appointments/{existing_id}", json={"appointment_date": "2026-04-01T11:00:00", "service_id": str(uuid4())})

    assert response.status_code == 200
    assert response.json()["appointment_status"] == "SCHEDULED"


def test_delete_appointment_returns_cancelled(monkeypatch):
    seed_stores()
    client = build_client_app(monkeypatch)
    existing_id = str(uuid4())
    response = client.delete(f"/appointments/{existing_id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Agendamento cancelado com sucesso"
    assert response.json()["success"] is True