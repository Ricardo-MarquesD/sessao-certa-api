from sqlalchemy import Column, Integer, String, Numeric, Enum, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from enum import Enum as enum
from config import Base

class MovementType(enum):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

class StockProduct(Base):
    __tablename__ = "stock_products"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    establishments_id = Column(Integer, ForeignKey("establishments.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    product_name = Column(String(150), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    establishment = relationship("Establishment", backref="stock_products", foreign_keys=[establishments_id])

    def __repr__(self):
        return (
            f"<StockProduct(id={self.id}, product_name='{self.product_name}', quantity={self.quantity}, price={self.price})>"
        )

    def to_dict(self):
        return {
            "id": self.id,
            "establishments_id": self.establishments_id,
            "product_name": self.product_name,
            "quantity": self.quantity,
            "price": float(self.price) if self.price is not None else None,
            "establishment": self.establishment.to_dict() if self.establishment else None
        }
    
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