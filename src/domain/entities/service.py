from __future__ import annotations
from dataclasses import dataclass
from .establishment import Establishment
from decimal import Decimal
from typing import Any

@dataclass
class Service():
    id: str | None  # UUID
    establishment: Establishment
    service_name: str
    time_duration: int
    price: Decimal | None
    description_service: str | None
    active: bool | None

    def __post_init__(self):
        if not isinstance(self.establishment, Establishment):
            raise ValueError("Establishment must be an Establishment instance")
        if not isinstance(self.service_name, str):
            raise ValueError("Service name must be a string")
        if not isinstance(self.time_duration, int) or self.time_duration <= 0:
            raise ValueError("Time duration must be a positive integer")
        if self.price is not None and (not isinstance(self.price, Decimal) or self.price < 0):
            raise ValueError("Price must be a non-negative Decimal when provided")
        
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "establishment": self.establishment.to_dict(),
            "service_name": self.service_name,
            "description_service": self.description_service,
            "time_duration": self.time_duration,
            "price": str(self.price) if self.price else None,
            "active": self.active
        }
    
    @staticmethod
    def from_dict(data: dict) -> Service:
        establishment_data = data.get("establishment")
        
        return Service(
            id=data.get("id"),
            establishment=Establishment.from_dict(establishment_data) if isinstance(establishment_data, dict) else establishment_data,
            service_name=data.get("service_name"),
            time_duration=int(data.get("time_duration")),
            price=Decimal(data.get("price")) if data.get("price") else None,
            description_service=data.get("description_service"),
            active=data.get("active")
        )
