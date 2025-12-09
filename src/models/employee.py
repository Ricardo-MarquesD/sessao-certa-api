from sqlalchemy import Column, Integer, Numeric, JSON, ForeignKey
from sqlalchemy.orm import relationship
from config import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key = True, autoincrement = True, nullable= False)
    users_id = Column(Integer, ForeignKey("users.id", ondelete = "CASCADE", onupdate = "CASCADE"), nullable = False)
    establishments_id = Column(Integer, ForeignKey("establishments.id", ondelete = "CASCADE", onupdate = "CASCADE"), nullable = False)
    percentage_commission = Column(Numeric(5, 2), nullable = False)
    available_hours = Column(JSON, nullable = False)
    user = relationship("User", backref = "employee", uselist = False, foreign_keys = [users_id])
    establishment = relationship("Establishment", backref = "employees", foreign_keys = [establishments_id])
    def __repr__(self):
        return (
            f"<Employee(id={self.id}, users_id={self.users_id}, establishments_id={self.establishments_id}, "
            f"percentage_commission={self.percentage_commission}, available_hours={self.available_hours})>"
        )
    
    def to_dict(self):
        return {
            "id": self.id,
            "users_id": self.users_id,
            "establishments_id": self.establishments_id,
            "percentage_commission": float(self.percentage_commission),
            "available_hours": self.available_hours,
            "user": self.user.to_dict() if self.user else None,
            "establishment": self.establishment.to_dict() if self.establishment else None
        }