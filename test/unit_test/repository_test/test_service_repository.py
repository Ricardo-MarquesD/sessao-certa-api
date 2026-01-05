import pytest
from infra.repository import ServiceRepository


class TestServiceRepository:
    """Testes para ServiceRepository"""

    def test_get_by_id(self, db_session, sample_service):
        """Testa busca por ID"""
        repo = ServiceRepository(db_session)
        
        found = repo.get_by_id(sample_service.uuid)
        
        assert found is not None
        assert found.id == sample_service.uuid

    def test_list_all(self, db_session, sample_service):
        """Testa listagem de todos os serviços"""
        repo = ServiceRepository(db_session)
        
        result = repo.list_all(limit=10)
        
        assert result.data is not None
        assert len(result.data) > 0

    def test_list_by_establishment_id(self, db_session, sample_service, sample_establishment):
        """Testa listagem por establishment_id"""
        repo = ServiceRepository(db_session)
        
        result = repo.list_by_establishment_id(
            establishment_id=sample_establishment.uuid,
            limit=10
        )
        
        assert result.data is not None

    def test_list_active_by_establishment_id(self, db_session, sample_service, sample_establishment):
        """Testa listagem de serviços ativos por estabelecimento"""
        repo = ServiceRepository(db_session)
        
        result = repo.list_active_by_establishment_id(
            active=True,
            establishment_id=sample_establishment.uuid,
            limit=10
        )
        
        assert result.data is not None
        for service in result.data:
            assert service.active is True

    def test_delete_service(self, db_session, sample_service):
        """Testa deleção de serviço"""
        repo = ServiceRepository(db_session)
        
        service_uuid = sample_service.uuid
        success = repo.delete(service_uuid)
        
        assert success is True
        
        found = repo.get_by_id(service_uuid)
        assert found is None
