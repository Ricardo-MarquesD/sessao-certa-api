import pytest
from decimal import Decimal
from domain.entities import Client
from domain.entities import User
from domain.entities import Plan
from utils.enum import UserRole, TypePlan


class TestClientEntity:
    """Testes unitários para a entidade Client"""
    
    @pytest.fixture
    def mock_user(self):
        """Fixture para criar um user de teste"""
        return User(
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
    
    @pytest.fixture
    def mock_plan(self):
        """Fixture para criar um plan de teste"""
        return Plan(
            id=1,
            type_plan=TypePlan.BRONZE,
            basic_price=Decimal("29.90"),
            max_employee=5,
            allow_stock=False,
            allow_advanced_analysis=False
        )
    
    def test_create_client_with_valid_data(self, mock_user, mock_plan):
        """Testa criação de client com dados válidos"""
        client = Client(
            id=1,
            user=mock_user,
            plan=mock_plan
        )
        
        assert client.id == 1
        assert client.user.user_name == "João Silva"
        assert client.plan.type_plan == TypePlan.BRONZE
    
    def test_create_client_with_invalid_user_raises_error(self, mock_plan):
        """Testa que user inválido levanta erro"""
        with pytest.raises(ValueError, match="User must be a User instance"):
            Client(
                id=1,
                user="invalid",
                plan=mock_plan
            )
    
    def test_create_client_with_invalid_plan_raises_error(self, mock_user):
        """Testa que plan inválido levanta erro"""
        with pytest.raises(ValueError, match="Plan must be a Plan instance"):
            Client(
                id=1,
                user=mock_user,
                plan="invalid"
            )
    
    def test_to_dict_returns_correct_structure(self, mock_user, mock_plan):
        """Testa to_dict() retorna estrutura correta"""
        client = Client(
            id=1,
            user=mock_user,
            plan=mock_plan
        )
        
        client_dict = client.to_dict()
        
        assert client_dict["id"] == 1
        assert "user" in client_dict
        assert "plan" in client_dict
        assert client_dict["user"]["user_name"] == "João Silva"
        assert client_dict["plan"]["type_plan"] == "BRONZE"
    
    def test_from_dict_creates_client_correctly(self, mock_user, mock_plan):
        """Testa from_dict() cria client corretamente"""
        data = {
            "id": 2,
            "user": mock_user,
            "plan": mock_plan
        }
        
        client = Client.from_dict(data)
        
        assert client.id == 2
        assert client.user.user_name == "João Silva"
        assert client.plan.type_plan == TypePlan.BRONZE
    
    def test_from_dict_with_user_dict(self, mock_plan):
        """Testa from_dict() com user como dicionário"""
        user_data = {
            "id": "user-456",
            "user_name": "Maria Silva",
            "email": "maria@example.com",
            "phone_number": "11999887766",
            "password_hash": "$2b$12$hashedpassword",
            "role": "CLIENT",
            "active_status": True,
            "img_url": None,
            "created_at": None,
            "updated_at": None
        }
        
        data = {
            "id": 3,
            "user": user_data,
            "plan": mock_plan
        }
        
        client = Client.from_dict(data)
        
        assert client.id == 3
        assert client.user.user_name == "Maria Silva"
        assert client.user.email == "maria@example.com"
    
    def test_from_dict_with_plan_dict(self, mock_user):
        """Testa from_dict() com plan como dicionário"""
        plan_data = {
            "id": 2,
            "type_plan": "SILVER",
            "basic_price": "59.90",
            "max_employee": 10,
            "allow_stock": False,
            "allow_advanced_analysis": True
        }
        
        data = {
            "id": 4,
            "user": mock_user,
            "plan": plan_data
        }
        
        client = Client.from_dict(data)
        
        assert client.id == 4
        assert client.plan.type_plan == TypePlan.SILVER
        assert client.plan.basic_price == Decimal("59.90")
