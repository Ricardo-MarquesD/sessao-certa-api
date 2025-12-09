from sqlalchemy import Column, Integer, String, Numeric, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from config import Base

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)
    establishments_id = Column(Integer, ForeignKey("establishments.id", ondelete = "CASCADE", onupdate = "CASCADE"), nullable = False)
    service_name = Column(String(150), nullable = False)
    description_service = Column(Text, nullable = True)
    time_duration = Column(Integer, nullable = False)
    price = Column(Numeric(10,2), nullable = False)
    active = Column(Boolean, default = True, nullable = False)
    establishment = relationship("Establishment", backref = "services", foreign_keys = [establishments_id])

    def __repr__(self):
        return (
            f"<Service(id={self.id}, establishments_id={self.establishments_id}, "
            f"service_name='{self.service_name}', description_service='{self.description_service}', "
            f"time_duration={self.time_duration}, price={self.price}, active={self.active})>"
        )
    
    def to_dict(self):
        return {
            "id": self.id,
            "establishments_id": self.establishments_id,
            "service_name": self.service_name,
            "description_service": self.description_service,
            "time_duration": self.time_duration,
            "price": float(self.price),
            "active": self.active,
            "establishment": self.establishment.to_dict() if self.establishment else None
        }