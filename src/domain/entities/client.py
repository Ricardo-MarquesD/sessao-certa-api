from __future__ import annotations
from dataclasses import dataclass
from .user import User
from .plan import Plan
from typing import Any

@dataclass
class Client:
    id: int | None
    user: User
    plan: Plan
    stripe_customer_id: str | None = None

    def __post_init__(self):
        if not isinstance(self.user, User):
            raise ValueError("User must be a User instance")
        if not isinstance(self.plan, Plan):
            raise ValueError("Plan must be a Plan instance")
        
    def to_dict(self)->dict[str, Any]:
        return {
            "id": self.id,
            "user": self.user.to_dict(),
            "plan": self.plan.to_dict(),
            "stripe_customer_id": self.stripe_customer_id
        }
    
    @staticmethod
    def from_dict(data: dict) -> Client:
        user_data = data.get("user")
        plan_data = data.get("plan")
        
        return Client(
            id=data.get("id"),
            user=User.from_dict(user_data) if isinstance(user_data, dict) else user_data,
            plan=Plan.from_dict(plan_data) if isinstance(plan_data, dict) else plan_data,
            stripe_customer_id=data.get("stripe_customer_id")
        )