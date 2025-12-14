from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from config import Base

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key = True, autoincrement = True, nullable= False)
    users_id = Column(Integer, ForeignKey("users.id", ondelete = "CASCADE", onupdate = "CASCADE"), nullable = False)
    plans_id = Column(Integer, ForeignKey("plans.id", ondelete = "RESTRICT", onupdate = "CASCADE"), nullable = False)
    user = relationship("User", backref = "client", uselist = False, foreign_keys = [users_id])
    plan = relationship("Plan", backref = "clients", foreign_keys = [plans_id])

    def __repr__(self):
        user_name = self.user.user_name if self.user else None
        return (
        f"<Client(id={self.id}, users_id={self.users_id}, plans_id={self.plans_id}, "
        f"user_name='{user_name}')>"
    )
    
    def to_dict(self):
        return {
            "id": self.id,
            "users_id": self.users_id,
            "plans_id": self.plans_id,
            "user": self.user.to_dict() if self.user else None,
            "plan": self.plan.to_dict() if self.plan else None
        }