from sqlalchemy import Column, Integer, Numeric, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .user import User

class Employee(User):
    __tablename__ = "employees"

    id = Column(Integer, primary_key = True, autoincrement = True, nullable= False)
    users_id = Column(Integer, ForeignKey("users.id", ondelete = "CASCADE", onupdate = "CASCADE"), nullable = False)
    establishment_id = Column(Integer, ForeignKey("establishments.id", ondelete = "CASCADE", onupdate = "CASCADE"), nullable = False)
    percentage_commission = Column(Numeric(5, 2), nullable = False)
    available_hours = Column(JSON, nullable = False)
    user = relationship("User", backref = "employee", uselist = False, foreign_keys = [users_id])
    establishment = relationship("Establishment", backref = "employees", foreign_keys = [establishment_id])

    __mapper_args__ = {
        "polymorphic_identity": "employee"
    }

    def __repr__(self):
        return (
            f"<Employee(id={self.id}, users_id={self.users_id}, establishment_id={self.establishment_id}, "
            f"percentage_commission={self.percentage_commission}, available_hours={self.available_hours})>"
        )
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "id_employee": self.id,
            "users_id": self.users_id,
            "establishment_id": self.establishment_id,
            "percentage_commission": float(self.percentage_commission),
            "available_hours": self.available_hours,
            "user": self.user.to_dict() if self.user else None,
            "establishment": self.establishment.to_dict() if self.establishment else None
        })
        return data