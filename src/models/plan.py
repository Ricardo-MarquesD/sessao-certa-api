from sqlalchemy import Column, Integer, Boolean, Numeric, Enum
from sqlalchemy.orm import validates
from enum import Enum as enum
from config import Base

class TypePlan(enum):
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"

class PlanModel(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key = True, autoincrement = True,nullable = False)
    type_plan = Column(Enum(TypePlan), nullable = False)
    basic_price = Column(Numeric(10,2), nullable = False)
    max_employee = Column(Integer, nullable = False)
    allow_stock = Column(Boolean, nullable = False)
    allow_advanced_analysis = Column(Boolean, nullable = False)

    def __repr__(self):
        return (
            f"<Plan(id={self.id}, type_plan='{self.type_plan.value}', basic_price={self.basic_price}, "
            f"max_employee={self.max_employee}, allow_stock={self.allow_stock}, allow_advanced_analysis={self.allow_advanced_analysis})>"   
        )
    
    def to_dict(self):
        return {
            "id": self.id,
            "type_plan": self.type_plan.value,
            "basic_price": self.basic_price,
            "max_employee": self.max_employee,
            "allow_stock": self.allow_stock,
            "allow_advanced_analysis": self.allow_advanced_analysis
        }
    
    @validates('basic_price')
    def validate_basic_price(self, key, price):
        if price < 0:
            raise ValueError("Basic price must be non-negative")
        return price
    
    @validates('max_employee')
    def validate_max_employee(self, key, max_emp):
        if max_emp < 1:
            raise ValueError("Max employee must be at least 1")
        return max_emp
    
    @validates('type_plan')
    def validate_type_plan(self, key, plan_type):
        if plan_type not in TypePlan:
            raise ValueError("Invalid plan type, type must be BRONZE, SILVER, or GOLD")
        return plan_type