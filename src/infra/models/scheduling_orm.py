from sqlalchemy import Column, Integer, DateTime, String,Boolean, Enum, ForeignKey, func
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.mysql import CHAR
from datetime import datetime
from config import Base
from utils.enum import AppointmentStatus
import uuid

class SchedulingModel(Base):
    __tablename__ = "schedulings"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    uuid = Column(CHAR(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False)
    establishments_id = Column(Integer, ForeignKey("establishments.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    employees_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    customers_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    services_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    google_calendar_event_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    appointment_date = Column(DateTime, nullable=False)
    appointment_status = Column(Enum(AppointmentStatus), nullable=False)
    notification_sent = Column(Boolean, nullable=False)
    establishment = relationship("EstablishmentModel", backref="schedulings", foreign_keys=[establishments_id])
    employee = relationship("EmployeeModel", backref="schedulings", foreign_keys=[employees_id])
    customer = relationship("CustomerModel", backref="schedulings", foreign_keys=[customers_id])
    service = relationship("ServiceModel", backref="schedulings", foreign_keys=[services_id])

    def __repr__(self):
        return (
            f"<Scheduling(id={self.uuid}, appointment_date={self.appointment_date}, "
            f"status={self.appointment_status.value}, notification_sent={self.notification_sent})>"
        )

    def to_dict(self):
        return {
            "id": self.uuid,
            "establishments_id": self.establishments_id,
            "employees_id": self.employees_id,
            "customers_id": self.customers_id,
            "services_id": self.services_id,
            "google_calendar_event_id": self.google_calendar_event_id,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "appointment_date": self.appointment_date.strftime("%Y-%m-%d %H:%M:%S") if self.appointment_date else None,
            "appointment_status": self.appointment_status.value,
            "notification_sent": self.notification_sent
        }
    
    @validates('appointment_date')
    def validate_appointment_date(self, key, appointment_date):
        if appointment_date < datetime.now():
            raise ValueError("Appointment date must be in the future")
        return appointment_date
    
    @validates('notification_sent')
    def validate_notification_sent(self, key, notification_sent):
        if not isinstance(notification_sent, bool):
            raise ValueError("Notification sent must be a boolean value")
        return notification_sent
    
    @validates('appointment_status')
    def validate_appointment_status(self, key, status):
        if status not in AppointmentStatus:
            raise ValueError(f"Appointment status must be one of {[s.value for s in AppointmentStatus]}")
        return status