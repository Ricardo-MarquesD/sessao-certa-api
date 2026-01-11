import pytest
from pydantic import ValidationError
from schema.plan_schema import (
    CreatePlanRequest,
    UpdatePlanRequest,
    PlanResponse
)
from utils.enum import TypePlan
from decimal import Decimal

class TestCreatePlanRequest:
    """Testes para CreatePlanRequest"""
    
    def test_create_plan_request_valid(self):
        """Deve criar plan request válido"""
        data = {
            "type_plan": TypePlan.BRONZE,
            "basic_price": Decimal("99.90"),
            "max_employee": 5,
            "allow_stock": True,
            "allow_advanced_analysis": False
        }
        plan = CreatePlanRequest(**data)
        assert plan.type_plan == TypePlan.BRONZE
        assert plan.basic_price == Decimal("99.90")
        assert plan.max_employee == 5
        assert plan.allow_stock == True
        assert plan.allow_advanced_analysis == False
    
    def test_create_plan_request_defaults(self):
        """Deve usar valores padrão"""
        data = {
            "type_plan": TypePlan.SILVER,
            "basic_price": Decimal("199.90"),
            "max_employee": 10
        }
        plan = CreatePlanRequest(**data)
        assert plan.allow_stock == False
        assert plan.allow_advanced_analysis == False
    
    def test_create_plan_request_price_zero_fails(self):
        """Deve falhar com preço zero ou negativo"""
        data = {
            "type_plan": TypePlan.BRONZE,
            "basic_price": Decimal("0"),
            "max_employee": 5
        }
        with pytest.raises(ValidationError):
            CreatePlanRequest(**data)
    
    def test_create_plan_request_price_negative_fails(self):
        """Deve falhar com preço negativo"""
        data = {
            "type_plan": TypePlan.BRONZE,
            "basic_price": Decimal("-10"),
            "max_employee": 5
        }
        with pytest.raises(ValidationError):
            CreatePlanRequest(**data)
    
    def test_create_plan_request_max_employee_zero_fails(self):
        """Deve falhar com max_employee zero ou negativo"""
        data = {
            "type_plan": TypePlan.BRONZE,
            "basic_price": Decimal("99.90"),
            "max_employee": 0
        }
        with pytest.raises(ValidationError):
            CreatePlanRequest(**data)

class TestUpdatePlanRequest:
    """Testes para UpdatePlanRequest"""
    
    def test_update_plan_request_all_fields(self):
        """Deve atualizar todos os campos"""
        data = {
            "basic_price": Decimal("299.90"),
            "max_employee": 20,
            "allow_stock": True,
            "allow_advanced_analysis": True
        }
        update = UpdatePlanRequest(**data)
        assert update.basic_price == Decimal("299.90")
        assert update.max_employee == 20
        assert update.allow_stock == True
        assert update.allow_advanced_analysis == True
    
    def test_update_plan_request_partial(self):
        """Deve aceitar atualização parcial"""
        data = {"basic_price": Decimal("149.90")}
        update = UpdatePlanRequest(**data)
        assert update.basic_price == Decimal("149.90")
        assert update.max_employee is None
        assert update.allow_stock is None
    
    def test_update_plan_request_empty(self):
        """Deve aceitar objeto vazio"""
        update = UpdatePlanRequest()
        assert update.basic_price is None
        assert update.max_employee is None
    
    def test_update_plan_request_price_zero_fails(self):
        """Deve falhar com preço zero"""
        data = {"basic_price": Decimal("0")}
        with pytest.raises(ValidationError):
            UpdatePlanRequest(**data)
    
    def test_update_plan_request_max_employee_zero_fails(self):
        """Deve falhar com max_employee zero"""
        data = {"max_employee": 0}
        with pytest.raises(ValidationError):
            UpdatePlanRequest(**data)

class TestPlanResponse:
    """Testes para PlanResponse"""
    
    def test_plan_response_valid(self):
        """Deve criar response válido"""
        data = {
            "id": 1,
            "type_plan": "BRONZE",
            "basic_price": "99.90",
            "max_employee": 5,
            "allow_stock": True,
            "allow_advanced_analysis": False
        }
        response = PlanResponse(**data)
        assert response.id == 1
        assert response.type_plan == "BRONZE"
        assert response.basic_price == "99.90"
        assert response.max_employee == 5
