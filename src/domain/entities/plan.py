from __future__ import annotations
from dataclasses import dataclass
from utils.enum import TypePlan
from decimal import Decimal
from typing import Any

@dataclass
class Plan():

    id: int | None
    type_plan: TypePlan
    basic_price: Decimal | None
    max_employee: int | None
    allow_stock: bool | None
    allow_advanced_analysis: bool | None

    def __post_init__(self):
        if not self.type_plan or not isinstance(self.type_plan, TypePlan):
            raise ValueError("Type Plan is incorrect, must be a BRONZE, SILVER or GOLD. ")
        
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type_plan": self.type_plan,
            "basic_price": self.basic_price,
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
            id = data.get("id"),
            type_plan = type_plan,
            basic_price = data.get("basic_price"),
            max_employee = data.get("max_employee"),
            allow_stock = data.get("allow_stock"),
            allow_advanced_analysis = data.get("allow_advanced_analysis")
        )