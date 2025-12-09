from sqlalchemy import Column, Integer, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import relationship
from config import Base
from enum import Enum as enum

class MovementType(enum):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    stock_products_id = Column(Integer, ForeignKey("stock_products.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    movement_type = Column(Enum(MovementType), nullable=False)
    quantity = Column(Integer, nullable=False)
    date = Column(DateTime, server_default=func.current_timestamp())
    stock_product = relationship("StockProduct", backref="stock_movements", foreign_keys=[stock_products_id])

    def __repr__(self):
        return (
            f"<StockMovement(id={self.id}, stock_products_id={self.stock_products_id}, movement_type='{self.movement_type.value}', "
            f"quantity={self.quantity}, date={self.date})>"
        )

    def to_dict(self):
        return {
            "id": self.id,
            "stock_products_id": self.stock_products_id,
            "movement_type": self.movement_type.value,
            "quantity": self.quantity,
            "date": self.date.strftime("%Y-%m-%d %H:%M:%S") if self.date else None,
            "stock_product": self.stock_product.to_dict() if self.stock_product else None
        }