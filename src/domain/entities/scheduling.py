from __future__ import annotations
from dataclasses import dataclass
from .establishment import Establishment
from .employee import Employee
from .customer import Customer
from .service import Service
from datetime import datetime
from utils.enum import AppointmentStatus
from typing import Any
from uuid import UUID

@dataclass
class Scheduling():
    id: UUID | None
    establishment: Establishment
    employee: Employee
    customer: Customer
    service: Service
    appointment_status: AppointmentStatus
    appointment_date: datetime | None
    notification_sent: bool | None
    created_at: datetime | None
    google_calendar_event_id: str | None = None

    def __post_init__(self):
        if not isinstance(self.establishment, Establishment):
            raise ValueError("Establishment must be an Establishment instance")
        if not isinstance(self.employee, Employee):
            raise ValueError("Employee must be an Employee instance")
        if not isinstance(self.customer, Customer):
            raise ValueError("Customer must be a Customer instance")
        if not isinstance(self.service, Service):
            raise ValueError("Service must be a Service instance")
        if not isinstance(self.appointment_status, AppointmentStatus):
            raise ValueError("Appointment status must be an AppointmentStatus enum")
        if self.appointment_date is not None and not isinstance(self.appointment_date, datetime):
            raise ValueError("Appointment date must be a datetime when provided")
        
    def can_cancel(self)->bool:
        return self.appointment_status in [
            AppointmentStatus.SCHEDULED,
            AppointmentStatus.CONFIRMED
        ]
    
    def mark_notification_sent(self)->None:
        self.notification_sent = True

    def calculate_end_time(self)->datetime:
        if not isinstance(self.appointment_date, datetime):
            raise ValueError("appointment_date must be a datetime")
        
        return self.service.calculate_end_time(self.appointment_date)
    
    def needs_notification(self)->bool:
        if not isinstance(self.appointment_date, datetime):
            raise ValueError("appointment_date must be a datetime")
        if self.notification_sent:
            return False
        
        time_until = (self.appointment_date - datetime.now()).total_seconds()/60
        return 20 <= time_until <= 30
        
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "establishment": self.establishment.to_dict(),
            "employee": self.employee.to_dict(),
            "customer": self.customer.to_dict(),
            "service": self.service.to_dict(),
            "google_calendar_event_id": self.google_calendar_event_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "appointment_date": self.appointment_date.isoformat() if self.appointment_date else None,
            "appointment_status": self.appointment_status.value,
            "notification_sent": self.notification_sent
        }
    
    @staticmethod
    def from_dict(data: dict) -> Scheduling:
        establishment_data = data.get("establishment")
        employee_data = data.get("employee")
        customer_data = data.get("customer")
        service_data = data.get("service")
        appointment_status_data = data.get("appointment_status")
        
        if isinstance(appointment_status_data, str):
            appointment_status = AppointmentStatus(appointment_status_data)
        elif isinstance(appointment_status_data, AppointmentStatus):
            appointment_status = appointment_status_data
        else:
            appointment_status = appointment_status_data
        
        return Scheduling(
            id=data.get("id"),
            establishment=Establishment.from_dict(establishment_data) if isinstance(establishment_data, dict) else establishment_data,
            employee=Employee.from_dict(employee_data) if isinstance(employee_data, dict) else employee_data,
            customer=Customer.from_dict(customer_data) if isinstance(customer_data, dict) else customer_data,
            service=Service.from_dict(service_data) if isinstance(service_data, dict) else service_data,
            appointment_status=appointment_status,
            appointment_date=datetime.fromisoformat(data.get("appointment_date")) if data.get("appointment_date") else None,
            notification_sent=data.get("notification_sent"),
            created_at=datetime.fromisoformat(data.get("created_at")) if data.get("created_at") else None,
            google_calendar_event_id=data.get("google_calendar_event_id")
        )
