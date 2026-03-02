from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func, Text, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR
from config import Base
import uuid

class ContextModel(Base):
    __tablename__ = "contexts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(CHAR(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False)
    establishments_id = Column(Integer, ForeignKey("establishments.id", ondelete="CASCADE"), nullable=False)
    customers_id = Column(Integer, ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)
    phone_number = Column(String(30), nullable=False)
    last_message_id = Column(String(255), nullable=True)
    context_arrow = Column(String(255), nullable=True)
    is_open = Column(Boolean, server_default="0")
    context_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    expires_at = Column(DateTime, nullable=False)

    establishment = relationship("EstablishmentModel", backref="contexts", foreign_keys=[establishments_id])
    customer = relationship("CustomerModel", backref="contexts", foreign_keys=[customers_id])

    __table_args__ = (
        Index("idx_active_conv", "establishments_id", "phone_number", "is_open"),
    )

    def __repr__(self):
        return (
            f"<Context(id={self.id}, uuid={self.uuid}, phone_number='{self.phone_number}', "
            f"is_open={self.is_open}, expires_at={self.expires_at})>"
        )

    def to_dict(self):
        return {
            "id": self.uuid,
            "establishments_id": self.establishments_id,
            "customers_id": self.customers_id,
            "phone_number": self.phone_number,
            "last_message_id": self.last_message_id,
            "context_arrow": self.context_arrow,
            "is_open": self.is_open,
            "context_data": self.context_data,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None,
            "expires_at": self.expires_at.strftime("%Y-%m-%d %H:%M:%S") if self.expires_at else None,
        }
