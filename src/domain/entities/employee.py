from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .user import User
from .establishment import Establishment
from decimal import Decimal

@dataclass
class Employee():
    id: str | None
    user: User
    establishment: Establishment
    percentage_commission: Decimal | None
    available_hours: dict | None

    def __post_init__(self):
        if not isinstance(self.user, User):
            raise ValueError("User must be a User instance")
        if not isinstance(self.establishment, Establishment):
            raise ValueError("Establishment must be a Establishment instance")
        
    def to_dict(self)->dict[str, Any]:
        return {
            "id": self.id,
            "user": self.user.to_dict(),
            "establishment": self.establishment.to_dict(),
            "percentage_commission": self.percentage_commission,
            "available_hours": self.available_hours
        }
    
    @staticmethod
    def from_dict(data: dict)->Employee:
        user_data = data.get("user")
        establishment_data = data.get("establishment")

        return Employee(
            id = data.get("id"),
            user = User.from_dict(user_data) if isinstance(user_data, dict) else user_data,
            establishment = Establishment.from_dict(establishment_data) if isinstance(establishment_data, dict) else establishment_data,
            percentage_commission = data.get("percentage_commission"),
            available_hours = data.get("available_hours")
        )