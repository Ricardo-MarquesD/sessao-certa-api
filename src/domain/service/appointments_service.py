from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from domain.entities import Scheduling
from infra.repository import (
    CustomerRepository,
    EmployeeRepository,
    EstablishmentRepository,
    SchedulingRepository,
    ServiceRepository,
    TaskQueueRepository,
)
from middleware.task_queue import TaskQueueFactory
from utils.enum import AppointmentStatus
from utils.value_object import SchedulingHelper


class AppointmentsService:
    @staticmethod
    def _ensure_establishment(db: Session, establishment_id: UUID):
        repository = EstablishmentRepository(db)
        establishment = repository.get_by_id(establishment_id)

        if establishment is None:
            raise ValueError("Establishment not found")

        return establishment, repository

    @staticmethod
    def _ensure_same_establishment(entity, establishment_id: UUID, entity_name: str):
        entity_establishment = getattr(entity, "establishment", None)
        entity_establishment_id = getattr(entity_establishment, "id", None)

        if str(entity_establishment_id) != str(establishment_id):
            raise ValueError(f"{entity_name} not found for establishment")

    @staticmethod
    def _ensure_employee(db: Session, employee_id: int, establishment_id: UUID):
        repository = EmployeeRepository(db)
        employee = repository.get_by_id(employee_id)

        if employee is None:
            raise ValueError("Employee not found")

        AppointmentsService._ensure_same_establishment(employee, establishment_id, "Employee")
        return employee

    @staticmethod
    def _ensure_customer(db: Session, customer_id: UUID, establishment_id: UUID):
        repository = CustomerRepository(db)
        customer = repository.get_by_id(customer_id)

        if customer is None:
            raise ValueError("Customer not found")

        AppointmentsService._ensure_same_establishment(customer, establishment_id, "Customer")
        return customer

    @staticmethod
    def _ensure_service(db: Session, service_id: UUID, establishment_id: UUID):
        repository = ServiceRepository(db)
        service = repository.get_by_id(service_id)

        if service is None:
            raise ValueError("Service not found")

        AppointmentsService._ensure_same_establishment(service, establishment_id, "Service")
        return service

    @staticmethod
    def _build_scheduling(
        *,
        scheduling_id: UUID,
        establishment,
        employee,
        customer,
        service,
        appointment_date: datetime,
        appointment_status: AppointmentStatus,
        google_calendar_event_id: str | None = None,
    ) -> Scheduling:
        return Scheduling(
            id=scheduling_id,
            establishment=establishment,
            employee=employee,
            customer=customer,
            service=service,
            appointment_status=appointment_status,
            appointment_date=appointment_date,
            notification_sent=False,
            created_at=None,
            google_calendar_event_id=google_calendar_event_id,
        )

    @staticmethod
    def _ensure_no_conflict(
        *,
        scheduling_repository: SchedulingRepository,
        establishment_internal_id: int,
        appointment_date: datetime,
        employee_id: int,
        service,
        ignore_scheduling_id: UUID | None = None,
    ):
        same_day_appointments = scheduling_repository.list_active_by_day_and_scope(
            day=appointment_date.date(),
            establishment_internal_id=establishment_internal_id,
            employee_id=employee_id,
        )

        if ignore_scheduling_id is not None:
            same_day_appointments = [appt for appt in same_day_appointments if appt.id != ignore_scheduling_id]

        appointment_end = service.calculate_end_time(appointment_date)
        if SchedulingHelper.has_conflict_interval(
            start_dt=appointment_date,
            end_dt=appointment_end,
            appointments=same_day_appointments,
        ):
            raise ValueError("Conflito de horário")

    @staticmethod
    def _enqueue_calendar_sync(*, db: Session, establishment, scheduling_id: UUID, action: str):
        establishment_repository = EstablishmentRepository(db)
        establishment_internal_id = establishment_repository.get_internal_id_by_id(establishment.id)

        if establishment_internal_id is None:
            return

        if not establishment.google_calendar_access_token and not establishment.google_calendar_refresh_token:
            return

        task = TaskQueueFactory.sync_calendar(
            establishments_id=establishment_internal_id,
            scheduling_id=str(scheduling_id),
            action=action,
        )
        TaskQueueRepository(db).create(task)

    @staticmethod
    def list_appointments(*, db: Session, establishment_id: UUID, cursor: str | None = None, limit: int = 15):
        AppointmentsService._ensure_establishment(db, establishment_id)
        repository = SchedulingRepository(db)
        paginated = repository.list_by_establishment_id(establishment_id, cursor=cursor, limit=limit)
        return paginated.data

    @staticmethod
    def get_appointment(*, db: Session, scheduling_id: UUID):
        repository = SchedulingRepository(db)
        scheduling = repository.get_by_id(scheduling_id)

        if scheduling is None:
            raise ValueError("Scheduling not found")

        return scheduling

    @staticmethod
    def create_appointment(*, db: Session, payload) -> Scheduling:
        establishment, _ = AppointmentsService._ensure_establishment(db, payload.establishment_id)
        employee = AppointmentsService._ensure_employee(db, payload.employee_id, payload.establishment_id)
        customer = AppointmentsService._ensure_customer(db, payload.customer_id, payload.establishment_id)
        service = AppointmentsService._ensure_service(db, payload.service_id, payload.establishment_id)

        establishment_repository = EstablishmentRepository(db)
        establishment_internal_id = establishment_repository.get_internal_id_by_id(establishment.id)

        if establishment_internal_id is None:
            raise ValueError("Establishment not found")

        repository = SchedulingRepository(db)
        AppointmentsService._ensure_no_conflict(
            scheduling_repository=repository,
            establishment_internal_id=establishment_internal_id,
            appointment_date=payload.appointment_date,
            employee_id=employee.id,
            service=service,
        )

        scheduling = AppointmentsService._build_scheduling(
            scheduling_id=uuid4(),
            establishment=establishment,
            employee=employee,
            customer=customer,
            service=service,
            appointment_date=payload.appointment_date,
            appointment_status=AppointmentStatus.SCHEDULED,
        )

        created = repository.create(scheduling)
        AppointmentsService._enqueue_calendar_sync(db=db, establishment=establishment, scheduling_id=created.id, action="create")
        return created

    @staticmethod
    def update_appointment(*, db: Session, scheduling_id: UUID, payload) -> Scheduling:
        repository = SchedulingRepository(db)
        existing = repository.get_by_id(scheduling_id)

        if existing is None:
            raise ValueError("Scheduling not found")

        establishment = existing.establishment
        employee = existing.employee
        service = existing.service
        appointment_date = existing.appointment_date

        if payload.employee_id is not None:
            employee = AppointmentsService._ensure_employee(db, payload.employee_id, establishment.id)

        if payload.service_id is not None:
            service = AppointmentsService._ensure_service(db, payload.service_id, establishment.id)

        if payload.appointment_date is not None:
            appointment_date = payload.appointment_date

        if appointment_date is None:
            raise ValueError("Appointment date is required")

        establishment_repository = EstablishmentRepository(db)
        establishment_internal_id = establishment_repository.get_internal_id_by_id(establishment.id)

        if establishment_internal_id is None:
            raise ValueError("Establishment not found")

        AppointmentsService._ensure_no_conflict(
            scheduling_repository=repository,
            establishment_internal_id=establishment_internal_id,
            appointment_date=appointment_date,
            employee_id=employee.id,
            service=service,
            ignore_scheduling_id=existing.id,
        )

        updated = AppointmentsService._build_scheduling(
            scheduling_id=existing.id,
            establishment=establishment,
            employee=employee,
            customer=existing.customer,
            service=service,
            appointment_date=appointment_date,
            appointment_status=existing.appointment_status,
            google_calendar_event_id=existing.google_calendar_event_id,
        )

        saved = repository.update(updated)

        if payload.appointment_date is not None or payload.employee_id is not None or payload.service_id is not None:
            AppointmentsService._enqueue_calendar_sync(db=db, establishment=establishment, scheduling_id=saved.id, action="update")

        return saved

    @staticmethod
    def delete_appointment(*, db: Session, scheduling_id: UUID) -> Scheduling:
        repository = SchedulingRepository(db)
        scheduling = repository.get_by_id(scheduling_id)

        if scheduling is None:
            raise ValueError("Scheduling not found")

        scheduling.appointment_status = AppointmentStatus.CANCELED
        saved = repository.update(scheduling)
        AppointmentsService._enqueue_calendar_sync(db=db, establishment=saved.establishment, scheduling_id=saved.id, action="cancel")
        return saved