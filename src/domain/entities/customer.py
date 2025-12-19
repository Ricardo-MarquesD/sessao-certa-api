from __future__ import annotations
from dataclasses import dataclass
from .establishment import Establishment
from typing import Any

@dataclass
class Customer():
    id: str | None # Lembrar desse id ser o UUID
    establishment: Establishment
    customer_name: str | None
    phone_number: str

    def __post_init__(self):
        if not self.establishment or not isinstance(self.establishment, Establishment):
            raise ValueError("Establishment must be a Establishment instance")
        if not self.phone_number or len(self.phone_number) < 8:
            raise ValueError("Phone Number is incorrect, is too short")
    
    def to_dict(self)->dict[str, Any]:
        return {
            "id": self.id,
            "establishment": self.establishment.to_dict(),
            "customer_name": self.customer_name,
            "phone_number": self.phone_number
        }
    
    @staticmethod
    def from_dict(data: dict)->Customer:
        establishment_data = data.get("establishment")

        return Customer(
            id = data.get("id"),
            establishment = Establishment.from_dict(establishment_data) if isinstance(establishment_data, dict) else establishment_data,
            customer_name = data.get("customer_name"),
            phone_number = data.get("phone_number")
        )