from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func, Text
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.mysql import CHAR
from config import Base
import uuid

class EstablishmentModel(Base):
    __tablename__ = "establishments"

    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)
    uuid = Column(CHAR(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False)
    clients_id = Column(Integer, ForeignKey("clients.id", ondelete = "CASCADE", onupdate = "CASCADE"), nullable = False)
    stripe_subscription_id = Column(String(255), unique=True, nullable=True)
    waba_id = Column(String(100), nullable=False)
    whatsapp_business_token = Column(Text, nullable=False)
    google_calendar_access_token = Column(Text, nullable=True)
    google_calendar_refresh_token = Column(Text, nullable=True)
    google_calendar_expiry = Column(DateTime, nullable=True)
    google_calendar_id = Column(String(255), nullable=True)
    establishment_name = Column(String(150), nullable = False)
    cnpj = Column(String(18), nullable = False)
    chatbot_phone_number = Column(String(30), nullable = False)
    address = Column(String(255), nullable = False)
    img_url = Column(String(500), nullable=False)
    subscription_date = Column(DateTime, server_default = func.current_timestamp())
    due_date = Column(DateTime, nullable = False)
    trial_active = Column(Boolean, nullable = False, server_default = "0")
    client = relationship("ClientModel", backref = "establishment", foreign_keys = [clients_id], uselist = False)

    def __repr__(self):
        return (
            f"<Establishment(id={self.uuid}, establishment_name='{self.establishment_name}', cnpj='{self.cnpj}', "
            f"chatbot_phone_number={self.chatbot_phone_number}, address={self.address}, subscription_date={self.subscription_date}, "
            f"due_date={self.due_date}, trial_active={self.trial_active})>"
        )
    
    def to_dict(self):
        return {
            "id": self.uuid,
            "clients_id": self.clients_id,
            "stripe_subscription_id": self.stripe_subscription_id,
            "waba_id": self.waba_id,
            "whatsapp_business_token": self.whatsapp_business_token,
            "google_calendar_access_token": self.google_calendar_access_token,
            "google_calendar_refresh_token": self.google_calendar_refresh_token,
            "google_calendar_expiry": self.google_calendar_expiry.strftime("%Y-%m-%d %H:%M:%S") if self.google_calendar_expiry else None,
            "google_calendar_id": self.google_calendar_id,
            "establishment_name": self.establishment_name,
            "cnpj": self.cnpj,
            "chatbot_phone_number": self.chatbot_phone_number,
            "address": self.address,
            "subscription_date": self.subscription_date.strftime("%Y-%m-%d %H:%M:%S") if self.subscription_date else None,
            "due_date": self.due_date.strftime("%Y-%m-%d %H:%M:%S") if self.due_date else None,
            "trial_active": self.trial_active,
            "client": self.client.to_dict() if self.client else None
        }
    
    @validates('cnpj')
    def validate_cnpj(self, key, cnpj_value):
        if len(cnpj_value) != 14:
            raise ValueError("Invalid CNPJ")
        return cnpj_value
    
    @validates('chatbot_phone_number')
    def validate_phone(self, key, number):
        if len(number) < 8:
            raise ValueError("Invalid phone number")
        return number
    
    @validates('address')
    def validate_address(self, key, address_value):
        if not address_value:
            raise ValueError("Address cannot be empty")
        return address_value