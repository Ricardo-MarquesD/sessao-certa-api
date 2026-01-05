import pytest
from datetime import datetime
from infra.repository import PaymentRepository
from utils.enum import PaymentStatus, PaymentType


class TestPaymentRepository:
    """Testes para PaymentRepository"""

    def test_get_by_id(self, db_session, sample_payment):
        """Testa busca por ID"""
        repo = PaymentRepository(db_session)
        
        found = repo.get_by_id(sample_payment.uuid)
        
        assert found is not None
        assert found.id == sample_payment.uuid

    def test_list_all(self, db_session, sample_payment):
        """Testa listagem de todos os pagamentos"""
        repo = PaymentRepository(db_session)
        
        result = repo.list_all(limit=10)
        
        assert result.data is not None
        assert len(result.data) > 0

    def test_list_by_establishment_id(self, db_session, sample_payment, sample_establishment):
        """Testa listagem por establishment_id"""
        repo = PaymentRepository(db_session)
        
        result = repo.list_by_establishment_id(
            establishment_id=sample_establishment.uuid,
            limit=10
        )
        
        assert result.data is not None

    def test_list_by_status(self, db_session, sample_payment):
        """Testa listagem por status"""
        repo = PaymentRepository(db_session)
        
        result = repo.list_by_status(
            status=PaymentStatus.PENDING,
            limit=10
        )
        
        assert result.data is not None

    def test_list_by_type(self, db_session, sample_payment):
        """Testa listagem por tipo"""
        repo = PaymentRepository(db_session)
        
        result = repo.list_by_type(
            payment_type=PaymentType.MONTHLY_SUBSCRIPTION,
            limit=10
        )
        
        assert result.data is not None

    def test_list_by_due_date_range(self, db_session, sample_payment):
        """Testa listagem por intervalo de datas"""
        repo = PaymentRepository(db_session)
        
        start_date = datetime(2026, 1, 1)
        end_date = datetime(2026, 12, 31)
        
        result = repo.list_by_due_date_range(
            start_date=start_date,
            end_date=end_date,
            limit=10
        )
        
        assert result.data is not None

    def test_delete_payment(self, db_session, sample_payment):
        """Testa deleção de pagamento"""
        repo = PaymentRepository(db_session)
        
        payment_uuid = sample_payment.uuid
        success = repo.delete(payment_uuid)
        
        assert success is True
        
        found = repo.get_by_id(payment_uuid)
        assert found is None
