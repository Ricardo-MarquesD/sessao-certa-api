from pydantic import BaseModel, Field
from utils.enum import TypePlan
from decimal import Decimal
from domain.entities import Plan

class CreatePlanRequest(BaseModel):
    type_plan: TypePlan
    basic_price: Decimal = Field(gt=0)
    max_employee: int = Field(gt=0)
    allow_stock: bool = False
    allow_advanced_analysis: bool = False

class UpdatePlanRequest(BaseModel):
    basic_price: Decimal | None = Field(default=None, gt=0)
    max_employee: int | None = Field(default=None, gt=0)
    allow_stock: bool | None = None
    allow_advanced_analysis: bool | None = None

class PlanResponse(BaseModel):
    id: int
    type_plan: str
    basic_price: str
    max_employee: int
    allow_stock: bool
    allow_advanced_analysis: bool
    
    @classmethod
    def from_entity(cls, plan: Plan) -> PlanResponse:
        return cls(
            id=plan.id,
            type_plan=plan.type_plan.value,
            basic_price=str(plan.basic_price),
            max_employee=plan.max_employee,
            allow_stock=plan.allow_stock or False,
            allow_advanced_analysis=plan.allow_advanced_analysis or False
        )