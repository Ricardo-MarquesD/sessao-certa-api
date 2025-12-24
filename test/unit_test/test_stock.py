import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from domain.entities import StockProduct, StockMovement
from domain.entities import Establishment
from domain.entities import Client
from domain.entities import User
from domain.entities import Plan
from utils.enum import UserRole, TypePlan, MovementType


class TestStockProductEntity:
    """Testes unitários para a entidade StockProduct"""
    
    @pytest.fixture
    def mock_establishment(self):
        """Fixture para criar um establishment de teste"""
        user = User(
            id="user-123",
            user_name="João Silva",
            email="joao@example.com",
            phone_number="11987654321",
            password_hash="$2b$12$hashedpassword",
            role=UserRole.CLIENT,
            active_status=True,
            img_url=None,
            created_at=None,
            updated_at=None
        )
        
        plan = Plan(
            id=3,
            type_plan=TypePlan.GOLD,
            basic_price=Decimal("99.90"),
            max_employee=20,
            allow_stock=True,
            allow_advanced_analysis=True
        )
        
        client = Client(
            id=1,
            user=user,
            plan=plan
        )
        
        establishment = Establishment(
            id="est-123",
            client=client,
            establishment_name="Barbearia João",
            cnpj="12345678901234",
            chatbot_phone_number="11987654321",
            address="Rua Teste, 123",
            img_url=None,
            subscription_date=datetime.now(),
            due_date=datetime.now() + timedelta(days=30),
            trial_active=False
        )
        
        return establishment
    
    def test_create_stock_product_with_valid_data(self, mock_establishment):
        """Testa criação de produto com dados válidos"""
        product = StockProduct(
            id=1,
            establishment=mock_establishment,
            product_name="Shampoo Profissional",
            quantity=50,
            price=Decimal("35.90")
        )
        
        assert product.product_name == "Shampoo Profissional"
        assert product.quantity == 50
        assert product.price == Decimal("35.90")
    
    def test_create_stock_product_with_invalid_establishment_raises_error(self):
        """Testa que establishment inválido levanta erro"""
        with pytest.raises(ValueError, match="Establishment must be an Establishment instance"):
            StockProduct(
                id=1,
                establishment="invalid",
                product_name="Shampoo",
                quantity=50,
                price=Decimal("35.90")
            )
    
    def test_create_stock_product_with_invalid_name_raises_error(self, mock_establishment):
        """Testa que nome inválido levanta erro"""
        with pytest.raises(ValueError, match="Product name must be a string"):
            StockProduct(
                id=1,
                establishment=mock_establishment,
                product_name=123,
                quantity=50,
                price=Decimal("35.90")
            )
    
    def test_create_stock_product_with_negative_quantity_raises_error(self, mock_establishment):
        """Testa que quantidade negativa levanta erro"""
        with pytest.raises(ValueError, match="Quantity must be a non-negative integer"):
            StockProduct(
                id=1,
                establishment=mock_establishment,
                product_name="Shampoo",
                quantity=-10,
                price=Decimal("35.90")
            )
    
    def test_create_stock_product_with_zero_quantity_is_valid(self, mock_establishment):
        """Testa que quantidade zero é válida"""
        product = StockProduct(
            id=1,
            establishment=mock_establishment,
            product_name="Shampoo",
            quantity=0,
            price=Decimal("35.90")
        )
        
        assert product.quantity == 0
    
    def test_is_available_returns_true_when_quantity_greater_than_zero(self, mock_establishment):
        """Testa is_available() retorna True quando quantidade > 0"""
        product = StockProduct(
            id=1,
            establishment=mock_establishment,
            product_name="Shampoo",
            quantity=10,
            price=Decimal("35.90")
        )
        
        assert product.is_available() is True
    
    def test_is_available_returns_false_when_quantity_is_zero(self, mock_establishment):
        """Testa is_available() retorna False quando quantidade = 0"""
        product = StockProduct(
            id=1,
            establishment=mock_establishment,
            product_name="Shampoo",
            quantity=0,
            price=Decimal("35.90")
        )
        
        assert product.is_available() is False
    
    def test_add_stock_increases_quantity(self, mock_establishment):
        """Testa add_stock() aumenta quantidade"""
        product = StockProduct(
            id=1,
            establishment=mock_establishment,
            product_name="Shampoo",
            quantity=10,
            price=Decimal("35.90")
        )
        
        product.add_stock(5)
        
        assert product.quantity == 15
    
    def test_add_stock_with_zero_raises_error(self, mock_establishment):
        """Testa add_stock() com zero levanta erro"""
        product = StockProduct(
            id=1,
            establishment=mock_establishment,
            product_name="Shampoo",
            quantity=10,
            price=Decimal("35.90")
        )
        
        with pytest.raises(ValueError, match="Quantity must be positive"):
            product.add_stock(0)
    
    def test_add_stock_with_negative_raises_error(self, mock_establishment):
        """Testa add_stock() com valor negativo levanta erro"""
        product = StockProduct(
            id=1,
            establishment=mock_establishment,
            product_name="Shampoo",
            quantity=10,
            price=Decimal("35.90")
        )
        
        with pytest.raises(ValueError, match="Quantity must be positive"):
            product.add_stock(-5)
    
    def test_remove_stock_decreases_quantity(self, mock_establishment):
        """Testa remove_stock() diminui quantidade"""
        product = StockProduct(
            id=1,
            establishment=mock_establishment,
            product_name="Shampoo",
            quantity=10,
            price=Decimal("35.90")
        )
        
        product.remove_stock(3)
        
        assert product.quantity == 7
    
    def test_remove_stock_with_insufficient_quantity_raises_error(self, mock_establishment):
        """Testa remove_stock() com estoque insuficiente levanta erro"""
        product = StockProduct(
            id=1,
            establishment=mock_establishment,
            product_name="Shampoo",
            quantity=5,
            price=Decimal("35.90")
        )
        
        with pytest.raises(ValueError, match="Insufficient stock"):
            product.remove_stock(10)
    
    def test_set_quantity_changes_quantity(self, mock_establishment):
        """Testa set_quantity() altera quantidade"""
        product = StockProduct(
            id=1,
            establishment=mock_establishment,
            product_name="Shampoo",
            quantity=10,
            price=Decimal("35.90")
        )
        
        product.set_quantity(25)
        
        assert product.quantity == 25
    
    def test_set_quantity_with_negative_raises_error(self, mock_establishment):
        """Testa set_quantity() com valor negativo levanta erro"""
        product = StockProduct(
            id=1,
            establishment=mock_establishment,
            product_name="Shampoo",
            quantity=10,
            price=Decimal("35.90")
        )
        
        with pytest.raises(ValueError, match="Quantity cannot be negative"):
            product.set_quantity(-5)
    
    def test_to_dict_returns_correct_structure(self, mock_establishment):
        """Testa to_dict() retorna estrutura correta"""
        product = StockProduct(
            id=1,
            establishment=mock_establishment,
            product_name="Shampoo",
            quantity=10,
            price=Decimal("35.90")
        )
        
        product_dict = product.to_dict()
        
        assert product_dict["id"] == 1
        assert product_dict["product_name"] == "Shampoo"
        assert product_dict["quantity"] == 10
        assert product_dict["price"] == "35.90"


