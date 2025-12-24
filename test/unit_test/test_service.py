import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from domain.entities import Service
from domain.entities import Establishment
from domain.entities import Client
from domain.entities import User
from domain.entities import Plan
from utils.enum import UserRole, TypePlan


class TestServiceEntity:
    """Testes unitários para a entidade Service"""
    
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
    
    def test_create_service_with_valid_data(self, mock_establishment):
        """Testa criação de serviço com dados válidos"""
        service = Service(
            id="srv-123",
            establishment=mock_establishment,
            service_name="Corte de Cabelo",
            time_duration=30,
            price=Decimal("35.00"),
            description_service="Corte masculino tradicional",
            active=True
        )
        
        assert service.service_name == "Corte de Cabelo"
        assert service.time_duration == 30
        assert service.price == Decimal("35.00")
        assert service.active is True
    
    def test_create_service_with_invalid_establishment_raises_error(self):
        """Testa que establishment inválido levanta erro"""
        with pytest.raises(ValueError, match="Establishment must be an Establishment instance"):
            Service(
                id="srv-123",
                establishment="invalid",
                service_name="Corte de Cabelo",
                time_duration=30,
                price=Decimal("35.00"),
                description_service=None,
                active=True
            )
    
    def test_create_service_with_invalid_name_raises_error(self, mock_establishment):
        """Testa que nome inválido levanta erro"""
        with pytest.raises(ValueError, match="Service name must be a string"):
            Service(
                id="srv-123",
                establishment=mock_establishment,
                service_name=123,
                time_duration=30,
                price=Decimal("35.00"),
                description_service=None,
                active=True
            )
    
    def test_create_service_with_zero_duration_raises_error(self, mock_establishment):
        """Testa que duração zero levanta erro"""
        with pytest.raises(ValueError, match="Time duration must be a positive integer"):
            Service(
                id="srv-123",
                establishment=mock_establishment,
                service_name="Corte de Cabelo",
                time_duration=0,
                price=Decimal("35.00"),
                description_service=None,
                active=True
            )
    
    def test_create_service_with_negative_duration_raises_error(self, mock_establishment):
        """Testa que duração negativa levanta erro"""
        with pytest.raises(ValueError, match="Time duration must be a positive integer"):
            Service(
                id="srv-123",
                establishment=mock_establishment,
                service_name="Corte de Cabelo",
                time_duration=-30,
                price=Decimal("35.00"),
                description_service=None,
                active=True
            )
    
    def test_create_service_with_negative_price_raises_error(self, mock_establishment):
        """Testa que preço negativo levanta erro"""
        with pytest.raises(ValueError, match="Price must be a non-negative Decimal"):
            Service(
                id="srv-123",
                establishment=mock_establishment,
                service_name="Corte de Cabelo",
                time_duration=30,
                price=Decimal("-35.00"),
                description_service=None,
                active=True
            )
    
    def test_create_service_with_none_price_is_valid(self, mock_establishment):
        """Testa que preço None é válido (serviço gratuito)"""
        service = Service(
            id="srv-123",
            establishment=mock_establishment,
            service_name="Consulta Gratuita",
            time_duration=15,
            price=None,
            description_service=None,
            active=True
        )
        
        assert service.price is None
    
    def test_is_active_returns_true_when_active(self, mock_establishment):
        """Testa is_active() retorna True quando ativo"""
        service = Service(
            id="srv-123",
            establishment=mock_establishment,
            service_name="Corte de Cabelo",
            time_duration=30,
            price=Decimal("35.00"),
            description_service=None,
            active=True
        )
        
        assert service.is_active() is True
    
    def test_is_active_returns_false_when_inactive(self, mock_establishment):
        """Testa is_active() retorna False quando inativo"""
        service = Service(
            id="srv-123",
            establishment=mock_establishment,
            service_name="Corte de Cabelo",
            time_duration=30,
            price=Decimal("35.00"),
            description_service=None,
            active=False
        )
        
        assert service.is_active() is False
    
    def test_is_active_returns_false_when_none(self, mock_establishment):
        """Testa is_active() retorna False quando None"""
        service = Service(
            id="srv-123",
            establishment=mock_establishment,
            service_name="Corte de Cabelo",
            time_duration=30,
            price=Decimal("35.00"),
            description_service=None,
            active=None
        )
        
        assert service.is_active() is False
    
    def test_activate_sets_status_to_true(self, mock_establishment):
        """Testa activate() define active como True"""
        service = Service(
            id="srv-123",
            establishment=mock_establishment,
            service_name="Corte de Cabelo",
            time_duration=30,
            price=Decimal("35.00"),
            description_service=None,
            active=False
        )
        
        service.activate()
        
        assert service.active is True
    
    def test_deactivate_sets_status_to_false(self, mock_establishment):
        """Testa deactivate() define active como False"""
        service = Service(
            id="srv-123",
            establishment=mock_establishment,
            service_name="Corte de Cabelo",
            time_duration=30,
            price=Decimal("35.00"),
            description_service=None,
            active=True
        )
        
        service.deactivate()
        
        assert service.active is False
    
    def test_calculate_end_time_adds_duration_correctly(self, mock_establishment):
        """Testa calculate_end_time() adiciona duração corretamente"""
        service = Service(
            id="srv-123",
            establishment=mock_establishment,
            service_name="Corte de Cabelo",
            time_duration=30,
            price=Decimal("35.00"),
            description_service=None,
            active=True
        )
        
        start_time = datetime(2025, 12, 24, 10, 0, 0)
        end_time = service.calculate_end_time(start_time)
        
        expected_end = datetime(2025, 12, 24, 10, 30, 0)
        assert end_time == expected_end
    
    def test_calculate_end_time_with_60_minutes(self, mock_establishment):
        """Testa calculate_end_time() com 60 minutos"""
        service = Service(
            id="srv-123",
            establishment=mock_establishment,
            service_name="Corte + Barba",
            time_duration=60,
            price=Decimal("50.00"),
            description_service=None,
            active=True
        )
        
        start_time = datetime(2025, 12, 24, 14, 0, 0)
        end_time = service.calculate_end_time(start_time)
        
        expected_end = datetime(2025, 12, 24, 15, 0, 0)
        assert end_time == expected_end
    
    def test_calculate_end_time_with_invalid_start_raises_error(self, mock_establishment):
        """Testa calculate_end_time() com start_time inválido levanta erro"""
        service = Service(
            id="srv-123",
            establishment=mock_establishment,
            service_name="Corte de Cabelo",
            time_duration=30,
            price=Decimal("35.00"),
            description_service=None,
            active=True
        )
        
        with pytest.raises(ValueError, match="start_time must be a datetime"):
            service.calculate_end_time("invalid")
    
    def test_to_dict_returns_correct_structure(self, mock_establishment):
        """Testa to_dict() retorna estrutura correta"""
        service = Service(
            id="srv-123",
            establishment=mock_establishment,
            service_name="Corte de Cabelo",
            time_duration=30,
            price=Decimal("35.00"),
            description_service="Corte masculino",
            active=True
        )
        
        service_dict = service.to_dict()
        
        assert service_dict["id"] == "srv-123"
        assert service_dict["service_name"] == "Corte de Cabelo"
        assert service_dict["time_duration"] == 30
        assert service_dict["price"] == "35.00"
        assert service_dict["active"] is True
    
    def test_from_dict_creates_service_correctly(self, mock_establishment):
        """Testa from_dict() cria serviço corretamente"""
        data = {
            "id": "srv-456",
            "establishment": mock_establishment,
            "service_name": "Barba",
            "time_duration": 20,
            "price": "25.00",
            "description_service": "Aparar barba",
            "active": True
        }
        
        service = Service.from_dict(data)
        
        assert service.id == "srv-456"
        assert service.service_name == "Barba"
        assert service.time_duration == 20
        assert service.price == Decimal("25.00")
