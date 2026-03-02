import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from domain.entities import Establishment
from domain.entities import Client
from domain.entities import User
from domain.entities import Plan
from utils.enum import UserRole, TypePlan


class TestEstablishmentEntity:
    """Testes unitários para a entidade Establishment"""
    
    @pytest.fixture
    def mock_client(self):
        """Fixture para criar um client de teste"""
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
        
        return Client(
            id=1,
            user=user,
            plan=plan
        )
    
    def test_create_establishment_with_valid_data(self, mock_client):
        """Testa criação de establishment com dados válidos"""
        establishment = Establishment(
            id="est-123",
            client=mock_client,
            stripe_subscription_id=None,
            waba_id="WABA-123",
            whatsapp_business_token="token-123",
            google_calendar_access_token=None,
            google_calendar_refresh_token=None,
            google_calendar_expiry=None,
            google_calendar_id=None,
            establishment_name="Barbearia João",
            cnpj="12345678901234",
            chatbot_phone_number="11987654321",
            address="Rua Teste, 123",
            img_url="https://example.com/img.jpg",
            subscription_date=datetime.now(),
            due_date=datetime.now() + timedelta(days=30),
            trial_active=False
        )
        
        assert establishment.establishment_name == "Barbearia João"
        assert establishment.cnpj == "12345678901234"
        assert establishment.trial_active is False
    
    def test_create_establishment_with_invalid_client_raises_error(self):
        """Testa que client inválido levanta erro"""
        with pytest.raises(ValueError, match="Client must be a Client instance"):
            Establishment(
                id="est-123",
                client="invalid",
                stripe_subscription_id=None,
                waba_id="WABA-123",
                whatsapp_business_token="token-123",
                google_calendar_access_token=None,
                google_calendar_refresh_token=None,
                google_calendar_expiry=None,
                google_calendar_id=None,
                establishment_name="Barbearia João",
                cnpj="12345678901234",
                chatbot_phone_number=None,
                address=None,
                img_url=None,
                subscription_date=None,
                due_date=None,
                trial_active=None
            )
    
    def test_create_establishment_with_short_cnpj_raises_error(self, mock_client):
        """Testa que CNPJ com menos de 14 caracteres levanta erro"""
        with pytest.raises(ValueError, match="CNPJ must be a string with 14 characters"):
            Establishment(
                id="est-123",
                client=mock_client,
                stripe_subscription_id=None,
                waba_id="WABA-123",
                whatsapp_business_token="token-123",
                google_calendar_access_token=None,
                google_calendar_refresh_token=None,
                google_calendar_expiry=None,
                google_calendar_id=None,
                establishment_name="Barbearia João",
                cnpj="123456789",
                chatbot_phone_number=None,
                address=None,
                img_url=None,
                subscription_date=None,
                due_date=None,
                trial_active=None
            )
    
    def test_create_establishment_with_long_cnpj_raises_error(self, mock_client):
        """Testa que CNPJ com mais de 14 caracteres levanta erro"""
        with pytest.raises(ValueError, match="CNPJ must be a string with 14 characters"):
            Establishment(
                id="est-123",
                client=mock_client,
                stripe_subscription_id=None,
                waba_id="WABA-123",
                whatsapp_business_token="token-123",
                google_calendar_access_token=None,
                google_calendar_refresh_token=None,
                google_calendar_expiry=None,
                google_calendar_id=None,
                establishment_name="Barbearia João",
                cnpj="123456789012345",
                chatbot_phone_number=None,
                address=None,
                img_url=None,
                subscription_date=None,
                due_date=None,
                trial_active=None
            )
    
    def test_is_trial_active_returns_true_when_active(self, mock_client):
        """Testa is_trial_active() retorna True quando trial ativo"""
        establishment = Establishment(
            id="est-123",
            client=mock_client,
            stripe_subscription_id=None,
            waba_id="WABA-123",
            whatsapp_business_token="token-123",
            google_calendar_access_token=None,
            google_calendar_refresh_token=None,
            google_calendar_expiry=None,
            google_calendar_id=None,
            establishment_name="Barbearia João",
            cnpj="12345678901234",
            chatbot_phone_number=None,
            address=None,
            img_url=None,
            subscription_date=None,
            due_date=None,
            trial_active=True
        )
        
        assert establishment.is_trial_active() is True
    
    def test_is_trial_active_returns_false_when_inactive(self, mock_client):
        """Testa is_trial_active() retorna False quando trial inativo"""
        establishment = Establishment(
            id="est-123",
            client=mock_client,
            stripe_subscription_id=None,
            waba_id="WABA-123",
            whatsapp_business_token="token-123",
            google_calendar_access_token=None,
            google_calendar_refresh_token=None,
            google_calendar_expiry=None,
            google_calendar_id=None,
            establishment_name="Barbearia João",
            cnpj="12345678901234",
            chatbot_phone_number=None,
            address=None,
            img_url=None,
            subscription_date=None,
            due_date=None,
            trial_active=False
        )
        
        assert establishment.is_trial_active() is False
    
    def test_is_trial_active_returns_false_when_none(self, mock_client):
        """Testa is_trial_active() retorna False quando None"""
        establishment = Establishment(
            id="est-123",
            client=mock_client,
            stripe_subscription_id=None,
            waba_id="WABA-123",
            whatsapp_business_token="token-123",
            google_calendar_access_token=None,
            google_calendar_refresh_token=None,
            google_calendar_expiry=None,
            google_calendar_id=None,
            establishment_name="Barbearia João",
            cnpj="12345678901234",
            chatbot_phone_number=None,
            address=None,
            img_url=None,
            subscription_date=None,
            due_date=None,
            trial_active=None
        )
        
        assert establishment.is_trial_active() is False
    
    def test_is_subscription_valid_returns_true_when_due_date_in_future(self, mock_client):
        """Testa is_subscription_valid() retorna True quando due_date no futuro"""
        establishment = Establishment(
            id="est-123",
            client=mock_client,
            stripe_subscription_id=None,
            waba_id="WABA-123",
            whatsapp_business_token="token-123",
            google_calendar_access_token=None,
            google_calendar_refresh_token=None,
            google_calendar_expiry=None,
            google_calendar_id=None,
            establishment_name="Barbearia João",
            cnpj="12345678901234",
            chatbot_phone_number=None,
            address=None,
            img_url=None,
            subscription_date=datetime.now(),
            due_date=datetime.now() + timedelta(days=30),
            trial_active=False
        )
        
        assert establishment.is_subscription_valid() is True
    
    def test_is_subscription_valid_returns_false_when_due_date_in_past(self, mock_client):
        """Testa is_subscription_valid() retorna False quando due_date no passado"""
        establishment = Establishment(
            id="est-123",
            client=mock_client,
            stripe_subscription_id=None,
            waba_id="WABA-123",
            whatsapp_business_token="token-123",
            google_calendar_access_token=None,
            google_calendar_refresh_token=None,
            google_calendar_expiry=None,
            google_calendar_id=None,
            establishment_name="Barbearia João",
            cnpj="12345678901234",
            chatbot_phone_number=None,
            address=None,
            img_url=None,
            subscription_date=datetime.now() - timedelta(days=60),
            due_date=datetime.now() - timedelta(days=30),
            trial_active=False
        )
        
        assert establishment.is_subscription_valid() is False
    
    def test_is_subscription_valid_returns_true_when_due_date_is_none(self, mock_client):
        """Testa is_subscription_valid() retorna True quando due_date é None"""
        establishment = Establishment(
            id="est-123",
            client=mock_client,
            stripe_subscription_id=None,
            waba_id="WABA-123",
            whatsapp_business_token="token-123",
            google_calendar_access_token=None,
            google_calendar_refresh_token=None,
            google_calendar_expiry=None,
            google_calendar_id=None,
            establishment_name="Barbearia João",
            cnpj="12345678901234",
            chatbot_phone_number=None,
            address=None,
            img_url=None,
            subscription_date=None,
            due_date=None,
            trial_active=True
        )
        
        assert establishment.is_subscription_valid() is True
    
    def test_time_until_due_returns_timedelta_when_due_date_set(self, mock_client):
        """Testa time_until_due() retorna timedelta quando due_date definido"""
        due_date = datetime.now() + timedelta(days=15)
        
        establishment = Establishment(
            id="est-123",
            client=mock_client,
            stripe_subscription_id=None,
            waba_id="WABA-123",
            whatsapp_business_token="token-123",
            google_calendar_access_token=None,
            google_calendar_refresh_token=None,
            google_calendar_expiry=None,
            google_calendar_id=None,
            establishment_name="Barbearia João",
            cnpj="12345678901234",
            chatbot_phone_number=None,
            address=None,
            img_url=None,
            subscription_date=datetime.now(),
            due_date=due_date,
            trial_active=False
        )
        
        time_until = establishment.time_until_due()
        
        assert time_until is not None
        assert isinstance(time_until, timedelta)
        # Deve ser próximo de 15 dias
        assert 14 <= time_until.days <= 16
    
    def test_time_until_due_returns_none_when_due_date_is_none(self, mock_client):
        """Testa time_until_due() retorna None quando due_date é None"""
        establishment = Establishment(
            id="est-123",
            client=mock_client,
            stripe_subscription_id=None,
            waba_id="WABA-123",
            whatsapp_business_token="token-123",
            google_calendar_access_token=None,
            google_calendar_refresh_token=None,
            google_calendar_expiry=None,
            google_calendar_id=None,
            establishment_name="Barbearia João",
            cnpj="12345678901234",
            chatbot_phone_number=None,
            address=None,
            img_url=None,
            subscription_date=None,
            due_date=None,
            trial_active=True
        )
        
        time_until = establishment.time_until_due()
        
        assert time_until is None
    
    def test_to_dict_returns_correct_structure(self, mock_client):
        """Testa to_dict() retorna estrutura correta"""
        subscription_date = datetime(2025, 12, 1, 10, 0, 0)
        due_date = datetime(2025, 12, 31, 23, 59, 59)
        
        establishment = Establishment(
            id="est-123",
            client=mock_client,
            stripe_subscription_id=None,
            waba_id="WABA-123",
            whatsapp_business_token="token-123",
            google_calendar_access_token=None,
            google_calendar_refresh_token=None,
            google_calendar_expiry=None,
            google_calendar_id=None,
            establishment_name="Barbearia João",
            cnpj="12345678901234",
            chatbot_phone_number="11987654321",
            address="Rua Teste, 123",
            img_url="https://example.com/img.jpg",
            subscription_date=subscription_date,
            due_date=due_date,
            trial_active=False
        )
        
        est_dict = establishment.to_dict()
        
        assert est_dict["id"] == "est-123"
        assert est_dict["establishment_name"] == "Barbearia João"
        assert est_dict["cnpj"] == "12345678901234"
        assert est_dict["trial_active"] is False
        assert "client" in est_dict
    
    def test_from_dict_creates_establishment_correctly(self, mock_client):
        """Testa from_dict() cria establishment corretamente"""
        data = {
            "id": "est-456",
            "client": mock_client,
            "stripe_subscription_id": None,
            "waba_id": "WABA-456",
            "whatsapp_business_token": "token-456",
            "google_calendar_access_token": None,
            "google_calendar_refresh_token": None,
            "google_calendar_expiry": None,
            "google_calendar_id": None,
            "establishment_name": "Salão Maria",
            "cnpj": "98765432109876",
            "chatbot_phone_number": "11999887766",
            "address": "Av. Principal, 456",
            "img_url": "https://example.com/img2.jpg",
            "subscription_date": "2025-12-01 10:00:00",
            "due_date": "2025-12-31 23:59:59",
            "trial_active": True
        }
        
        establishment = Establishment.from_dict(data)
        
        assert establishment.id == "est-456"
        assert establishment.establishment_name == "Salão Maria"
        assert establishment.cnpj == "98765432109876"
        assert establishment.trial_active is True
