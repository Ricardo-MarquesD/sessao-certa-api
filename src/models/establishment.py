from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from ...config import Base

class Establishment(Base):
    __tablename__ = "establishments"

    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)
    clients_id = Column(Integer, ForeignKey("clients.id", ondelete = "CASCADE", onupdate = "CASCADE"), nullable = False)
    establishment_name = Column(String(150), nullable = False)
    cnpj = Column(String(14), nullable = False)
    chatbot_phone_number = Column(String(30), nullable = False)
    address = Column(String(255), nullable = False)
    subscription_date = Column(DateTime, server_default = func.current_timestamp())
    due_date = Column(DateTime, nullable = False)
    trial_active = Column(Boolean, nullable = False, server_default = "0")
    client = relationship("Client", backref = "establishment", foreign_keys = [clients_id], uselist = False)

    def __repr__(self):
        return (
            f"<Establishment(id={self.id}, establishment_name='{self.establishment_name}', cnpj='{self.cnpj}', "
            f"chatbot_phone_number={self.chatbot_phone_number}, address={self.address}, subscription_date={self.subscription_date}, "
            f"due_date={self.due_date}, trial_active={self.trial_active})>"
        )
    
    def to_dict(self):
        return {
            "id": self.id,
            "clients_id": self.clients_id,
            "establishment_name": self.establishment_name,
            "cnpj": self.cnpj,
            "chatbot_phone_number": self.chatbot_phone_number,
            "address": self.address,
            "subscription_date": self.subscription_date.strftime("%Y-%m-%d %H:%M:%S") if self.subscription_date else None,
            "due_date": self.due_date.strftime("%Y-%m-%d %H:%M:%S") if self.due_date else None,
            "trial_active": self.trial_active,
            "client": self.client.to_dict() if self.client else None
        }