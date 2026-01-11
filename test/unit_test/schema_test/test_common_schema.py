import pytest
from pydantic import ValidationError
from schema.common_schema import (
    SuccessResponse,
    ErrorResponse,
    MessageResponse,
    DeleteResponse,
    PaginatedResponse
)
from datetime import datetime

class TestSuccessResponse:
    """Testes para SuccessResponse"""
    
    def test_success_response_valid(self):
        """Deve criar response de sucesso válido"""
        data = {
            "message": "Operação realizada com sucesso",
            "data": {"id": 1, "name": "Test"}
        }
        response = SuccessResponse(**data)
        assert response.success == True
        assert response.message == "Operação realizada com sucesso"
        assert response.data["id"] == 1
        assert isinstance(response.timestamp, datetime)
    
    def test_success_response_without_data(self):
        """Deve aceitar sem data"""
        data = {"message": "Operação concluída"}
        response = SuccessResponse(**data)
        assert response.data is None

class TestErrorResponse:
    """Testes para ErrorResponse"""
    
    def test_error_response_valid(self):
        """Deve criar response de erro válido"""
        data = {
            "error": "Validation Error",
            "detail": "Campo obrigatório ausente"
        }
        response = ErrorResponse(**data)
        assert response.error == "Validation Error"
        assert response.detail == "Campo obrigatório ausente"
        assert isinstance(response.timestamp, datetime)
    
    def test_error_response_without_detail(self):
        """Deve aceitar sem detail"""
        data = {"error": "Internal Server Error"}
        response = ErrorResponse(**data)
        assert response.detail is None

class TestMessageResponse:
    """Testes para MessageResponse"""
    
    def test_message_response_valid(self):
        """Deve criar message response válido"""
        data = {"message": "Ação executada"}
        response = MessageResponse(**data)
        assert response.message == "Ação executada"

class TestDeleteResponse:
    """Testes para DeleteResponse"""
    
    def test_delete_response_valid(self):
        """Deve criar delete response válido"""
        data = {
            "deleted_id": "uuid-123"
        }
        response = DeleteResponse(**data)
        assert response.success == True
        assert response.message == "Registro deletado com sucesso"
        assert response.deleted_id == "uuid-123"
    
    def test_delete_response_with_int_id(self):
        """Deve aceitar ID inteiro"""
        data = {"deleted_id": 123}
        response = DeleteResponse(**data)
        assert response.deleted_id == 123
    
    def test_delete_response_without_id(self):
        """Deve aceitar sem ID"""
        response = DeleteResponse()
        assert response.deleted_id is None

class TestPaginatedResponse:
    """Testes para PaginatedResponse"""
    
    def test_paginated_response_valid(self):
        """Deve criar paginated response válido"""
        data = {
            "data": [{"id": 1}, {"id": 2}],
            "cursor": "next_page_cursor",
            "has_more": True,
            "total_count": 100
        }
        response = PaginatedResponse(**data)
        assert len(response.data) == 2
        assert response.cursor == "next_page_cursor"
        assert response.has_more == True
        assert response.total_count == 100
    
    def test_paginated_response_last_page(self):
        """Deve criar response da última página"""
        data = {
            "data": [{"id": 10}],
            "cursor": None,
            "has_more": False,
            "total_count": 10
        }
        response = PaginatedResponse(**data)
        assert response.cursor is None
        assert response.has_more == False
    
    def test_paginated_response_empty_data(self):
        """Deve aceitar data vazio"""
        data = {
            "data": [],
            "has_more": False
        }
        response = PaginatedResponse(**data)
        assert len(response.data) == 0
        assert response.cursor is None
        assert response.total_count is None
