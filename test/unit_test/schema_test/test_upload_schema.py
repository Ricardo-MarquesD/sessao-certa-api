import pytest
from pydantic import ValidationError
from schema.upload_schema import (
    ImageUploadResponse,
    ImageDeleteResponse,
    ImageValidationError
)

class TestImageUploadResponse:
    """Testes para ImageUploadResponse"""
    
    def test_image_upload_response_valid(self):
        """Deve criar response válido"""
        data = {
            "img_url": "/static/img/user/uuid/file.jpg",
            "filename": "abc123-xyz.jpg",
            "size": 245678,
            "content_type": "image/jpeg"
        }
        response = ImageUploadResponse(**data)
        assert response.img_url == "/static/img/user/uuid/file.jpg"
        assert response.filename == "abc123-xyz.jpg"
        assert response.size == 245678
        assert response.content_type == "image/jpeg"

class TestImageDeleteResponse:
    """Testes para ImageDeleteResponse"""
    
    def test_image_delete_response_valid(self):
        """Deve criar delete response válido"""
        data = {
            "message": "Imagem deletada com sucesso",
            "deleted_path": "/path/to/image.jpg"
        }
        response = ImageDeleteResponse(**data)
        assert response.message == "Imagem deletada com sucesso"
        assert response.deleted_path == "/path/to/image.jpg"

class TestImageValidationError:
    """Testes para ImageValidationError"""
    
    def test_image_validation_error_valid(self):
        """Deve criar validation error válido"""
        data = {
            "error": "Invalid file type",
            "detail": "Only JPEG and PNG are allowed"
        }
        error = ImageValidationError(**data)
        assert error.error == "Invalid file type"
        assert error.detail == "Only JPEG and PNG are allowed"
