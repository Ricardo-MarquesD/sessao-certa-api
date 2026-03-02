import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from domain.entities import Payment
from domain.entities import Establishment
from domain.entities import Client
from domain.entities import User
from domain.entities import Plan
from utils.enum import UserRole, TypePlan
from utils.enum import PaymentStatus, PaymentType


class TestPaymentEntity:
    """Testes unitários para a entidade Payment"""
    
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
            img_url=None,
            subscription_date=datetime.now(),
            due_date=datetime.now() + timedelta(days=30),
            trial_active=False
        )
        
        return establishment
    
    def test_create_payment_with_valid_data(self, mock_establishment):
        """Testa criação de payment com dados válidos"""
        payment = Payment(
            id="pay-123",
            establishment=mock_establishment,
            valor=Decimal("29.90"),
            payment_status=PaymentStatus.PENDING,
            payment_type=PaymentType.MONTHLY_SUBSCRIPTION,
            payment_day=datetime.now(),
            employee_quantity=5,
            gateway_transaction_id="txn-456"
        )
        
        assert payment.valor == Decimal("29.90")
        assert payment.payment_status == PaymentStatus.PENDING
        assert payment.payment_type == PaymentType.MONTHLY_SUBSCRIPTION
    
    def test_create_payment_with_invalid_establishment_raises_error(self):
        """Testa que establishment inválido levanta erro"""
        with pytest.raises(ValueError, match="Establishment must be an Establishment instance"):
            Payment(
                id="pay-123",
                establishment="invalid",
                valor=Decimal("29.90"),
                payment_status=PaymentStatus.PENDING,
                payment_type=PaymentType.MONTHLY_SUBSCRIPTION
            )
    
    def test_create_payment_with_zero_valor_raises_error(self, mock_establishment):
        """Testa que valor zero levanta erro"""
        with pytest.raises(ValueError, match="Valor must be a positive Decimal"):
            Payment(
                id="pay-123",
                establishment=mock_establishment,
                valor=Decimal("0"),
                payment_status=PaymentStatus.PENDING,
                payment_type=PaymentType.MONTHLY_SUBSCRIPTION
            )
    
    def test_create_payment_with_negative_valor_raises_error(self, mock_establishment):
        """Testa que valor negativo levanta erro"""
        with pytest.raises(ValueError, match="Valor must be a positive Decimal"):
            Payment(
                id="pay-123",
                establishment=mock_establishment,
                valor=Decimal("-29.90"),
                payment_status=PaymentStatus.PENDING,
                payment_type=PaymentType.MONTHLY_SUBSCRIPTION
            )
    
    def test_create_payment_with_invalid_status_raises_error(self, mock_establishment):
        """Testa que status inválido levanta erro"""
        with pytest.raises(ValueError, match="Payment status must be a PaymentStatus enum"):
            Payment(
                id="pay-123",
                establishment=mock_establishment,
                valor=Decimal("29.90"),
                payment_status="INVALID",
                payment_type=PaymentType.MONTHLY_SUBSCRIPTION
            )
    
    def test_create_payment_with_invalid_type_raises_error(self, mock_establishment):
        """Testa que type inválido levanta erro"""
        with pytest.raises(ValueError, match="Payment type must be a PaymentType enum"):
            Payment(
                id="pay-123",
                establishment=mock_establishment,
                valor=Decimal("29.90"),
                payment_status=PaymentStatus.PENDING,
                payment_type="INVALID"
            )
    
    def test_can_refund_returns_true_when_approved(self, mock_establishment):
        """Testa can_refund() retorna True quando aprovado"""
        payment = Payment(
            id="pay-123",
            establishment=mock_establishment,
            valor=Decimal("29.90"),
            payment_status=PaymentStatus.APPROVED,
            payment_type=PaymentType.MONTHLY_SUBSCRIPTION
        )
        
        assert payment.can_refund() is True
    
    def test_can_refund_returns_false_when_pending(self, mock_establishment):
        """Testa can_refund() retorna False quando pendente"""
        payment = Payment(
            id="pay-123",
            establishment=mock_establishment,
            valor=Decimal("29.90"),
            payment_status=PaymentStatus.PENDING,
            payment_type=PaymentType.MONTHLY_SUBSCRIPTION
        )
        
        assert payment.can_refund() is False
    
    def test_can_refund_returns_false_when_refused(self, mock_establishment):
        """Testa can_refund() retorna False quando recusado"""
        payment = Payment(
            id="pay-123",
            establishment=mock_establishment,
            valor=Decimal("29.90"),
            payment_status=PaymentStatus.REFUSED,
            payment_type=PaymentType.MONTHLY_SUBSCRIPTION
        )
        
        assert payment.can_refund() is False
    
    def test_can_approve_returns_true_when_pending(self, mock_establishment):
        """Testa can_approve() retorna True quando pendente"""
        payment = Payment(
            id="pay-123",
            establishment=mock_establishment,
            valor=Decimal("29.90"),
            payment_status=PaymentStatus.PENDING,
            payment_type=PaymentType.MONTHLY_SUBSCRIPTION
        )
        
        assert payment.can_approve() is True
    
    def test_can_approve_returns_false_when_approved(self, mock_establishment):
        """Testa can_approve() retorna False quando já aprovado"""
        payment = Payment(
            id="pay-123",
            establishment=mock_establishment,
            valor=Decimal("29.90"),
            payment_status=PaymentStatus.APPROVED,
            payment_type=PaymentType.MONTHLY_SUBSCRIPTION
        )
        
        assert payment.can_approve() is False
    
    def test_can_approve_returns_false_when_refused(self, mock_establishment):
        """Testa can_approve() retorna False quando recusado"""
        payment = Payment(
            id="pay-123",
            establishment=mock_establishment,
            valor=Decimal("29.90"),
            payment_status=PaymentStatus.REFUSED,
            payment_type=PaymentType.MONTHLY_SUBSCRIPTION
        )
        
        assert payment.can_approve() is False
    
    def test_can_refuse_returns_true_when_pending(self, mock_establishment):
        """Testa can_refuse() retorna True quando pendente"""
        payment = Payment(
            id="pay-123",
            establishment=mock_establishment,
            valor=Decimal("29.90"),
            payment_status=PaymentStatus.PENDING,
            payment_type=PaymentType.MONTHLY_SUBSCRIPTION
        )
        
        assert payment.can_refuse() is True
    
    def test_can_refuse_returns_false_when_approved(self, mock_establishment):
        """Testa can_refuse() retorna False quando aprovado"""
        payment = Payment(
            id="pay-123",
            establishment=mock_establishment,
            valor=Decimal("29.90"),
            payment_status=PaymentStatus.APPROVED,
            payment_type=PaymentType.MONTHLY_SUBSCRIPTION
        )
        
        assert payment.can_refuse() is False
    
    def test_to_dict_returns_correct_structure(self, mock_establishment):
        """Testa to_dict() retorna estrutura correta"""
        payment_day = datetime(2025, 12, 24, 10, 0, 0)
        payment = Payment(
            id="pay-123",
            establishment=mock_establishment,
            valor=Decimal("29.90"),
            payment_status=PaymentStatus.APPROVED,
            payment_type=PaymentType.MONTHLY_SUBSCRIPTION,
            payment_day=payment_day,
            employee_quantity=5,
            gateway_transaction_id="txn-456"
        )
        
        payment_dict = payment.to_dict()
        
        assert payment_dict["id"] == "pay-123"
        assert payment_dict["valor"] == "29.90"
        assert payment_dict["payment_status"] == "APPROVED"
        assert payment_dict["payment_type"] == "MONTHLY_SUBSCRIPTION"
        assert payment_dict["employee_quantity"] == 5
        assert payment_dict["gateway_transaction_id"] == "txn-456"
    
    def test_from_dict_creates_payment_correctly(self, mock_establishment):
        """Testa from_dict() cria payment corretamente"""
        data = {
            "id": "pay-456",
            "establishment": mock_establishment,
            "valor": "59.90",
            "payment_status": "PENDING",
            "payment_type": "ANNUAL_SUBSCRIPTION",
            "payment_day": "2025-12-24T10:00:00",
            "employee_quantity": 7,
            "gateway_transaction_id": "txn-789"
        }
        
        payment = Payment.from_dict(data)
        
        assert payment.id == "pay-456"
        assert payment.valor == Decimal("59.90")
        assert payment.payment_status == PaymentStatus.PENDING
        assert payment.payment_type == PaymentType.ANNUAL_SUBSCRIPTION
