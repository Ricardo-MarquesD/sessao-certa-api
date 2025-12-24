import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from domain.entities import Customer
from domain.entities import Establishment
from domain.entities import Client
from domain.entities import User
from domain.entities import Plan
from utils.enum import UserRole, TypePlan


class TestCustomerEntity:
    """Testes unitários para a entidade Customer"""
    
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
            id=1,
            type_plan=TypePlan.BRONZE,
            basic_price=Decimal("29.90"),
            max_employee=5,
            allow_stock=False,
            allow_advanced_analysis=False
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
    
    def test_create_customer_with_valid_data(self, mock_establishment):
        """Testa criação de customer com dados válidos"""
        customer = Customer(
            id="cust-123",
            establishment=mock_establishment,
            customer_name="Carlos Souza",
            phone_number="11999887766"
        )
        
        assert customer.customer_name == "Carlos Souza"
        assert customer.phone_number == "11999887766"
    
    def test_create_customer_with_invalid_establishment_raises_error(self):
        """Testa que establishment inválido levanta erro"""
        with pytest.raises(ValueError, match="Establishment must be a Establishment instance"):
            Customer(
                id="cust-123",
                establishment="invalid",
                customer_name="Carlos Souza",
                phone_number="11999887766"
            )
    
    def test_create_customer_with_invalid_name_raises_error(self, mock_establishment):
        """Testa que nome inválido levanta erro"""
        with pytest.raises(ValueError, match="Customer name must be a string"):
            Customer(
                id="cust-123",
                establishment=mock_establishment,
                customer_name=123,
                phone_number="11999887766"
            )
    
    def test_create_customer_with_short_phone_raises_error(self, mock_establishment):
        """Testa que telefone muito curto levanta erro"""
        with pytest.raises(ValueError, match="Phone Number is incorrect, is too short"):
            Customer(
                id="cust-123",
                establishment=mock_establishment,
                customer_name="Carlos Souza",
                phone_number="123"
            )
    
    def test_create_customer_with_valid_short_phone(self, mock_establishment):
        """Testa que telefone com 8 caracteres é válido"""
        customer = Customer(
            id="cust-123",
            establishment=mock_establishment,
            customer_name="Carlos Souza",
            phone_number="12345678"
        )
        
        assert customer.phone_number == "12345678"
    
    def test_to_dict_returns_correct_structure(self, mock_establishment):
        """Testa to_dict() retorna estrutura correta"""
        customer = Customer(
            id="cust-123",
            establishment=mock_establishment,
            customer_name="Carlos Souza",
            phone_number="11999887766"
        )
        
        customer_dict = customer.to_dict()
        
        assert customer_dict["id"] == "cust-123"
        assert customer_dict["customer_name"] == "Carlos Souza"
        assert customer_dict["phone_number"] == "11999887766"
        assert "establishment" in customer_dict
    
    def test_from_dict_creates_customer_correctly(self, mock_establishment):
        """Testa from_dict() cria customer corretamente"""
        data = {
            "id": "cust-456",
            "establishment": mock_establishment,
            "customer_name": "Ana Paula",
            "phone_number": "11988776655"
        }
        
        customer = Customer.from_dict(data)
        
        assert customer.id == "cust-456"
        assert customer.customer_name == "Ana Paula"
        assert customer.phone_number == "11988776655"
    
    def test_from_dict_with_establishment_dict(self):
        """Testa from_dict() com establishment como dicionário"""
        user_data = {
            "id": "user-123",
            "user_name": "João Silva",
            "email": "joao@example.com",
            "phone_number": "11987654321",
            "password_hash": "$2b$12$hashedpassword",
            "role": "CLIENT",
            "active_status": True,
            "img_url": None,
            "created_at": None,
            "updated_at": None
        }
        
        plan_data = {
            "id": 1,
            "type_plan": "BRONZE",
            "basic_price": "29.90",
            "max_employee": 5,
            "allow_stock": False,
            "allow_advanced_analysis": False
        }
        
        client_data = {
            "id": 1,
            "user": user_data,
            "plan": plan_data
        }
        
        establishment_data = {
            "id": "est-789",
            "client": client_data,
            "establishment_name": "Salão Teste",
            "cnpj": "98765432109876",
            "chatbot_phone_number": "11987654321",
            "address": "Rua Teste, 456",
            "img_url": None,
            "subscription_date": "2025-12-01 10:00:00",
            "due_date": "2025-12-31 23:59:59",
            "trial_active": False
        }
        
        data = {
            "id": "cust-789",
            "establishment": establishment_data,
            "customer_name": "Roberto Lima",
            "phone_number": "11977665544"
        }
        
        customer = Customer.from_dict(data)
        
        assert customer.id == "cust-789"
        assert customer.customer_name == "Roberto Lima"
        assert customer.establishment.establishment_name == "Salão Teste"