class TestStockMovementEntity:
    """Testes unitários para a entidade StockMovement"""
    
    @pytest.fixture
    def mock_stock_product(self):
        """Fixture para criar um stock product de teste"""
        user = User(
            id="user-123",
            user_name="João Silva",
            email="joao@example.com",
            phone_number="11987654321",
            password_hash="$2b$12$hashedpassword",
            role=UserRole.CLIENT,
            active_status=True,
            img_url=None,
            created_at=None,
            updated_at=None
        )
        
        plan = Plan(
            id=3,
            type_plan=TypePlan.GOLD,
            basic_price=Decimal("99.90"),
            max_employee=20,
            allow_stock=True,
            allow_advanced_analysis=True
        )
        
        client = Client(
            id=1,
            user=user,
            plan=plan
        )
        
        establishment = Establishment(
            id="est-123",
            client=client,
            establishment_name="Barbearia João",
            cnpj="12345678901234",
            chatbot_phone_number="11987654321",
            address="Rua Teste, 123",
            img_url=None,
            subscription_date=datetime.now(),
            due_date=datetime.now() + timedelta(days=30),
            trial_active=False
        )
        
        return StockProduct(
            id=1,
            establishment=establishment,
            product_name="Shampoo",
            quantity=10,
            price=Decimal("35.90")
        )
    
    def test_create_movement_with_valid_data(self, mock_stock_product):
        """Testa criação de movimento com dados válidos"""
        movement = StockMovement(
            id=1,
            stock_product=mock_stock_product,
            movement_type=MovementType.INPUT,
            quantity=5,
            date=datetime.now()
        )
        
        assert movement.movement_type == MovementType.INPUT
        assert movement.quantity == 5
    
    def test_create_movement_with_invalid_stock_product_raises_error(self):
        """Testa que stock_product inválido levanta erro"""
        with pytest.raises(ValueError, match="Stock product must be a StockProduct instance"):
            StockMovement(
                id=1,
                stock_product="invalid",
                movement_type=MovementType.INPUT,
                quantity=5,
                date=datetime.now()
            )
    
    def test_create_movement_with_invalid_type_raises_error(self, mock_stock_product):
        """Testa que movement_type inválido levanta erro"""
        with pytest.raises(ValueError, match="Movement type must be a MovementType enum"):
            StockMovement(
                id=1,
                stock_product=mock_stock_product,
                movement_type="INVALID",
                quantity=5,
                date=datetime.now()
            )
    
    def test_create_movement_with_zero_quantity_raises_error(self, mock_stock_product):
        """Testa que quantidade zero levanta erro"""
        with pytest.raises(ValueError, match="Quantity must be a positive integer"):
            StockMovement(
                id=1,
                stock_product=mock_stock_product,
                movement_type=MovementType.INPUT,
                quantity=0,
                date=datetime.now()
            )
    
    def test_is_input_returns_true_for_input_type(self, mock_stock_product):
        """Testa is_input() retorna True para tipo INPUT"""
        movement = StockMovement(
            id=1,
            stock_product=mock_stock_product,
            movement_type=MovementType.INPUT,
            quantity=5,
            date=datetime.now()
        )
        
        assert movement.is_input() is True
        assert movement.is_output() is False
    
    def test_is_output_returns_true_for_output_type(self, mock_stock_product):
        """Testa is_output() retorna True para tipo OUTPUT"""
        movement = StockMovement(
            id=1,
            stock_product=mock_stock_product,
            movement_type=MovementType.OUTPUT,
            quantity=3,
            date=datetime.now()
        )
        
        assert movement.is_output() is True
        assert movement.is_input() is False
    
    def test_apply_to_product_adds_stock_for_input(self, mock_stock_product):
        """Testa apply_to_product() adiciona estoque para INPUT"""
        initial_quantity = mock_stock_product.quantity
        
        movement = StockMovement(
            id=1,
            stock_product=mock_stock_product,
            movement_type=MovementType.INPUT,
            quantity=5,
            date=datetime.now()
        )
        
        movement.apply_to_product()
        
        assert mock_stock_product.quantity == initial_quantity + 5
    
    def test_apply_to_product_removes_stock_for_output(self, mock_stock_product):
        """Testa apply_to_product() remove estoque para OUTPUT"""
        initial_quantity = mock_stock_product.quantity
        
        movement = StockMovement(
            id=1,
            stock_product=mock_stock_product,
            movement_type=MovementType.OUTPUT,
            quantity=3,
            date=datetime.now()
        )
        
        movement.apply_to_product()
        
        assert mock_stock_product.quantity == initial_quantity - 3
    
    def test_apply_to_product_with_none_quantity_raises_error(self, mock_stock_product):
        """Testa apply_to_product() com quantity None levanta erro"""
        movement = StockMovement(
            id=1,
            stock_product=mock_stock_product,
            movement_type=MovementType.INPUT,
            quantity=None,
            date=datetime.now()
        )
        
        with pytest.raises(ValueError, match="Quantity must be set to apply movement"):
            movement.apply_to_product()
    
    def test_to_dict_returns_correct_structure(self, mock_stock_product):
        """Testa to_dict() retorna estrutura correta"""
        movement_date = datetime(2025, 12, 24, 10, 0, 0)
        movement = StockMovement(
            id=1,
            stock_product=mock_stock_product,
            movement_type=MovementType.INPUT,
            quantity=5,
            date=movement_date
        )
        
        movement_dict = movement.to_dict()
        
        assert movement_dict["id"] == 1
        assert movement_dict["movement_type"] == "INPUT"
        assert movement_dict["quantity"] == 5
