import pytest
from decimal import Decimal
from domain.entities import Plan
from utils.enum import TypePlan


class TestPlanEntity:
    """Testes unitários para a entidade Plan"""
    
    def test_create_bronze_plan_with_valid_data(self):
        """Testa criação de plano Bronze com dados válidos"""
        plan = Plan(
            id=1,
            type_plan=TypePlan.BRONZE,
            basic_price=Decimal("29.90"),
            max_employee=5,
            allow_stock=False,
            allow_advanced_analysis=False
        )
        
        assert plan.type_plan == TypePlan.BRONZE
        assert plan.basic_price == Decimal("29.90")
        assert plan.max_employee == 5
        assert plan.allow_stock is False
    
    def test_create_silver_plan_with_valid_data(self):
        """Testa criação de plano Silver com dados válidos"""
        plan = Plan(
            id=2,
            type_plan=TypePlan.SILVER,
            basic_price=Decimal("59.90"),
            max_employee=10,
            allow_stock=False,
            allow_advanced_analysis=True
        )
        
        assert plan.type_plan == TypePlan.SILVER
        assert plan.basic_price == Decimal("59.90")
    
    def test_create_gold_plan_with_valid_data(self):
        """Testa criação de plano Gold com dados válidos"""
        plan = Plan(
            id=3,
            type_plan=TypePlan.GOLD,
            basic_price=Decimal("99.90"),
            max_employee=20,
            allow_stock=True,
            allow_advanced_analysis=True
        )
        
        assert plan.type_plan == TypePlan.GOLD
        assert plan.has_stock_feature() is True
    
    def test_create_plan_with_invalid_type_raises_error(self):
        """Testa que type_plan inválido levanta erro"""
        with pytest.raises(ValueError, match="Type Plan is incorrect"):
            Plan(
                id=1,
                type_plan="INVALID",
                basic_price=Decimal("29.90"),
                max_employee=5,
                allow_stock=False,
                allow_advanced_analysis=False
            )
    
    def test_create_plan_with_negative_price_raises_error(self):
        """Testa que preço negativo levanta erro"""
        with pytest.raises(ValueError, match="Basic price must be a positive Decimal"):
            Plan(
                id=1,
                type_plan=TypePlan.BRONZE,
                basic_price=Decimal("-29.90"),
                max_employee=5,
                allow_stock=False,
                allow_advanced_analysis=False
            )
    
    def test_create_plan_with_zero_price_raises_error(self):
        """Testa que preço zero levanta erro"""
        with pytest.raises(ValueError, match="Basic price must be a positive Decimal"):
            Plan(
                id=1,
                type_plan=TypePlan.BRONZE,
                basic_price=Decimal("0"),
                max_employee=5,
                allow_stock=False,
                allow_advanced_analysis=False
            )
    
    def test_create_plan_with_invalid_max_employee_raises_error(self):
        """Testa que max_employee inválido levanta erro"""
        with pytest.raises(ValueError, match="Max employee must be a positive integer"):
            Plan(
                id=1,
                type_plan=TypePlan.BRONZE,
                basic_price=Decimal("29.90"),
                max_employee=0,
                allow_stock=False,
                allow_advanced_analysis=False
            )
    
    def test_is_bronze_returns_true_for_bronze_plan(self):
        """Testa is_bronze() retorna True para plano Bronze"""
        plan = Plan(
            id=1,
            type_plan=TypePlan.BRONZE,
            basic_price=Decimal("29.90"),
            max_employee=5,
            allow_stock=False,
            allow_advanced_analysis=False
        )
        
        assert plan.is_bronze() is True
        assert plan.is_silver() is False
        assert plan.is_gold() is False
    
    def test_is_silver_returns_true_for_silver_plan(self):
        """Testa is_silver() retorna True para plano Silver"""
        plan = Plan(
            id=2,
            type_plan=TypePlan.SILVER,
            basic_price=Decimal("59.90"),
            max_employee=10,
            allow_stock=False,
            allow_advanced_analysis=True
        )
        
        assert plan.is_bronze() is False
        assert plan.is_silver() is True
        assert plan.is_gold() is False
    
    def test_is_gold_returns_true_for_gold_plan(self):
        """Testa is_gold() retorna True para plano Gold"""
        plan = Plan(
            id=3,
            type_plan=TypePlan.GOLD,
            basic_price=Decimal("99.90"),
            max_employee=20,
            allow_stock=True,
            allow_advanced_analysis=True
        )
        
        assert plan.is_bronze() is False
        assert plan.is_silver() is False
        assert plan.is_gold() is True
    
    def test_has_stock_feature_returns_true_when_enabled(self):
        """Testa has_stock_feature() retorna True quando habilitado"""
        plan = Plan(
            id=3,
            type_plan=TypePlan.GOLD,
            basic_price=Decimal("99.90"),
            max_employee=20,
            allow_stock=True,
            allow_advanced_analysis=True
        )
        
        assert plan.has_stock_feature() is True
    
    def test_has_stock_feature_returns_false_when_disabled(self):
        """Testa has_stock_feature() retorna False quando desabilitado"""
        plan = Plan(
            id=1,
            type_plan=TypePlan.BRONZE,
            basic_price=Decimal("29.90"),
            max_employee=5,
            allow_stock=False,
            allow_advanced_analysis=False
        )
        
        assert plan.has_stock_feature() is False
    
    def test_has_stock_feature_returns_false_when_none(self):
        """Testa has_stock_feature() retorna False quando None"""
        plan = Plan(
            id=1,
            type_plan=TypePlan.BRONZE,
            basic_price=Decimal("29.90"),
            max_employee=5,
            allow_stock=None,
            allow_advanced_analysis=None
        )
        
        assert plan.has_stock_feature() is False
    
    def test_has_advanced_analysis_feature_returns_true_when_enabled(self):
        """Testa has_advanced_analysis_feature() retorna True quando habilitado"""
        plan = Plan(
            id=2,
            type_plan=TypePlan.SILVER,
            basic_price=Decimal("59.90"),
            max_employee=10,
            allow_stock=False,
            allow_advanced_analysis=True
        )
        
        assert plan.has_advanced_analysis_feature() is True
    
    def test_is_within_included_limit_returns_true_when_within(self):
        """Testa is_within_included_limit() retorna True quando dentro do limite"""
        plan = Plan(
            id=1,
            type_plan=TypePlan.BRONZE,
            basic_price=Decimal("29.90"),
            max_employee=5,
            allow_stock=False,
            allow_advanced_analysis=False
        )
        
        assert plan.is_within_included_limit(3) is True
        assert plan.is_within_included_limit(5) is True
    
    def test_is_within_included_limit_returns_false_when_exceeds(self):
        """Testa is_within_included_limit() retorna False quando excede"""
        plan = Plan(
            id=1,
            type_plan=TypePlan.BRONZE,
            basic_price=Decimal("29.90"),
            max_employee=5,
            allow_stock=False,
            allow_advanced_analysis=False
        )
        
        assert plan.is_within_included_limit(6) is False
        assert plan.is_within_included_limit(10) is False
    
    def test_calculate_employee_tax_returns_zero_within_limit(self):
        """Testa calculate_employee_tax() retorna 0 quando dentro do limite"""
        plan = Plan(
            id=1,
            type_plan=TypePlan.BRONZE,
            basic_price=Decimal("29.90"),
            max_employee=5,
            allow_stock=False,
            allow_advanced_analysis=False
        )
        
        tax = plan.calculate_employee_tax(3)
        assert tax == Decimal("0.00")
        
        tax = plan.calculate_employee_tax(5)
        assert tax == Decimal("0.00")
    
    def test_calculate_employee_tax_returns_correct_value_when_exceeds(self):
        """Testa calculate_employee_tax() retorna valor correto quando excede limite"""
        plan = Plan(
            id=1,
            type_plan=TypePlan.BRONZE,
            basic_price=Decimal("29.90"),
            max_employee=5,
            allow_stock=False,
            allow_advanced_analysis=False
        )
        
        # 7 funcionários: 2 extras × R$5,00 = R$10,00
        tax = plan.calculate_employee_tax(7)
        assert tax == Decimal("10.00")
        
        # 6 funcionários: 1 extra × R$5,00 = R$5,00
        tax = plan.calculate_employee_tax(6)
        assert tax == Decimal("5.00")
    
    def test_calculate_total_price_includes_base_and_tax(self):
        """Testa calculate_total_price() inclui preço base + taxa"""
        plan = Plan(
            id=1,
            type_plan=TypePlan.BRONZE,
            basic_price=Decimal("29.90"),
            max_employee=5,
            allow_stock=False,
            allow_advanced_analysis=False
        )
        
        # Dentro do limite: apenas preço base
        total = plan.calculate_total_price(5)
        assert total == Decimal("29.90")
        
        # 7 funcionários: R$29,90 + R$10,00 = R$39,90
        total = plan.calculate_total_price(7)
        assert total == Decimal("39.90")
    
    def test_can_change_to_returns_true_for_different_plan(self):
        """Testa can_change_to() retorna True para plano diferente"""
        plan = Plan(
            id=1,
            type_plan=TypePlan.BRONZE,
            basic_price=Decimal("29.90"),
            max_employee=5,
            allow_stock=False,
            allow_advanced_analysis=False
        )
        
        assert plan.can_change_to(TypePlan.SILVER) is True
        assert plan.can_change_to(TypePlan.GOLD) is True
    
    def test_can_change_to_returns_false_for_same_plan(self):
        """Testa can_change_to() retorna False para o mesmo plano"""
        plan = Plan(
            id=1,
            type_plan=TypePlan.BRONZE,
            basic_price=Decimal("29.90"),
            max_employee=5,
            allow_stock=False,
            allow_advanced_analysis=False
        )
        
        assert plan.can_change_to(TypePlan.BRONZE) is False
    
    def test_is_upgrade_detects_bronze_to_silver(self):
        """Testa is_upgrade() detecta upgrade de Bronze para Silver"""
        plan = Plan(
            id=1,
            type_plan=TypePlan.BRONZE,
            basic_price=Decimal("29.90"),
            max_employee=5,
            allow_stock=False,
            allow_advanced_analysis=False
        )
        
        assert plan.is_upgrade(TypePlan.SILVER) is True
        assert plan.is_upgrade(TypePlan.GOLD) is True
    
    def test_is_upgrade_detects_silver_to_gold(self):
        """Testa is_upgrade() detecta upgrade de Silver para Gold"""
        plan = Plan(
            id=2,
            type_plan=TypePlan.SILVER,
            basic_price=Decimal("59.90"),
            max_employee=10,
            allow_stock=False,
            allow_advanced_analysis=True
        )
        
        assert plan.is_upgrade(TypePlan.GOLD) is True
        assert plan.is_upgrade(TypePlan.BRONZE) is False
    
    def test_is_downgrade_detects_gold_to_silver(self):
        """Testa is_downgrade() detecta downgrade de Gold para Silver"""
        plan = Plan(
            id=3,
            type_plan=TypePlan.GOLD,
            basic_price=Decimal("99.90"),
            max_employee=20,
            allow_stock=True,
            allow_advanced_analysis=True
        )
        
        assert plan.is_downgrade(TypePlan.SILVER) is True
        assert plan.is_downgrade(TypePlan.BRONZE) is True
    
    def test_is_downgrade_detects_silver_to_bronze(self):
        """Testa is_downgrade() detecta downgrade de Silver para Bronze"""
        plan = Plan(
            id=2,
            type_plan=TypePlan.SILVER,
            basic_price=Decimal("59.90"),
            max_employee=10,
            allow_stock=False,
            allow_advanced_analysis=True
        )
        
        assert plan.is_downgrade(TypePlan.BRONZE) is True
        assert plan.is_downgrade(TypePlan.GOLD) is False
    
    def test_to_dict_returns_correct_structure(self):
        """Testa to_dict() retorna estrutura correta"""
        plan = Plan(
            id=1,
            type_plan=TypePlan.BRONZE,
            basic_price=Decimal("29.90"),
            max_employee=5,
            allow_stock=False,
            allow_advanced_analysis=False
        )
        
        plan_dict = plan.to_dict()
        
        assert plan_dict["id"] == 1
        assert plan_dict["type_plan"] == "BRONZE"
        assert plan_dict["basic_price"] == "29.90"
        assert plan_dict["max_employee"] == 5
        assert plan_dict["allow_stock"] is False
    
    def test_from_dict_creates_plan_correctly(self):
        """Testa from_dict() cria plano corretamente"""
        data = {
            "id": 2,
            "type_plan": "SILVER",
            "basic_price": "59.90",
            "max_employee": 10,
            "allow_stock": False,
            "allow_advanced_analysis": True
        }
        
        plan = Plan.from_dict(data)
        
        assert plan.id == 2
        assert plan.type_plan == TypePlan.SILVER
        assert plan.basic_price == Decimal("59.90")
        assert plan.max_employee == 10
        assert plan.allow_advanced_analysis is True
