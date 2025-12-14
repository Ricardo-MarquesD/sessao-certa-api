from sqlalchemy import Column, Integer, Numeric, JSON, ForeignKey
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.mysql import CHAR
from config import Base
import uuid

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key = True, autoincrement = True, nullable= False)
    uuid = Column(CHAR(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False)
    users_id = Column(Integer, ForeignKey("users.id", ondelete = "CASCADE", onupdate = "CASCADE"), nullable = False)
    establishments_id = Column(Integer, ForeignKey("establishments.id", ondelete = "CASCADE", onupdate = "CASCADE"), nullable = False)
    percentage_commission = Column(Numeric(5, 2), nullable = True)
    available_hours = Column(JSON, nullable = False)
    user = relationship("User", backref = "employees", uselist = False, foreign_keys = [users_id])
    establishment = relationship("Establishment", backref = "employees", foreign_keys = [establishments_id])
    def __repr__(self):
        return (
            f"<Employee(id={self.uuid}, users_id={self.users_id}, establishments_id={self.establishments_id}, "
            f"percentage_commission={self.percentage_commission}, available_hours={self.available_hours})>"
        )
    
    def to_dict(self):
        return {
            "id": self.uuid,
            "users_id": self.users_id,
            "establishments_id": self.establishments_id,
            "percentage_commission": float(self.percentage_commission),
            "available_hours": self.available_hours,
            "user": self.user.to_dict() if self.user else None,
            "establishment": self.establishment.to_dict() if self.establishment else None
        }
    
    @validates('percentage_commission')
    def validate_percentage_commission(self, key, value):
        if value is not None and (value < 0 or value > 100):
            raise ValueError("Percentage commission must be between 0 and 100")
        return value
    
    @validates('available_hours')
    def validate_available_hours(self, key, hours):
        if not isinstance(hours, dict):
            raise ValueError("Available hours must be a dictionary")
        return hours