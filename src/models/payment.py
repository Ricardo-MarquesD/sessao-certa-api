from sqlalchemy import Column, Integer, String, DateTime, Numeric, Enum, ForeignKey
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.mysql import CHAR
from config import Base
from enum import Enum as enum
import uuid

class PaymentStatus(enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REFUSED = "REFUSED"
    REFUND = "REFUND"

class PaymentType(enum):
    MONTHLY_SUBSCRIPTION = "MONTHLY_SUBSCRIPTION"
    ANNUAL_SUBSCRIPTION = "ANNUAL_SUBSCRIPTION"

class PaymentModel(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)
    uuid = Column(CHAR(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False)
    establishments_id = Column(Integer, ForeignKey("establishments.id"), nullable = False)
    valor = Column(Numeric(10,2), nullable = False)
    payment_day = Column(DateTime, nullable = False)
    payment_status = Column(Enum(PaymentStatus), nullable = False)
    payment_type = Column(Enum(PaymentType), nullable = False)
    employee_quantity = Column(Integer, nullable = False)
    gateway_transaction_id = Column(String(100), nullable = False)
    establishment = relationship("EstablishmentModel", backref = "payments", foreign_keys = [establishments_id])

    def __repr__(self):
        return (
            f"<Payment(id={self.uuid}, establishments_id={self.establishments_id}, valor={self.valor}, "
            f"payment_day={self.payment_day}, payment_status='{self.payment_status.value}', "
            f"payment_type='{self.payment_type.value}', employee_quantity={self.employee_quantity}, "
            f"gateway_transaction_id='{self.gateway_transaction_id}')>"
        )
    
    def to_dict(self):
        return {
            "id": self.uuid,
            "establishments_id": self.establishments_id,
            "valor": self.valor,
            "payment_day": self.payment_day.strftime("%Y-%m-%d %H:%M:%S") if self.payment_day else None,
            "payment_status": self.payment_status.value,
            "payment_type": self.payment_type.value,
            "employee_quantity": self.employee_quantity,
            "gateway_transaction_id": self.gateway_transaction_id,
            "establishment": self.establishment.to_dict() if self.establishment else None
        }
    
    @validates('valor')
    def validate_valor(self, key, value):
        if value < 0:
            raise ValueError("Valor must be non-negative")
        return value
    
    @validates('employee_quantity')
    def validate_employee_quantity(self, key, quantity):
        if quantity < 0:
            raise ValueError("Employee quantity must be non-negative")
        if not isinstance(quantity, int):
            raise ValueError("Employee quantity must be an integer")
        return quantity
    
    @validates('payment_status')
    def validate_payment_status(self, key, status):
        if status not in PaymentStatus:
            raise ValueError(f"Payment status must be one of {[s.value for s in PaymentStatus]}")
        return status
    
    @validates('payment_type')
    def validate_payment_type(self, key, ptype):
        if ptype not in PaymentType:
            raise ValueError(f"Payment type must be one of {[t.value for t in PaymentType]}")
        return ptype
    
    @validates('gateway_transaction_id')
    def validate_gateway_transaction_id(self, key, transaction_id):
        if not transaction_id:
            raise ValueError("Gateway transaction ID cannot be empty")
        return transaction_id