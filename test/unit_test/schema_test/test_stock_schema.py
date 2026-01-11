import pytest
from pydantic import ValidationError
from schema.stock_schema import (
    CreateStockProductRequest,
    UpdateStockProductRequest,
    AdjustStockRequest,
    CreateStockMovementRequest,
    StockProductResponse
)
from utils.enum import MovementType
from decimal import Decimal
from uuid import uuid4
from datetime import datetime

class TestCreateStockProductRequest:
    """Testes para CreateStockProductRequest"""
    
    def test_create_stock_product_request_valid(self):
        """Deve criar stock product request válido"""
        data = {
            "establishment_id": uuid4(),
            "product_name": "Shampoo",
            "quantity": 50,
            "price": Decimal("25.90")
        }
        product = CreateStockProductRequest(**data)
        assert product.product_name == "Shampoo"
        assert product.quantity == 50
        assert product.price == Decimal("25.90")
    
    def test_create_stock_product_request_without_price(self):
        """Deve aceitar sem preço"""
        data = {
            "establishment_id": uuid4(),
            "product_name": "Condicionador",
            "quantity": 30
        }
        product = CreateStockProductRequest(**data)
        assert product.price is None
    
    def test_create_stock_product_request_quantity_negative_fails(self):
        """Deve falhar com quantidade negativa"""
        data = {
            "establishment_id": uuid4(),
            "product_name": "Produto",
            "quantity": -1
        }
        with pytest.raises(ValidationError) as exc:
            CreateStockProductRequest(**data)
        assert "Quantity cannot be negative" in str(exc.value)
    
    def test_create_stock_product_request_price_negative_fails(self):
        """Deve falhar com preço negativo"""
        data = {
            "establishment_id": uuid4(),
            "product_name": "Produto",
            "quantity": 10,
            "price": Decimal("-5")
        }
        with pytest.raises(ValidationError) as exc:
            CreateStockProductRequest(**data)
        assert "Price cannot be negative" in str(exc.value)

class TestUpdateStockProductRequest:
    """Testes para UpdateStockProductRequest"""
    
    def test_update_stock_product_request_valid(self):
        """Deve atualizar stock product"""
        data = {
            "product_name": "Novo Nome",
            "quantity": 100,
            "price": Decimal("30.00")
        }
        update = UpdateStockProductRequest(**data)
        assert update.product_name == "Novo Nome"
        assert update.quantity == 100
    
    def test_update_stock_product_request_partial(self):
        """Deve aceitar atualização parcial"""
        data = {"quantity": 75}
        update = UpdateStockProductRequest(**data)
        assert update.quantity == 75
        assert update.product_name is None
    
    def test_update_stock_product_request_quantity_negative_fails(self):
        """Deve falhar com quantidade negativa"""
        data = {"quantity": -10}
        with pytest.raises(ValidationError):
            UpdateStockProductRequest(**data)

class TestAdjustStockRequest:
    """Testes para AdjustStockRequest"""
    
    def test_adjust_stock_request_valid(self):
        """Deve criar adjust request válido"""
        data = {"quantity": 20}
        adjust = AdjustStockRequest(**data)
        assert adjust.quantity == 20
    
    def test_adjust_stock_request_zero_fails(self):
        """Deve falhar com quantidade zero"""
        data = {"quantity": 0}
        with pytest.raises(ValidationError) as exc:
            AdjustStockRequest(**data)
        assert "Quantity must be positive" in str(exc.value)
    
    def test_adjust_stock_request_negative_fails(self):
        """Deve falhar com quantidade negativa"""
        data = {"quantity": -5}
        with pytest.raises(ValidationError):
            AdjustStockRequest(**data)

class TestCreateStockMovementRequest:
    """Testes para CreateStockMovementRequest"""
    
    def test_create_stock_movement_request_input_valid(self):
        """Deve criar movement request de entrada válido"""
        data = {
            "stock_product_id": 1,
            "movement_type": MovementType.INPUT,
            "quantity": 50
        }
        movement = CreateStockMovementRequest(**data)
        assert movement.movement_type == MovementType.INPUT
        assert movement.quantity == 50
    
    def test_create_stock_movement_request_output_valid(self):
        """Deve criar movement request de saída válido"""
        data = {
            "stock_product_id": 1,
            "movement_type": MovementType.OUTPUT,
            "quantity": 10
        }
        movement = CreateStockMovementRequest(**data)
        assert movement.movement_type == MovementType.OUTPUT
        assert movement.quantity == 10
    
    def test_create_stock_movement_request_quantity_zero_fails(self):
        """Deve falhar com quantidade zero"""
        data = {
            "stock_product_id": 1,
            "movement_type": MovementType.INPUT,
            "quantity": 0
        }
        with pytest.raises(ValidationError) as exc:
            CreateStockMovementRequest(**data)
        assert "Quantity must be positive" in str(exc.value)
    
    def test_create_stock_movement_request_quantity_negative_fails(self):
        """Deve falhar com quantidade negativa"""
        data = {
            "stock_product_id": 1,
            "movement_type": MovementType.INPUT,
            "quantity": -5
        }
        with pytest.raises(ValidationError):
            CreateStockMovementRequest(**data)

class TestStockProductResponse:
    """Testes para StockProductResponse"""
    
    def test_stock_product_response_valid(self):
        """Deve criar response válido"""
        establishment_id = uuid4()
        data = {
            "id": 1,
            "establishment_id": establishment_id,
            "product_name": "Shampoo",
            "quantity": 50,
            "price": "25.90",
            "is_available": True
        }
        response = StockProductResponse(**data)
        assert response.id == 1
        assert response.product_name == "Shampoo"
        assert response.is_available == True
