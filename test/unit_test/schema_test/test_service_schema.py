import pytest
from pydantic import ValidationError
from schema.service_schema import (
    CreateServiceRequest,
    UpdateServiceRequest,
    UpdateServiceStatusRequest,
    ServiceResponse
)
from decimal import Decimal
from uuid import uuid4

class TestCreateServiceRequest:
    """Testes para CreateServiceRequest"""
    
    def test_create_service_request_valid(self):
        """Deve criar service request válido"""
        data = {
            "establishment_id": uuid4(),
            "service_name": "Corte de Cabelo",
            "description_service": "Corte masculino",
            "time_duration": 30,
            "price": Decimal("50.00"),
            "active": True
        }
        service = CreateServiceRequest(**data)
        assert service.service_name == "Corte de Cabelo"
        assert service.time_duration == 30
        assert service.price == Decimal("50.00")
    
    def test_create_service_request_defaults(self):
        """Deve usar valores padrão"""
        data = {
            "establishment_id": uuid4(),
            "service_name": "Manicure",
            "time_duration": 45
        }
        service = CreateServiceRequest(**data)
        assert service.active == True
        assert service.description_service is None
        assert service.price is None
    
    def test_create_service_request_time_zero_fails(self):
        """Deve falhar com duração zero ou negativa"""
        data = {
            "establishment_id": uuid4(),
            "service_name": "Serviço",
            "time_duration": 0
        }
        with pytest.raises(ValidationError):
            CreateServiceRequest(**data)
    
    def test_create_service_request_price_negative_fails(self):
        """Deve falhar com preço negativo"""
        data = {
            "establishment_id": uuid4(),
            "service_name": "Serviço",
            "time_duration": 30,
            "price": Decimal("-10")
        }
        with pytest.raises(ValidationError):
            CreateServiceRequest(**data)

class TestUpdateServiceRequest:
    """Testes para UpdateServiceRequest"""
    
    def test_update_service_request_valid(self):
        """Deve atualizar service"""
        data = {
            "service_name": "Novo Nome",
            "description_service": "Nova Descrição",
            "time_duration": 60,
            "price": Decimal("75.00")
        }
        update = UpdateServiceRequest(**data)
        assert update.service_name == "Novo Nome"
        assert update.time_duration == 60
    
    def test_update_service_request_partial(self):
        """Deve aceitar atualização parcial"""
        data = {"price": Decimal("80.00")}
        update = UpdateServiceRequest(**data)
        assert update.price == Decimal("80.00")
        assert update.service_name is None
    
    def test_update_service_request_empty(self):
        """Deve aceitar objeto vazio"""
        update = UpdateServiceRequest()
        assert update.service_name is None

class TestUpdateServiceStatusRequest:
    """Testes para UpdateServiceStatusRequest"""
    
    def test_update_service_status_request_valid(self):
        """Deve atualizar status"""
        data = {"active": False}
        update = UpdateServiceStatusRequest(**data)
        assert update.active == False

class TestServiceResponse:
    """Testes para ServiceResponse"""
    
    def test_service_response_valid(self):
        """Deve criar response válido"""
        service_id = uuid4()
        establishment_id = uuid4()
        data = {
            "id": service_id,
            "establishment_id": establishment_id,
            "service_name": "Corte",
            "description_service": "Descrição",
            "time_duration": 30,
            "price": "50.00",
            "active": True
        }
        response = ServiceResponse(**data)
        assert response.id == service_id
        assert response.service_name == "Corte"
