from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .establishment import Establishment
from decimal import Decimal
from datetime import datetime
from utils.enum.payment_enum import PaymentStatus, PaymentType

@dataclass
class Payment():
    id: str | None # Lembresse de ser o UUID
    establishment: Establishment
    valor: Decimal
    payment_status: PaymentStatus
    payment_type: PaymentType
    payment_day: datetime | None = None
    employee_quantity: int | None = None
    gateway_transaction_id: str | None = None

    def __post_init__(self):
        if not isinstance(self.establishment, Establishment):
            raise ValueError("Establishment must be an Establishment instance")
        if not isinstance(self.valor, Decimal) or self.valor <= 0:
            raise ValueError("Valor must be a positive Decimal")
        if not isinstance(self.payment_status, PaymentStatus):
            raise ValueError("Payment status must be a PaymentStatus enum")
        if not isinstance(self.payment_type, PaymentType):
            raise ValueError("Payment type must be a PaymentType enum")
        
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "establishment": self.establishment.to_dict(),
            "valor": str(self.valor),
            "payment_day": self.payment_day.isoformat() if self.payment_day else None,
            "payment_status": self.payment_status.value,
            "payment_type": self.payment_type.value,
            "employee_quantity": self.employee_quantity,
            "gateway_transaction_id": self.gateway_transaction_id
        }
    
    @staticmethod
    def from_dict(data: dict) -> Payment:
        establishment_data = data.get("establishment")
        
        return Payment(
            id=data.get("id"),
            establishment=Establishment.from_dict(establishment_data) if isinstance(establishment_data, dict) else establishment_data,
            valor=Decimal(data.get("valor")),
            payment_status=PaymentStatus(data.get("payment_status")),
            payment_type=PaymentType(data.get("payment_type")),
            payment_day=datetime.fromisoformat(data.get("payment_day")) if data.get("payment_day") else None,
            employee_quantity=data.get("employee_quantity"),
            gateway_transaction_id=data.get("gateway_transaction_id")
        )
