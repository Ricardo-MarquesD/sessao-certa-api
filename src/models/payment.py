from sqlalchemy import Column, Integer, String, DateTime, Numeric, Enum, ForeignKey
from sqlalchemy.orm import relationship
from config import Base
from enum import Enum as enum

class PaymentStatus(enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REFUSED = "REFUSED"
    REFUND = "REFUND"

class PaymentType(enum):
    MONTHLY_SUBSCRIPTION = "MONTHLY_SUBSCRIPTION"
    ANNUAL_SUBSCRIPTION = "ANNUAL_SUBSCRIPTION"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)
    establishments_id = Column(Integer, ForeignKey("establishments.id"), nullable = False)
    valor = Column(Numeric(10,2), nullable = False)
    payment_day = Column(DateTime, nullable = False)
    payment_status = Column(Enum(PaymentStatus), nullable = False)
    payment_type = Column(Enum(PaymentType), nullable = False)
    employee_quantity = Column(Integer, nullable = False)
    gateway_transaction_id = Column(String(100), nullable = False)
    establishment = relationship("Establishment", backref = "payments", foreign_keys = [establishments_id])

    def __repr__(self):
        return (
            f"<Payment(id={self.id}, establishments_id={self.establishments_id}, valor={self.valor}, "
            f"payment_day={self.payment_day}, payment_status='{self.payment_status.value}', "
            f"payment_type='{self.payment_type.value}', employee_quantity={self.employee_quantity}, "
            f"gateway_transaction_id='{self.gateway_transaction_id}')>"
        )
    
    def to_dict(self):
        return {
            "id": self.id,
            "establishments_id": self.establishments_id,
            "valor": self.valor,
            "payment_day": self.payment_day.strftime("%Y-%m-%d %H:%M:%S") if self.payment_day else None,
            "payment_status": self.payment_status.value,
            "payment_type": self.payment_type.value,
            "employee_quantity": self.employee_quantity,
            "gateway_transaction_id": self.gateway_transaction_id,
            "establishment": self.establishment.to_dict() if self.establishment else None
        }