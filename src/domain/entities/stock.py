from __future__ import annotations
from dataclasses import dataclass
from .establishment import Establishment
from utils.enum import MovementType
from decimal import Decimal
from datetime import datetime
from typing import Any

@dataclass
class StockProduct():
    id: int | None
    establishment: Establishment
    product_name: str
    quantity: int
    price: Decimal | None

    def __post_init__(self):
        if not isinstance(self.establishment, Establishment):
            raise ValueError("Establishment must be an Establishment instance")
        if not isinstance(self.product_name, str):
            raise ValueError("Product name must be a string")
        if not isinstance(self.quantity, int) or self.quantity < 0:
            raise ValueError("Quantity must be a non-negative integer")
        
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "establishment": self.establishment.to_dict(),
            "product_name": self.product_name,
            "quantity": self.quantity,
            "price": str(self.price) if self.price else None
        }
    
    @staticmethod
    def from_dict(data: dict) -> StockProduct:
        establishment_data = data.get("establishment")
        
        return StockProduct(
            id=data.get("id"),
            establishment=Establishment.from_dict(establishment_data) if isinstance(establishment_data, dict) else establishment_data,
            product_name=data.get("product_name"),
            quantity=int(data.get("quantity")),
            price=Decimal(data.get("price")) if data.get("price") else None
        )
    
@dataclass
class StockMovement():
    id: int | None
    stock_product: StockProduct
    movement_type: MovementType
    quantity: int | None
    date: datetime | None

    def __post_init__(self):
        if not isinstance(self.stock_product, StockProduct):
            raise ValueError("Stock product must be a StockProduct instance")
        if not isinstance(self.movement_type, MovementType):
            raise ValueError("Movement type must be a MovementType enum")
        if self.quantity is not None and (not isinstance(self.quantity, int) or self.quantity <= 0):
            raise ValueError("Quantity must be a positive integer when provided")
        
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "stock_product": self.stock_product.to_dict(),
            "movement_type": self.movement_type.value,
            "quantity": self.quantity,
            "date": self.date.isoformat() if self.date else None
        }
    
    @staticmethod
    def from_dict(data: dict) -> StockMovement:
        stock_product_data = data.get("stock_product")
        movement_type_data = data.get("movement_type")
        
        if isinstance(movement_type_data, str):
            movement_type = MovementType(movement_type_data)
        elif isinstance(movement_type_data, MovementType):
            movement_type = movement_type_data
        else:
            movement_type = movement_type_data
        
        return StockMovement(
            id=data.get("id"),
            stock_product=StockProduct.from_dict(stock_product_data) if isinstance(stock_product_data, dict) else stock_product_data,
            movement_type=movement_type,
            quantity=int(data.get("quantity")) if data.get("quantity") is not None else None,
            date=datetime.fromisoformat(data.get("date")) if data.get("date") else None
        )

