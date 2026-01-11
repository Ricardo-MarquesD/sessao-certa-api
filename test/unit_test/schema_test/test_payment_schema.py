import pytest
from pydantic import ValidationError
from schema.payment_schema import (
    CreatePaymentRequest,
    UpdatePaymentStatusRequest,
    RefundPaymentRequest,
    PaymentResponse
)
from utils.enum import PaymentStatus, PaymentType
from decimal import Decimal
from uuid import uuid4
from datetime import datetime

class TestCreatePaymentRequest:
    """Testes para CreatePaymentRequest"""
    
    def test_create_payment_request_valid(self):
        """Deve criar payment request válido"""
        data = {
            "establishment_id": uuid4(),
            "valor": Decimal("199.90"),
            "payment_type": PaymentType.MONTHLY_SUBSCRIPTION,
            "employee_quantity": 5,
            "gateway_transaction_id": "txn_123456"
        }
        payment = CreatePaymentRequest(**data)
        assert payment.valor == Decimal("199.90")
        assert payment.payment_type == PaymentType.MONTHLY_SUBSCRIPTION
        assert payment.employee_quantity == 5
    
    def test_create_payment_request_without_employee_quantity(self):
        """Deve aceitar sem employee_quantity"""
        data = {
            "establishment_id": uuid4(),
            "valor": Decimal("99.90"),
            "payment_type": PaymentType.ANNUAL_SUBSCRIPTION
        }
        payment = CreatePaymentRequest(**data)
        assert payment.employee_quantity is None
    
    def test_create_payment_request_valor_zero_fails(self):
        """Deve falhar com valor zero ou negativo"""
        data = {
            "establishment_id": uuid4(),
            "valor": Decimal("0"),
            "payment_type": PaymentType.MONTHLY_SUBSCRIPTION
        }
        with pytest.raises(ValidationError):
            CreatePaymentRequest(**data)
    
    def test_create_payment_request_employee_quantity_negative_fails(self):
        """Deve falhar com quantity negativa"""
        data = {
            "establishment_id": uuid4(),
            "valor": Decimal("100"),
            "payment_type": PaymentType.MONTHLY_SUBSCRIPTION,
            "employee_quantity": -1
        }
        with pytest.raises(ValidationError):
            CreatePaymentRequest(**data)

class TestUpdatePaymentStatusRequest:
    """Testes para UpdatePaymentStatusRequest"""
    
    def test_update_payment_status_request_valid(self):
        """Deve atualizar status do pagamento"""
        data = {
            "payment_status": PaymentStatus.APPROVED,
            "gateway_transaction_id": "txn_approved_123"
        }
        update = UpdatePaymentStatusRequest(**data)
        assert update.payment_status == PaymentStatus.APPROVED
        assert update.gateway_transaction_id == "txn_approved_123"
    
    def test_update_payment_status_request_without_transaction_id(self):
        """Deve aceitar sem transaction_id"""
        data = {"payment_status": PaymentStatus.REFUSED}
        update = UpdatePaymentStatusRequest(**data)
        assert update.payment_status == PaymentStatus.REFUSED
        assert update.gateway_transaction_id is None

class TestRefundPaymentRequest:
    """Testes para RefundPaymentRequest"""
    
    def test_refund_payment_request_valid(self):
        """Deve criar refund request válido"""
        data = {"reason": "Cliente solicitou cancelamento do plano"}
        refund = RefundPaymentRequest(**data)
        assert refund.reason == "Cliente solicitou cancelamento do plano"
    
    def test_refund_payment_request_reason_too_short_fails(self):
        """Deve falhar com motivo muito curto"""
        data = {"reason": "curto"}
        with pytest.raises(ValidationError):
            RefundPaymentRequest(**data)
    
    def test_refund_payment_request_reason_too_long_fails(self):
        """Deve falhar com motivo muito longo"""
        data = {"reason": "a" * 501}
        with pytest.raises(ValidationError):
            RefundPaymentRequest(**data)

class TestPaymentResponse:
    """Testes para PaymentResponse"""
    
    def test_payment_response_valid(self):
        """Deve criar response válido"""
        payment_id = uuid4()
        establishment_id = uuid4()
        data = {
            "id": payment_id,
            "establishment_id": establishment_id,
            "valor": "199.90",
            "payment_status": "PENDING",
            "payment_type": "MONTHLY_SUBSCRIPTION",
            "payment_day": datetime.now(),
            "employee_quantity": 5,
            "gateway_transaction_id": "txn_123",
            "can_refund": False
        }
        response = PaymentResponse(**data)
        assert response.id == payment_id
        assert response.valor == "199.90"
        assert response.payment_status == "PENDING"
