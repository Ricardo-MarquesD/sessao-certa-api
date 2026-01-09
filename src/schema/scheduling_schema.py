from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from utils.enum import AppointmentStatus
from domain import Scheduling
from schema import (
    EstablishmentResponse,
    EmployeeResponse,
    CustomerResponse,
    ServiceResponse
)

class CreateSchedulingRequest(BaseModel):
    establishment_id: str
    employee_id: int
    customer_id: str
    service_id: str
    appointment_date: datetime
    
    @field_validator('appointment_date')
    @classmethod
    def validate_future_date(cls, v: datetime):
        if v <= datetime.now():
            raise ValueError("Appointment date must be in the future")
        return v

class UpdateSchedulingRequest(BaseModel):
    appointment_date: datetime | None = None
    employee_id: int | None = None
    
    @field_validator('appointment_date')
    @classmethod
    def validate_future_date(cls, v: datetime | None):
        if v is not None and v <= datetime.now():
            raise ValueError("Appointment date must be in the future")
        return v

class UpdateSchedulingStatusRequest(BaseModel):
    appointment_status: AppointmentStatus

class CancelSchedulingRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=500)

class SchedulingResponse(BaseModel):
    id: str
    establishment_id: str
    employee_id: int
    customer_id: str
    service_id: str
    appointment_date: datetime
    appointment_end_time: datetime
    appointment_status: str
    notification_sent: bool
    created_at: datetime | None
    can_cancel: bool
    
    @classmethod
    def from_entity(cls, scheduling: Scheduling) -> SchedulingResponse:
        return cls(
            id=str(scheduling.id),
            establishment_id=str(scheduling.establishment.id),
            employee_id=scheduling.employee.id,
            customer_id=str(scheduling.customer.id),
            service_id=str(scheduling.service.id),
            appointment_date=scheduling.appointment_date,
            appointment_end_time=scheduling.calculate_end_time(),
            appointment_status=scheduling.appointment_status.value,
            notification_sent=scheduling.notification_sent or False,
            created_at=scheduling.created_at,
            can_cancel=scheduling.can_cancel()
        )

class SchedulingDetailResponse(BaseModel):
    id: str
    establishment: EstablishmentResponse
    employee: EmployeeResponse
    customer: CustomerResponse
    service: ServiceResponse
    appointment_date: datetime
    appointment_end_time: datetime
    appointment_status: str
    notification_sent: bool
    created_at: datetime | None
    can_cancel: bool
    needs_notification: bool
    
    @classmethod
    def from_entity(cls, scheduling: Scheduling) -> SchedulingDetailResponse:
        return cls(
            id=str(scheduling.id),
            establishment=EstablishmentResponse.from_entity(scheduling.establishment),
            employee=EmployeeResponse.from_entity(scheduling.employee),
            customer=CustomerResponse.from_entity(scheduling.customer),
            service=ServiceResponse.from_entity(scheduling.service),
            appointment_date=scheduling.appointment_date,
            appointment_end_time=scheduling.calculate_end_time(),
            appointment_status=scheduling.appointment_status.value,
            notification_sent=scheduling.notification_sent or False,
            created_at=scheduling.created_at,
            can_cancel=scheduling.can_cancel(),
            needs_notification=scheduling.needs_notification()
        )

class SchedulingCalendarResponse(BaseModel):
    id: str
    customer_name: str
    service_name: str
    employee_name: str
    appointment_date: datetime
    appointment_end_time: datetime
    status: str
    duration_minutes: int
    
    @classmethod
    def from_entity(cls, scheduling: Scheduling) -> SchedulingCalendarResponse:
        return cls(
            id=str(scheduling.id),
            customer_name=scheduling.customer.customer_name,
            service_name=scheduling.service.service_name,
            employee_name=scheduling.employee.user.user_name,
            appointment_date=scheduling.appointment_date,
            appointment_end_time=scheduling.calculate_end_time(),
            status=scheduling.appointment_status.value,
            duration_minutes=scheduling.service.time_duration
        )