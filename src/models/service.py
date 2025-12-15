from sqlalchemy import Column, Integer, String, Numeric, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.mysql import CHAR
from config import Base
import uuid

class ServiceModel(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)
    uuid = Column(CHAR(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False)
    establishments_id = Column(Integer, ForeignKey("establishments.id", ondelete = "CASCADE", onupdate = "CASCADE"), nullable = False)
    service_name = Column(String(150), nullable = False)
    description_service = Column(Text, nullable = False)
    time_duration = Column(Integer, nullable = False)
    price = Column(Numeric(10,2), nullable = False)
    active = Column(Boolean, nullable = False, server_default = "1")
    establishment = relationship("EstablishmentModel", backref = "services", foreign_keys = [establishments_id])

    def __repr__(self):
        return (
            f"<Service(id={self.uuid}, establishments_id={self.establishments_id}, "
            f"service_name='{self.service_name}', description_service='{self.description_service}', "
            f"time_duration={self.time_duration}, price={self.price}, active={self.active})>"
        )
    
    def to_dict(self):
        return {
            "id": self.uuid,
            "establishments_id": self.establishments_id,
            "service_name": self.service_name,
            "description_service": self.description_service,
            "time_duration": self.time_duration,
            "price": float(self.price),
            "active": self.active,
            "establishment": self.establishment.to_dict() if self.establishment else None
        }
    
    @validates('service_name')
    def validate_service_name(self, key, name):
        if not name:
            raise ValueError("Service name cannot be empty")
        return name
    
    @validates('time_duration')
    def validate_time_duration(self, key, duration):
        if duration <= 0:
            raise ValueError("Time duration must be positive")
        return duration
    
    @validates('price')
    def validate_price(self, key, price_value):
        if price_value < 0:
            raise ValueError("Price cannot be negative")
        return price_value
    
    @validates('description_service')
    def validate_description_service(self, key, description):
        if not description:
            raise ValueError("Description cannot be empty")
        return description