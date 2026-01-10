from pydantic import BaseModel, field_validator
from decimal import Decimal
from domain.entities import StockProduct, StockMovement
from utils.enum import MovementType
from datetime import datetime
from uuid import UUID
from schema.establishment_schema import EstablishmentResponse

class _StockProductBase(BaseModel):
    product_name: str
    quantity: int
    price: Decimal | None = None
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v < 0:
            raise ValueError('Quantity cannot be negative')
        return v
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v is not None and v < 0:
            raise ValueError('Price cannot be negative')
        return v

class CreateStockProductRequest(_StockProductBase):
    establishment_id: UUID

class UpdateStockProductRequest(BaseModel):
    product_name: str | None = None
    quantity: int | None = None
    price: Decimal | None = None
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v is not None and v < 0:
            raise ValueError('Quantity cannot be negative')
        return v
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v is not None and v < 0:
            raise ValueError('Price cannot be negative')
        return v

class StockProductResponse(BaseModel):
    id: int
    establishment_id: UUID
    product_name: str
    quantity: int
    price: str | None
    is_available: bool
    
    @classmethod
    def from_entity(cls, product: StockProduct) -> StockProductResponse:
        return cls(
            id=product.id,
            establishment_id=product.establishment.id,
            product_name=product.product_name,
            quantity=product.quantity,
            price=str(product.price) if product.price else None,
            is_available=product.is_available()
        )

class StockProductDetailResponse(BaseModel):
    id: int
    establishment: EstablishmentResponse
    product_name: str
    quantity: int
    price: str | None
    is_available: bool
    
    @classmethod
    def from_entity(cls, product: StockProduct) -> StockProductDetailResponse:
        return cls(
            id=product.id,
            establishment=EstablishmentResponse.from_entity(product.establishment),
            product_name=product.product_name,
            quantity=product.quantity,
            price=str(product.price) if product.price else None,
            is_available=product.is_available()
        )

class AdjustStockRequest(BaseModel):
    quantity: int
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v
    
class CreateStockMovementRequest(BaseModel):
    stock_product_id: int
    movement_type: MovementType
    quantity: int
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v

class StockMovementResponse(BaseModel):
    id: int
    stock_product_id: int
    movement_type: str
    quantity: int
    date: datetime
    
    @classmethod
    def from_entity(cls, movement: StockMovement) -> StockMovementResponse:
        return cls(
            id=movement.id,
            stock_product_id=movement.stock_product.id,
            movement_type=movement.movement_type.value,
            quantity=movement.quantity,
            date=movement.date
        )

class StockMovementDetailResponse(BaseModel):
    id: int
    stock_product: StockProductResponse
    movement_type: str
    quantity: int
    date: datetime
    
    @classmethod
    def from_entity(cls, movement: StockMovement) -> StockMovementDetailResponse:
        return cls(
            id=movement.id,
            stock_product=StockProductResponse.from_entity(movement.stock_product),
            movement_type=movement.movement_type.value,
            quantity=movement.quantity,
            date=movement.date
        )