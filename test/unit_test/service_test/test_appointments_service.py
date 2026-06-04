from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from domain.entities import Client, Customer, Employee, Establishment, Plan, Scheduling, Service, User
from domain.service.appointments_service import AppointmentsService
from utils.enum import AppointmentStatus, TypePlan, UserRole


class FakeTaskQueueRepository:
    created_tasks: list = []

    def __init__(self, session):
        self.session = session

    def create(self, task):
        self.created_tasks.append(task)
        return task


class FakeEstablishmentRepository:
    establishment = None
    internal_id = 77

    def __init__(self, session):
        self.session = session

    def get_by_id(self, establishment_id):
        return self.establishment if self.establishment and self.establishment.id == establishment_id else None

    def get_internal_id_by_id(self, establishment_id):
        return self.internal_id if self.establishment and self.establishment.id == establishment_id else None


class FakeEmployeeRepository:
    employee = None

    def __init__(self, session):
        self.session = session

    def get_by_id(self, employee_id):
        return self.employee if self.employee and self.employee.id == employee_id else None


class FakeCustomerRepository:
    customer = None

    def __init__(self, session):
        self.session = session

    def get_by_id(self, customer_id):
        return self.customer if self.customer and self.customer.id == customer_id else None


class FakeServiceRepository:
    service = None

    def __init__(self, session):
        self.session = session

    def get_by_id(self, service_id):
        return self.service if self.service and self.service.id == service_id else None


class FakeSchedulingRepository:
    store: dict = {}

    def __init__(self, session):
        self.session = session

    @classmethod
    def reset(cls):
        cls.store = {}

    def create(self, scheduling):
        self.store[scheduling.id] = scheduling
        return scheduling

    def update(self, scheduling):
        self.store[scheduling.id] = scheduling
        return scheduling

    def get_by_id(self, scheduling_id):
        return self.store.get(scheduling_id)

    def list_by_establishment_id(self, establishment_id, cursor=None, limit=15):
        data = [item for item in self.store.values() if item.establishment.id == establishment_id]
        return SimpleNamespace(data=data, cursor=None, has_more=False, total_count=None)

    def list_active_by_day_and_scope(self, day, establishment_internal_id, employee_id=None):
        return [
            item
            for item in self.store.values()
            if item.appointment_date.date() == day
            and (employee_id is None or item.employee.id == employee_id)
            and item.appointment_status in {AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED}
        ]


def build_user(*, user_name: str, email: str, phone_number: str, role: UserRole):
    return User(
        id=uuid4(),
        user_name=user_name,
        email=email,
        phone_number=phone_number,
        password_hash="hash",
        role=role,
        active_status=True,
        img_url=None,
        created_at=None,
        updated_at=None,
    )


def build_establishment():
    client = Client(
        id=1,
        user=build_user(user_name="Cliente", email="cliente@example.com", phone_number="11999990000", role=UserRole.CLIENT),
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

    return Establishment(
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


def build_employee(establishment: Establishment):
    return Employee(
        id=7,
        user=build_user(user_name="Ana", email="ana@example.com", phone_number="11988880000", role=UserRole.EMPLOYEE),
        establishment=establishment,
        percentage_commission=Decimal("10.00"),
        available_hours=establishment.available_hours,
    )


def build_customer(establishment: Establishment):
    return Customer(
        id=uuid4(),
        establishment=establishment,
        customer_name="João",
        phone_number="11977770000",
        wa_id=None,
    )


def build_service(establishment: Establishment, *, service_name: str = "Corte", time_duration: int = 30):
    return Service(
        id=uuid4(),
        establishment=establishment,
        service_name=service_name,
        time_duration=time_duration,
        price=Decimal("50.00"),
        description_service="Serviço de teste",
        active=True,
    )


def build_scheduling(*, scheduling_id, establishment, employee, customer, service, appointment_date, status=AppointmentStatus.SCHEDULED, event_id="event-1"):
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


def seed_repositories(monkeypatch):
    establishment = build_establishment()
    employee = build_employee(establishment)
    customer = build_customer(establishment)
    service = build_service(establishment)

    FakeEstablishmentRepository.establishment = establishment
    FakeEmployeeRepository.employee = employee
    FakeCustomerRepository.customer = customer
    FakeServiceRepository.service = service
    FakeSchedulingRepository.reset()
    FakeTaskQueueRepository.created_tasks = []

    monkeypatch.setattr("domain.service.appointments_service.EstablishmentRepository", FakeEstablishmentRepository)
    monkeypatch.setattr("domain.service.appointments_service.EmployeeRepository", FakeEmployeeRepository)
    monkeypatch.setattr("domain.service.appointments_service.CustomerRepository", FakeCustomerRepository)
    monkeypatch.setattr("domain.service.appointments_service.ServiceRepository", FakeServiceRepository)
    monkeypatch.setattr("domain.service.appointments_service.SchedulingRepository", FakeSchedulingRepository)
    monkeypatch.setattr("domain.service.appointments_service.TaskQueueRepository", FakeTaskQueueRepository)

    db = SimpleNamespace()
    return db, establishment, employee, customer, service


def test_create_appointment_enqueues_sync(monkeypatch):
    db, establishment, employee, customer, service = seed_repositories(monkeypatch)

    payload = SimpleNamespace(
        establishment_id=establishment.id,
        employee_id=employee.id,
        customer_id=customer.id,
        service_id=service.id,
        appointment_date=datetime(2026, 4, 1, 10, 0, 0),
    )

    result = AppointmentsService.create_appointment(db=db, payload=payload)

    assert result.appointment_status == AppointmentStatus.SCHEDULED
    assert len(FakeTaskQueueRepository.created_tasks) == 1
    assert FakeTaskQueueRepository.created_tasks[0].payload["action"] == "create"


def test_update_appointment_enqueues_sync(monkeypatch):
    db, establishment, employee, customer, service = seed_repositories(monkeypatch)
    original = build_scheduling(
        scheduling_id=uuid4(),
        establishment=establishment,
        employee=employee,
        customer=customer,
        service=service,
        appointment_date=datetime(2026, 4, 1, 10, 0, 0),
    )
    FakeSchedulingRepository.store[original.id] = original

    payload = SimpleNamespace(
        appointment_date=datetime(2026, 4, 1, 11, 0, 0),
        employee_id=None,
        service_id=None,
    )

    result = AppointmentsService.update_appointment(db=db, scheduling_id=original.id, payload=payload)

    assert result.appointment_date == datetime(2026, 4, 1, 11, 0, 0)
    assert len(FakeTaskQueueRepository.created_tasks) == 1
    assert FakeTaskQueueRepository.created_tasks[0].payload["action"] == "update"


def test_delete_appointment_enqueues_sync(monkeypatch):
    db, establishment, employee, customer, service = seed_repositories(monkeypatch)
    original = build_scheduling(
        scheduling_id=uuid4(),
        establishment=establishment,
        employee=employee,
        customer=customer,
        service=service,
        appointment_date=datetime(2026, 4, 1, 10, 0, 0),
    )
    FakeSchedulingRepository.store[original.id] = original

    result = AppointmentsService.delete_appointment(db=db, scheduling_id=original.id)

    assert result.appointment_status == AppointmentStatus.CANCELED
    assert len(FakeTaskQueueRepository.created_tasks) == 1
    assert FakeTaskQueueRepository.created_tasks[0].payload["action"] == "cancel"