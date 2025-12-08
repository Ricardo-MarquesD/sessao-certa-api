from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .user import User

class Client(User):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key = True, autoincrement = True, nullable= False)
    users_id = Column(Integer, ForeignKey("users.id", ondelete = "CASCADE", onupdate = "CASCADE"), nullable = False)
    plans_id = Column(Integer, ForeignKey("plans.id", ondelete = "RESTRICT", onupdate = "CASCADE"), nullable = False)
    user = relationship("User", backref = "client", uselist = False, foreign_keys = [users_id])
    plan = relationship("Plan", backref = "clients", foreign_keys = [plans_id])

    __mapper_args__ = {
        "polymorphic_identity": "client"
    }

    def __repr__(self):
        return (
            f"<Client(id={self.id}, users_id={self.users_id}, plans_id={self.plans_id}, "
            f"user_name='{self.user.user_name}')>"
        )
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "id_client": self.id,
            "users_id": self.users_id,
            "plans_id": self.plans_id,
            "user": self.user.to_dict() if self.user else None,
            "plan": self.plan.to_dict() if self.plan else None
        })
        return data