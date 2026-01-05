import pytest
from domain.entities import Customer
from infra.repository import CustomerRepository


class TestCustomerRepository:
    """Testes para CustomerRepository"""

    def test_get_by_id(self, db_session, sample_customer):
        """Testa busca por ID"""
        repo = CustomerRepository(db_session)
        
        found = repo.get_by_id(sample_customer.uuid)
        
        assert found is not None
        assert found.id == sample_customer.uuid

    def test_get_by_phone_number(self, db_session, sample_customer, sample_establishment):
        """Testa busca por telefone e estabelecimento"""
        repo = CustomerRepository(db_session)
        
        found = repo.get_by_phone_number(
            phone_number=sample_customer.phone_number,
            establishment_id=sample_establishment.uuid
        )
        
        assert found is not None
        assert found.phone_number == sample_customer.phone_number

    def test_list_all(self, db_session, sample_customer):
        """Testa listagem de todos os customers"""
        repo = CustomerRepository(db_session)
        
        result = repo.list_all(limit=10)
        
        assert result.data is not None
        assert len(result.data) > 0

    def test_list_by_establishment_id(self, db_session, sample_customer, sample_establishment):
        """Testa listagem por establishment_id"""
        repo = CustomerRepository(db_session)
        
        result = repo.list_by_establishment_id(
            establishment_id=sample_establishment.uuid,
            limit=10
        )
        
        assert result.data is not None

    def test_search_by_name(self, db_session, sample_customer, sample_establishment):
        """Testa busca parcial por nome"""
        repo = CustomerRepository(db_session)
        
        result = repo.search_by_name(
            name="Cliente",
            establishment_id=sample_establishment.uuid,
            limit=10
        )
        
        assert result.data is not None

    def test_delete_customer(self, db_session, sample_customer):
        """Testa deleção de customer"""
        repo = CustomerRepository(db_session)
        
        customer_uuid = sample_customer.uuid
        success = repo.delete(customer_uuid)
        
        assert success is True
        
        found = repo.get_by_id(customer_uuid)
        assert found is None
