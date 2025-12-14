from sqlalchemy import Column, Integer, DateTime, Boolean, Enum, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR
from config import Base
from enum import Enum as enum
import uuid

class AppointmentStatus(enum):
    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    CANCELED = "CANCELED"
    COMPLETED = "COMPLETED"
    NO_SHOW = "NO_SHOW"

class Scheduling(Base):
    __tablename__ = "schedulings"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    uuid = Column(CHAR(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False)
    establishments_id = Column(Integer, ForeignKey("establishments.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    employees_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    customers_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    services_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    appointment_date = Column(DateTime, nullable=False)
    appointment_status = Column(Enum(AppointmentStatus), nullable=False)
    notification_sent = Column(Boolean, nullable=False)
    establishment = relationship("Establishment", backref="schedulings", foreign_keys=[establishments_id])
    employee = relationship("Employee", backref="schedulings", foreign_keys=[employees_id])
    customer = relationship("Customer", backref="schedulings", foreign_keys=[customers_id])
    service = relationship("Service", backref="schedulings", foreign_keys=[services_id])

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
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "appointment_date": self.appointment_date.strftime("%Y-%m-%d %H:%M:%S") if self.appointment_date else None,
            "appointment_status": self.appointment_status.value,
            "notification_sent": self.notification_sent
        }