from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from config import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    phone_number = Column(String(30), nullable=False)
    establishments_id = Column(Integer, ForeignKey("establishments.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    establishment = relationship("Establishment", backref="customers", foreign_keys=[establishments_id])

    def __repr__(self):
        return (
            f"<Customer(id={self.id}, phone_number='{self.phone_number}', "
            f"establishments_id={self.establishments_id})>"
        )
    
    def to_dict(self):
        return {
            "id": self.id,
            "phone_number": self.phone_number,
            "establishments_id": self.establishments_id,
            "establishment": self.establishment.to_dict() if self.establishment else None
        }