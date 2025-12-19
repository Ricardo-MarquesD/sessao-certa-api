from __future__ import annotations
from dataclasses import dataclass
from utils.enum import TypePlan
from decimal import Decimal
from typing import Any

@dataclass
class Plan():

    id: int | None
    type_plan: TypePlan
    basic_price: Decimal
    max_employee: int
    allow_stock: bool | None
    allow_advanced_analysis: bool | None

    def __post_init__(self):
        if not isinstance(self.type_plan, TypePlan):
            raise ValueError("Type Plan is incorrect, must be a BRONZE, SILVER or GOLD")
        if not isinstance(self.basic_price, Decimal) or self.basic_price <= 0:
            raise ValueError("Basic price must be a positive Decimal")
        if not isinstance(self.max_employee, int) or self.max_employee <= 0:
            raise ValueError("Max employee must be a positive integer")
        
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type_plan": self.type_plan.value,
            "basic_price": str(self.basic_price),
            "max_employee": self.max_employee,
            "allow_stock": self.allow_stock,
            "allow_advanced_analysis": self.allow_advanced_analysis
        }
    
    @staticmethod
    def from_dict(data: dict) -> Plan:
        type_plan_data = data.get("type_plan")
        if isinstance(type_plan_data, str):
            type_plan = TypePlan(type_plan_data)
        elif isinstance(type_plan_data, TypePlan):
            type_plan = type_plan_data
        else:
            type_plan = type_plan_data

        return Plan(
            id=data.get("id"),
            type_plan=type_plan,
            basic_price=Decimal(data.get("basic_price")),
            max_employee=int(data.get("max_employee")),
            allow_stock=data.get("allow_stock"),
            allow_advanced_analysis=data.get("allow_advanced_analysis")
        )