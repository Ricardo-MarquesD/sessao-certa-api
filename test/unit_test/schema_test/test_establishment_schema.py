import pytest
from pydantic import ValidationError
from schema.establishment_schema import (
    CreateEstablishmentRequest,
    UpdateEstablishmentRequest,
    UpdateEstablishmentImgRequest,
    EstablishmentResponse
)
from datetime import datetime
from uuid import uuid4

class TestCreateEstablishmentRequest:
    """Testes para CreateEstablishmentRequest"""
    
    def test_create_establishment_request_valid(self):
        """Deve criar establishment request válido"""
        data = {
            "client_id": 1,
            "establishment_name": "Salão Beauty",
            "cnpj": "12345678000190",
            "chatbot_phone_number": "+5511999999999",
            "address": "Rua A, 123",
            "trial_active": True
        }
        establishment = CreateEstablishmentRequest(**data)
        assert establishment.establishment_name == "Salão Beauty"
        assert establishment.cnpj == "12345678000190"
    
    def test_create_establishment_request_cnpj_with_mask(self):
        """Deve aceitar CNPJ com máscara e remover"""
        data = {
            "client_id": 1,
            "establishment_name": "Salão Beauty",
            "cnpj": "12.345.678/0001-90",
            "trial_active": True
        }
        establishment = CreateEstablishmentRequest(**data)
        assert establishment.cnpj == "12345678000190"
    
    def test_create_establishment_request_cnpj_invalid_length_fails(self):
        """Deve falhar com CNPJ com menos de 14 dígitos"""
        data = {
            "client_id": 1,
            "establishment_name": "Salão Beauty",
            "cnpj": "123456789",
            "trial_active": True
        }
        with pytest.raises(ValidationError) as exc:
            CreateEstablishmentRequest(**data)
        assert "at least 14 characters" in str(exc.value)
    
    def test_create_establishment_request_empty_name_fails(self):
        """Deve falhar com nome vazio"""
        data = {
            "client_id": 1,
            "establishment_name": "",
            "cnpj": "12345678000190"
        }
        with pytest.raises(ValidationError):
            CreateEstablishmentRequest(**data)

class TestUpdateEstablishmentRequest:
    """Testes para UpdateEstablishmentRequest"""
    
    def test_update_establishment_request_valid(self):
        """Deve atualizar establishment"""
        data = {
            "establishment_name": "Novo Nome",
            "chatbot_phone_number": "+5511988888888",
            "address": "Nova Rua, 456",
            "due_date": datetime.now(),
            "trial_active": False
        }
        update = UpdateEstablishmentRequest(**data)
        assert update.establishment_name == "Novo Nome"
        assert update.trial_active == False
    
    def test_update_establishment_request_partial(self):
        """Deve aceitar atualização parcial"""
        data = {"establishment_name": "Apenas Nome"}
        update = UpdateEstablishmentRequest(**data)
        assert update.establishment_name == "Apenas Nome"
        assert update.address is None
    
    def test_update_establishment_request_empty(self):
        """Deve aceitar objeto vazio"""
        update = UpdateEstablishmentRequest()
        assert update.establishment_name is None

class TestUpdateEstablishmentImgRequest:
    """Testes para UpdateEstablishmentImgRequest"""
    
    def test_update_establishment_img_request_valid(self):
        """Deve aceitar URL válida"""
        data = {"img_url": "/static/img/establishment/uuid/file.jpg"}
        img = UpdateEstablishmentImgRequest(**data)
        assert img.img_url == "/static/img/establishment/uuid/file.jpg"
    
    def test_update_establishment_img_request_long_url_fails(self):
        """Deve falhar com URL maior que 500 caracteres"""
        data = {"img_url": "a" * 501}
        with pytest.raises(ValidationError):
            UpdateEstablishmentImgRequest(**data)

class TestEstablishmentResponse:
    """Testes para EstablishmentResponse"""
    
    def test_establishment_response_valid(self):
        """Deve criar response válido"""
        establishment_id = uuid4()
        data = {
            "id": establishment_id,
            "client_id": 1,
            "establishment_name": "Salão Beauty",
            "cnpj": "12345678000190",
            "chatbot_phone_number": "+5511999999999",
            "address": "Rua A, 123",
            "img_url": "/static/img/establishment/uuid/file.jpg",
            "subscription_date": datetime.now(),
            "due_date": datetime.now(),
            "trial_active": True,
            "is_subscription_valid": True
        }
        response = EstablishmentResponse(**data)
        assert response.id == establishment_id
        assert response.establishment_name == "Salão Beauty"
