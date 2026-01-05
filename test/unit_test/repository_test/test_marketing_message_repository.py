import pytest
from infra.repository import MarketingMessageRepository


class TestMarketingMessageRepository:
    """Testes para MarketingMessageRepository"""

    def test_get_by_id(self, db_session, sample_marketing_message):
        """Testa busca por ID"""
        repo = MarketingMessageRepository(db_session)
        
        found = repo.get_by_id(sample_marketing_message.id)
        
        assert found is not None
        assert found.id == sample_marketing_message.id

    def test_list_all(self, db_session, sample_marketing_message):
        """Testa listagem de todas as mensagens"""
        repo = MarketingMessageRepository(db_session)
        
        result = repo.list_all(limit=10)
        
        assert result.data is not None
        assert len(result.data) > 0

    def test_list_by_establishment_id(self, db_session, sample_marketing_message, sample_establishment):
        """Testa listagem por establishment_id"""
        repo = MarketingMessageRepository(db_session)
        
        result = repo.list_by_establishment_id(
            establishment_id=sample_establishment.uuid,
            limit=10
        )
        
        assert result.data is not None

    def test_delete_marketing_message(self, db_session, sample_marketing_message):
        """Testa deleção de mensagem"""
        repo = MarketingMessageRepository(db_session)
        
        message_id = sample_marketing_message.id
        success = repo.delete(message_id)
        
        assert success is True
        
        found = repo.get_by_id(message_id)
        assert found is None
