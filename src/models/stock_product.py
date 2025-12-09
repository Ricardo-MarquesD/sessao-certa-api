from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from config import Base

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