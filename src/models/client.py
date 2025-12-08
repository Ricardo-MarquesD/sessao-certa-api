from sqlalchemy import Column, Integer, ForeignKey, func
from sqlalchemy.orm import relationship
from ...config import Base
from .user import User

class Client(User):
    __tablename__ = "clients"
    id = Column(Integer, primary_key = True, autoincrement = True, nullable= False)
    users_id = Column(Integer, ForeignKey("users.id"), nullable = False)
    plans_id = Column(Integer, ForeignKey("plans.id"), nullable = False)

    __mapper_args__ = {
        "polymorphic_identity": "client"
    }

    def __repr__(self):
        return
    
    def to_dict(self):
        return {
            "id": self.id,
            "users_id": self.users_id,
            "plans_id": self.plans_id,
            "User": super().to_dict()
        }
        