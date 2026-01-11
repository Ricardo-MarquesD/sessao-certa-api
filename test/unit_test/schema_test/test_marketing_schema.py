import pytest
from pydantic import ValidationError
from schema.marketing_schema import (
    CreateMarketingMessageRequest,
    UpdateMarketingMessageRequest,
    MarketingMessageResponse
)
from uuid import uuid4

class TestCreateMarketingMessageRequest:
    """Testes para CreateMarketingMessageRequest"""
    
    def test_create_marketing_message_request_valid(self):
        """Deve criar marketing message request válido"""
        data = {
            "establishment_id": uuid4(),
            "title": "Promoção de Natal",
            "content": "Desconto de 20% em todos os serviços"
        }
        message = CreateMarketingMessageRequest(**data)
        assert message.title == "Promoção de Natal"
        assert message.content == "Desconto de 20% em todos os serviços"
    
    def test_create_marketing_message_request_without_title(self):
        """Deve aceitar sem título"""
        data = {
            "establishment_id": uuid4(),
            "content": "Apenas conteúdo"
        }
        message = CreateMarketingMessageRequest(**data)
        assert message.title is None
        assert message.content == "Apenas conteúdo"
    
    def test_create_marketing_message_request_without_content(self):
        """Deve aceitar sem conteúdo"""
        data = {
            "establishment_id": uuid4(),
            "title": "Apenas título"
        }
        message = CreateMarketingMessageRequest(**data)
        assert message.title == "Apenas título"
        assert message.content is None
    
    def test_create_marketing_message_request_title_too_long_fails(self):
        """Deve falhar com título muito longo"""
        data = {
            "establishment_id": uuid4(),
            "title": "a" * 256
        }
        with pytest.raises(ValidationError):
            CreateMarketingMessageRequest(**data)
    
    def test_create_marketing_message_request_content_too_long_fails(self):
        """Deve falhar com conteúdo muito longo"""
        data = {
            "establishment_id": uuid4(),
            "content": "a" * 5001
        }
        with pytest.raises(ValidationError):
            CreateMarketingMessageRequest(**data)

class TestUpdateMarketingMessageRequest:
    """Testes para UpdateMarketingMessageRequest"""
    
    def test_update_marketing_message_request_valid(self):
        """Deve atualizar marketing message"""
        data = {
            "title": "Novo Título",
            "content": "Novo Conteúdo"
        }
        update = UpdateMarketingMessageRequest(**data)
        assert update.title == "Novo Título"
        assert update.content == "Novo Conteúdo"
    
    def test_update_marketing_message_request_partial(self):
        """Deve aceitar atualização parcial"""
        data = {"title": "Apenas Título"}
        update = UpdateMarketingMessageRequest(**data)
        assert update.title == "Apenas Título"
        assert update.content is None
    
    def test_update_marketing_message_request_empty(self):
        """Deve aceitar objeto vazio"""
        update = UpdateMarketingMessageRequest()
        assert update.title is None
        assert update.content is None

class TestMarketingMessageResponse:
    """Testes para MarketingMessageResponse"""
    
    def test_marketing_message_response_valid(self):
        """Deve criar response válido"""
        establishment_id = uuid4()
        data = {
            "id": 1,
            "establishment_id": establishment_id,
            "title": "Promoção",
            "content": "Desconto"
        }
        response = MarketingMessageResponse(**data)
        assert response.id == 1
        assert response.establishment_id == establishment_id
        assert response.title == "Promoção"
