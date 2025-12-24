import pytest
from decimal import Decimal
from domain.entities import Employee
from domain.entities import User
from domain.entities import Establishment
from domain.entities import Client
from domain.entities import Plan
from utils.enum import UserRole, TypePlan
from datetime import datetime, timedelta


class TestEmployeeEntity:
    """Testes unitários para a entidade Employee"""
    
    @pytest.fixture
    def mock_user(self):
        """Fixture para criar um user de teste"""
        return User(
            id="user-emp-123",
            user_name="Maria Silva",
            email="maria@example.com",
            phone_number="11987654321",
            password_hash="$2b$12$hashedpassword",
            role=UserRole.EMPLOYEE,
            active_status=True,
            img_url=None,
            created_at=None,
            updated_at=None
        )
    
    @pytest.fixture
    def mock_establishment(self):
        """Fixture para criar um establishment de teste"""
        user = User(
            id="user-client-123",
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
    
    def test_create_employee_with_valid_data(self, mock_user, mock_establishment):
        """Testa criação de employee com dados válidos"""
        employee = Employee(
            id="emp-123",
            user=mock_user,
            establishment=mock_establishment,
            percentage_commission=Decimal("10.00"),
            available_hours={"monday": ["09:00-18:00"]}
        )
        
        assert employee.user.user_name == "Maria Silva"
        assert employee.percentage_commission == Decimal("10.00")
    
    def test_create_employee_with_invalid_user_raises_error(self, mock_establishment):
        """Testa que user inválido levanta erro"""
        with pytest.raises(ValueError, match="User must be a User instance"):
            Employee(
                id="emp-123",
                user="invalid",
                establishment=mock_establishment,
                percentage_commission=Decimal("10.00"),
                available_hours=None
            )
    
    def test_create_employee_with_invalid_establishment_raises_error(self, mock_user):
        """Testa que establishment inválido levanta erro"""
        with pytest.raises(ValueError, match="Establishment must be a Establishment instance"):
            Employee(
                id="emp-123",
                user=mock_user,
                establishment="invalid",
                percentage_commission=Decimal("10.00"),
                available_hours=None
            )
    
    def test_commission_calculates_correctly_with_10_percent(self, mock_user, mock_establishment):
        """Testa commission() calcula corretamente com 10%"""
        employee = Employee(
            id="emp-123",
            user=mock_user,
            establishment=mock_establishment,
            percentage_commission=Decimal("10.00"),
            available_hours=None
        )
        
        # 10% de R$100,00 = R$10,00
        commission = employee.commission(Decimal("100.00"))
        assert commission == Decimal("10.00")
    
    def test_commission_calculates_correctly_with_15_percent(self, mock_user, mock_establishment):
        """Testa commission() calcula corretamente com 15%"""
        employee = Employee(
            id="emp-123",
            user=mock_user,
            establishment=mock_establishment,
            percentage_commission=Decimal("15.00"),
            available_hours=None
        )
        
        # 15% de R$50,00 = R$7,50
        commission = employee.commission(Decimal("50.00"))
        assert commission == Decimal("7.50")
    
    def test_commission_returns_zero_when_percentage_is_none(self, mock_user, mock_establishment):
        """Testa commission() retorna 0 quando percentage_commission é None"""
        employee = Employee(
            id="emp-123",
            user=mock_user,
            establishment=mock_establishment,
            percentage_commission=None,
            available_hours=None
        )
        
        commission = employee.commission(Decimal("100.00"))
        assert commission == Decimal("0.00")
    
    def test_commission_with_high_service_price(self, mock_user, mock_establishment):
        """Testa commission() com preço alto"""
        employee = Employee(
            id="emp-123",
            user=mock_user,
            establishment=mock_establishment,
            percentage_commission=Decimal("20.00"),
            available_hours=None
        )
        
        # 20% de R$500,00 = R$100,00
        commission = employee.commission(Decimal("500.00"))
        assert commission == Decimal("100.00")
    
    def test_to_dict_returns_correct_structure(self, mock_user, mock_establishment):
        """Testa to_dict() retorna estrutura correta"""
        employee = Employee(
            id="emp-123",
            user=mock_user,
            establishment=mock_establishment,
            percentage_commission=Decimal("10.00"),
            available_hours={"monday": ["09:00-18:00"]}
        )
        
        emp_dict = employee.to_dict()
        
        assert emp_dict["id"] == "emp-123"
        assert emp_dict["percentage_commission"] == "10.00"
        assert "user" in emp_dict
        assert "establishment" in emp_dict
    
    def test_to_dict_with_none_commission(self, mock_user, mock_establishment):
        """Testa to_dict() com percentage_commission None"""
        employee = Employee(
            id="emp-123",
            user=mock_user,
            establishment=mock_establishment,
            percentage_commission=None,
            available_hours=None
        )
        
        emp_dict = employee.to_dict()
        
        assert emp_dict["percentage_commission"] is None
    
    def test_from_dict_creates_employee_correctly(self, mock_user, mock_establishment):
        """Testa from_dict() cria employee corretamente"""
        data = {
            "id": "emp-456",
            "user": mock_user,
            "establishment": mock_establishment,
            "percentage_commission": "12.50",
            "available_hours": {"tuesday": ["10:00-19:00"]}
        }
        
        employee = Employee.from_dict(data)
        
        assert employee.id == "emp-456"
        assert employee.percentage_commission == "12.50"
        assert employee.available_hours["tuesday"] == ["10:00-19:00"]
