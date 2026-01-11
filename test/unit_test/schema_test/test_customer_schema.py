import pytest
from pydantic import ValidationError
from schema.customer_schema import (
    CreateCustomerRequest,
    UpdateCustomerRequest,
    CustomerResponse
)
from uuid import uuid4

class TestCreateCustomerRequest:
    """Testes para CreateCustomerRequest"""
    
    def test_create_customer_request_valid(self):
        """Deve criar customer request válido"""
        data = {
            "establishment_id": uuid4(),
            "customer_name": "Carlos Silva",
            "phone_number": "+5511999999999"
        }
        customer = CreateCustomerRequest(**data)
        assert customer.customer_name == "Carlos Silva"
        assert customer.establishment_id is not None
    
    def test_create_customer_request_brazilian_phone(self):
        """Deve aceitar telefone brasileiro"""
        data = {
            "establishment_id": uuid4(),
            "customer_name": "Maria",
            "phone_number": "+5511988888888"
        }
        customer = CreateCustomerRequest(**data)
        assert customer.phone_number is not None
    
    def test_create_customer_request_empty_name_fails(self):
        """Deve falhar com nome vazio"""
        data = {
            "establishment_id": uuid4(),
            "customer_name": "",
            "phone_number": "+5511999999999"
        }
        with pytest.raises(ValidationError):
            CreateCustomerRequest(**data)
    
    def test_create_customer_request_name_too_long_fails(self):
        """Deve falhar com nome maior que 255 caracteres"""
        data = {
            "establishment_id": uuid4(),
            "customer_name": "a" * 256,
            "phone_number": "+5511999999999"
        }
        with pytest.raises(ValidationError):
            CreateCustomerRequest(**data)

class TestUpdateCustomerRequest:
    """Testes para UpdateCustomerRequest"""
    
    def test_update_customer_request_valid(self):
        """Deve atualizar customer"""
        data = {
            "customer_name": "Carlos Silva Jr",
            "phone_number": "+5511988888888"
        }
        update = UpdateCustomerRequest(**data)
        assert update.customer_name == "Carlos Silva Jr"
        assert update.phone_number is not None
    
    def test_update_customer_request_partial(self):
        """Deve aceitar atualização parcial"""
        data = {"customer_name": "Novo Nome"}
        update = UpdateCustomerRequest(**data)
        assert update.customer_name == "Novo Nome"
        assert update.phone_number is None
    
    def test_update_customer_request_empty(self):
        """Deve aceitar objeto vazio"""
        update = UpdateCustomerRequest()
        assert update.customer_name is None
        assert update.phone_number is None

class TestCustomerResponse:
    """Testes para CustomerResponse"""
    
    def test_customer_response_valid(self):
        """Deve criar response válido"""
        establishment_id = uuid4()
        customer_id = uuid4()
        data = {
            "id": customer_id,
            "establishment_id": establishment_id,
            "customer_name": "Carlos Silva",
            "phone_number": "+5511999999999"
        }
        response = CustomerResponse(**data)
        assert response.id == customer_id
        assert response.establishment_id == establishment_id
        assert response.customer_name == "Carlos Silva"
