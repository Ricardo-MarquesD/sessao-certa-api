import pytest
from datetime import datetime
from domain.entities import Establishment
from infra.repository import EstablishmentRepository


class TestEstablishmentRepository:
    """Testes para EstablishmentRepository"""

    def test_get_by_id(self, db_session, sample_establishment):
        """Testa busca por ID"""
        repo = EstablishmentRepository(db_session)
        
        found = repo.get_by_id(sample_establishment.uuid)
        
        assert found is not None
        assert found.id == sample_establishment.uuid

    def test_get_by_client_id(self, db_session, sample_establishment, sample_client):
        """Testa busca por client_id"""
        repo = EstablishmentRepository(db_session)
        
        found = repo.get_by_client_id(sample_client.id)
        
        assert found is not None
        assert found.establishment_name == sample_establishment.establishment_name

    def test_get_by_cnpj(self, db_session, sample_establishment):
        """Testa busca por CNPJ"""
        repo = EstablishmentRepository(db_session)
        
        found = repo.get_by_cnpj(sample_establishment.cnpj)
        
        assert found is not None
        assert found.cnpj == sample_establishment.cnpj

    def test_list_all(self, db_session, sample_establishment):
        """Testa listagem de todos os estabelecimentos"""
        repo = EstablishmentRepository(db_session)
        
        result = repo.list_all(limit=10)
        
        assert result.data is not None
        assert len(result.data) > 0

    def test_list_all_by_trial_active(self, db_session, sample_establishment):
        """Testa listagem por trial ativo"""
        repo = EstablishmentRepository(db_session)
        
        result = repo.list_all_by_trial_active(trial_active=False, limit=10)
        
        assert result.data is not None

    def test_list_with_due_date_expired(self, db_session):
        """Testa listagem com data de vencimento expirada"""
        repo = EstablishmentRepository(db_session)
        
        result = repo.list_with_due_date_expired(limit=10)
        
        assert result.data is not None

    def test_search_by_establishment_name(self, db_session, sample_establishment):
        """Testa busca parcial por nome"""
        repo = EstablishmentRepository(db_session)
        
        result = repo.search_by_establishment_name("Salão", limit=10)
        
        assert result.data is not None

    def test_delete_establishment(self, db_session, sample_establishment):
        """Testa deleção de estabelecimento"""
        repo = EstablishmentRepository(db_session)
        
        establishment_uuid = sample_establishment.uuid
        success = repo.delete(establishment_uuid)
        
        assert success is True
        
        found = repo.get_by_id(establishment_uuid)
        assert found is None
