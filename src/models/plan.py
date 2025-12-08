from sqlalchemy import Column, Integer, Boolean, Numeric, Enum
from ...config import Base
from enum import Enum as enum

class TypePlan(enum):
    BRONZE = 0
    SILVER = 1
    GOLD = 2

class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key = True, autoincrement = True,nullable = False)
    type_plan = Column(Enum(TypePlan), nullable = False)
    basic_price = Column(Numeric(10,2), nullable = False)
    max_employee = Column(Integer, nullable = False)
    allow_stock = Column(Boolean, nullable = False)
    allow_advanced_analysis = Column(Boolean, nullable = False)

    def __repr__(self):
        return (
            f"<Plan(id={self.id}, type_plan='{self.type_plan.name}', basic_price={self.basic_price}, "
            f"max_employee={self.max_employee}, allow_stock={self.allow_stock}, allow_advanced_analysis={self.allow_advanced_analysis})>"   
        )
    
    def to_dict(self):
        return {
            "id": self.id,
            "type_plan": self.type_plan.name,
            "basic_price": self.basic_price,
            "max_employee": self.max_employee,
            "allow_stock": self.allow_stock,
            "allow_advanced_analysis": self.allow_advanced_analysis
        }