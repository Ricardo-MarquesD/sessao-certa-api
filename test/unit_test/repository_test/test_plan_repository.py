import pytest
from decimal import Decimal
from domain.entities import Plan
from infra.repository import PlanRepository
from utils.enum import TypePlan


class TestPlanRepository:
    """Testes para PlanRepository"""

    def test_create_plan(self, db_session):
        """Testa criação de plano"""
        repo = PlanRepository(db_session)
        
        plan = Plan(
            id=None,
            type_plan=TypePlan.GOLD,
            basic_price=Decimal("99.90"),
            max_employee=10,
            allow_stock=True,
            allow_advanced_analysis=True
        )
        
        created = repo.create(plan)
        
        assert created.id is not None
        assert created.type_plan == TypePlan.GOLD
        assert created.basic_price == Decimal("99.90")
        assert created.max_employee == 10

    def test_update_plan(self, db_session, sample_plan):
        """Testa atualização de plano"""
        repo = PlanRepository(db_session)
        
        plan_entity = Plan(
            id=sample_plan.id,
            type_plan=TypePlan.GOLD,
            basic_price=Decimal("149.90"),
            max_employee=15,
            allow_stock=True,
            allow_advanced_analysis=True
        )
        
        updated = repo.update(plan_entity)
        
        assert updated.type_plan == TypePlan.GOLD
        assert updated.basic_price == Decimal("149.90")
        assert updated.max_employee == 15

    def test_get_by_id(self, db_session, sample_plan):
        """Testa busca por ID"""
        repo = PlanRepository(db_session)
        
        found = repo.get_by_id(sample_plan.id)
        
        assert found is not None
        assert found.id == sample_plan.id
        assert found.type_plan == sample_plan.type_plan

    def test_get_by_id_not_found(self, db_session):
        """Testa busca por ID inexistente"""
        repo = PlanRepository(db_session)
        
        found = repo.get_by_id(99999)
        
        assert found is None

    def test_get_by_max_employee(self, db_session, sample_plan):
        """Testa busca por número máximo de funcionários"""
        repo = PlanRepository(db_session)
        
        found = repo.get_by_max_employee(sample_plan.max_employee)
        
        assert found is not None
        assert found.max_employee == sample_plan.max_employee

    def test_list_all(self, db_session, sample_plan):
        """Testa listagem de todos os planos"""
        repo = PlanRepository(db_session)
        
        result = repo.list_all(limit=10)
        
        assert result.data is not None
        assert len(result.data) > 0

    def test_list_by_type(self, db_session, sample_plan):
        """Testa listagem por tipo de plano"""
        repo = PlanRepository(db_session)
        
        result = repo.list_by_type(type_plan=TypePlan.SILVER, limit=10)
        
        assert result.data is not None
        for plan in result.data:
            assert plan.type_plan == TypePlan.SILVER

    def test_list_by_allow_stock(self, db_session, sample_plan):
        """Testa listagem por permissão de estoque"""
        repo = PlanRepository(db_session)
        
        result = repo.list_by_allow_stock(allow_stock=True, limit=10)
        
        assert result.data is not None
        for plan in result.data:
            assert plan.allow_stock is True

    def test_list_by_allow_advanced_analysis(self, db_session, sample_plan):
        """Testa listagem por análise avançada"""
        repo = PlanRepository(db_session)
        
        result = repo.list_by_allow_advanced_analysis(allow_advanced_analysis=True, limit=10)
        
        assert result.data is not None
        for plan in result.data:
            assert plan.allow_advanced_analysis is True

    def test_list_by_max_employee(self, db_session, sample_plan):
        """Testa listagem por número máximo de funcionários"""
        repo = PlanRepository(db_session)
        
        result = repo.list_by_max_employee(max_employee=5, limit=10)
        
        assert result.data is not None
        for plan in result.data:
            assert plan.max_employee >= 5

    def test_delete_plan(self, db_session, sample_plan):
        """Testa deleção de plano"""
        repo = PlanRepository(db_session)
        
        plan_id = sample_plan.id
        success = repo.delete(plan_id)
        
        assert success is True
        
        # Verifica se foi deletado
        found = repo.get_by_id(plan_id)
        assert found is None

    def test_delete_nonexistent_plan(self, db_session):
        """Testa deleção de plano inexistente"""
        repo = PlanRepository(db_session)
        
        success = repo.delete(99999)
        
        assert success is False
