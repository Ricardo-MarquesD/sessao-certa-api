import pytest
from pydantic import ValidationError
from schema.user_schema import (
    CreateUserRequest,
    UpdateUserRequest,
    UserResponse,
    UpdateImgRequest,
    UpdateRoleRequest,
    CreateClientRequest,
    UpdateClientRequest,
    CreateEmployeeRequest,
    UpdateEmployeeRequest,
    UpdateEmployeeAvailabilityRequest
)
from utils.enum import UserRole
from uuid import uuid4
from decimal import Decimal

class TestCreateUserRequest:
    """Testes para CreateUserRequest"""
    
    def test_create_user_request_valid(self):
        """Deve criar request válido"""
        data = {
            "user_name": "João Silva",
            "email": "joao@example.com",
            "phone_number": "+5511999999999",
            "role": "CLIENT",
            "password": "senha123"
        }
        user = CreateUserRequest(**data)
        assert user.user_name == "João Silva"
        assert user.email == "joao@example.com"
        assert user.password == "senha123"
    
    def test_create_user_request_brazilian_phone(self):
        """Deve aceitar telefone brasileiro com código do país"""
        data = {
            "user_name": "Maria",
            "email": "maria@example.com",
            "phone_number": "+5511988888888",
            "role": "CLIENT",
            "password": "senha123"
        }
        user = CreateUserRequest(**data)
        assert user.phone_number is not None
    
    def test_create_user_request_admin_role_fails(self):
        """Não deve aceitar role ADMIN"""
        data = {
            "user_name": "Admin",
            "email": "admin@example.com",
            "phone_number": "+5511999999999",
            "role": UserRole.ADMIN,
            "password": "senha123"
        }
        with pytest.raises(ValidationError) as exc:
            CreateUserRequest(**data)
        assert "Request cannot put Admin status" in str(exc.value)
    
    def test_create_user_request_invalid_email(self):
        """Deve falhar com email inválido"""
        data = {
            "user_name": "João",
            "email": "email-invalido",
            "phone_number": "+5511999999999",
            "role": UserRole.CLIENT,
            "password": "senha123"
        }
        with pytest.raises(ValidationError):
            CreateUserRequest(**data)
    
    def test_create_user_request_empty_name(self):
        """Deve falhar com nome vazio"""
        data = {
            "user_name": "",
            "email": "joao@example.com",
            "phone_number": "+5511999999999",
            "role": UserRole.CLIENT,
            "password": "senha123"
        }
        with pytest.raises(ValidationError):
            CreateUserRequest(**data)

class TestUpdateUserRequest:
    """Testes para UpdateUserRequest"""
    
    def test_update_user_request_all_fields(self):
        """Deve atualizar todos os campos"""
        data = {
            "user_name": "Novo Nome",
            "email": "novo@example.com",
            "phone_number": "+5511988888888",
            "active_status": False
        }
        update = UpdateUserRequest(**data)
        assert update.user_name == "Novo Nome"
        assert update.email == "novo@example.com"
        assert update.active_status == False
    
    def test_update_user_request_partial(self):
        """Deve aceitar atualização parcial"""
        data = {"user_name": "Apenas Nome"}
        update = UpdateUserRequest(**data)
        assert update.user_name == "Apenas Nome"
        assert update.email is None
        assert update.phone_number is None
        assert update.active_status is None
    
    def test_update_user_request_empty(self):
        """Deve aceitar objeto vazio"""
        update = UpdateUserRequest()
        assert update.user_name is None
        assert update.email is None

class TestUpdateImgRequest:
    """Testes para UpdateImgRequest"""
    
    def test_update_img_request_valid(self):
        """Deve aceitar URL válida"""
        data = {"img_url": "/static/img/user/uuid/file.jpg"}
        img = UpdateImgRequest(**data)
        assert img.img_url == "/static/img/user/uuid/file.jpg"
    
    def test_update_img_request_long_url_fails(self):
        """Deve falhar com URL maior que 500 caracteres"""
        data = {"img_url": "a" * 501}
        with pytest.raises(ValidationError):
            UpdateImgRequest(**data)

class TestUpdateRoleRequest:
    """Testes para UpdateRoleRequest"""
    
    def test_update_role_request_valid(self):
        """Deve aceitar role válido"""
        data = {"role": UserRole.EMPLOYEE}
        role = UpdateRoleRequest(**data)
        assert role.role == UserRole.EMPLOYEE

class TestCreateClientRequest:
    """Testes para CreateClientRequest"""
    
    def test_create_client_request_valid(self):
        """Deve criar client request válido"""
        data = {
            "user_id": uuid4(),
            "plan_id": 1
        }
        client = CreateClientRequest(**data)
        assert client.user_id is not None
        assert client.plan_id == 1

class TestUpdateClientRequest:
    """Testes para UpdateClientRequest"""
    
    def test_update_client_request_valid(self):
        """Deve aceitar plan_id válido"""
        data = {"plan_id": 2}
        update = UpdateClientRequest(**data)
        assert update.plan_id == 2

class TestCreateEmployeeRequest:
    """Testes para CreateEmployeeRequest"""
    
    def test_create_employee_request_valid(self):
        """Deve criar employee request válido"""
        data = {
            "user_id": uuid4(),
            "establishment_id": uuid4(),
            "percentage_commission": Decimal("10.5"),
            "available_hours": {
                "monday": ["09:00-18:00"],
                "tuesday": ["09:00-18:00"]
            }
        }
        employee = CreateEmployeeRequest(**data)
        assert employee.percentage_commission == Decimal("10.5")
        assert "monday" in employee.available_hours
    
    def test_create_employee_request_commission_over_100_fails(self):
        """Deve falhar com comissão acima de 100"""
        data = {
            "user_id": uuid4(),
            "establishment_id": uuid4(),
            "percentage_commission": Decimal("101")
        }
        with pytest.raises(ValidationError):
            CreateEmployeeRequest(**data)
    
    def test_create_employee_request_commission_negative_fails(self):
        """Deve falhar com comissão negativa"""
        data = {
            "user_id": uuid4(),
            "establishment_id": uuid4(),
            "percentage_commission": Decimal("-1")
        }
        with pytest.raises(ValidationError):
            CreateEmployeeRequest(**data)

class TestUpdateEmployeeRequest:
    """Testes para UpdateEmployeeRequest"""
    
    def test_update_employee_request_valid(self):
        """Deve atualizar employee"""
        data = {
            "percentage_commission": Decimal("15.0"),
            "available_hours": {"friday": ["09:00-17:00"]}
        }
        update = UpdateEmployeeRequest(**data)
        assert update.percentage_commission == Decimal("15.0")

class TestUpdateEmployeeAvailabilityRequest:
    """Testes para UpdateEmployeeAvailabilityRequest"""
    
    def test_update_availability_request_valid(self):
        """Deve atualizar disponibilidade"""
        data = {
            "available_hours": {
                "monday": ["09:00-18:00"],
                "wednesday": []
            }
        }
        update = UpdateEmployeeAvailabilityRequest(**data)
        assert "monday" in update.available_hours
        assert update.available_hours["wednesday"] == []
