import pytest
from domain.entities import Client
from infra.repository import ClientRepository


class TestClientRepository:
    """Testes para ClientRepository"""

    def test_create_client(self, db_session, sample_user, sample_plan):
        """Testa criação de cliente"""
        repo = ClientRepository(db_session)
        
        # Criar entidades User e Plan a partir dos models
        from domain.entities import User, Plan
        user_entity = User(
            id=sample_user.uuid,
            user_name=sample_user.user_name,
            email=sample_user.email,
            phone_number=sample_user.phone_number,
            password_hash=sample_user.password_hash,
            role=sample_user.role,
            active_status=sample_user.active_status,
            img_url=sample_user.img_url,
            created_at=sample_user.create_in,
            updated_at=sample_user.update_in
        )
        
        plan_entity = Plan(
            id=sample_plan.id,
            type_plan=sample_plan.type_plan,
            basic_price=sample_plan.basic_price,
            max_employee=sample_plan.max_employee,
            allow_stock=sample_plan.allow_stock,
            allow_advanced_analysis=sample_plan.allow_advanced_analysis
        )
        
        client = Client(
            id=None,
            user=user_entity,
            plan=plan_entity
        )
        
        created = repo.create(client)
        
        assert created.id is not None
        assert created.user.id == sample_user.uuid
        assert created.plan.id == sample_plan.id

    def test_get_by_id(self, db_session, sample_client):
        """Testa busca por ID"""
        repo = ClientRepository(db_session)
        
        found = repo.get_by_id(sample_client.id)
        
        assert found is not None
        assert found.id == sample_client.id

    def test_get_by_id_not_found(self, db_session):
        """Testa busca por ID inexistente"""
        repo = ClientRepository(db_session)
        
        found = repo.get_by_id(99999)
        
        assert found is None

    def test_get_by_user_id(self, db_session, sample_client, sample_user):
        """Testa busca por user_id"""
        repo = ClientRepository(db_session)
        
        found = repo.get_by_user_id(sample_user.uuid)
        
        assert found is not None
        assert found.user.id == sample_user.uuid

    def test_list_all(self, db_session, sample_client):
        """Testa listagem de todos os clientes"""
        repo = ClientRepository(db_session)
        
        result = repo.list_all(limit=10)
        
        assert result.data is not None
        assert len(result.data) > 0

    def test_list_by_plan_id(self, db_session, sample_client, sample_plan):
        """Testa listagem por plan_id"""
        repo = ClientRepository(db_session)
        
        result = repo.list_by_plan_id(plan_id=sample_plan.id, limit=10)
        
        assert result.data is not None
        for client in result.data:
            assert client.plan.id == sample_plan.id

    def test_update_client(self, db_session, sample_client, sample_plan):
        """Testa atualização de cliente"""
        repo = ClientRepository(db_session)
        
        # Buscar o cliente existente
        existing = repo.get_by_id(sample_client.id)
        
        # Atualizar para um plano diferente (criar um novo plano)
        from infra.models import PlanModel
        from utils.enum import TypePlan
        from decimal import Decimal
        
        new_plan = PlanModel(
            type_plan=TypePlan.GOLD,
            basic_price=Decimal("199.90"),
            max_employee=20,
            allow_stock=True,
            allow_advanced_analysis=True
        )
        db_session.add(new_plan)
        db_session.flush()
        
        from domain.entities import Plan
        new_plan_entity = Plan(
            id=new_plan.id,
            type_plan=new_plan.type_plan,
            basic_price=new_plan.basic_price,
            max_employee=new_plan.max_employee,
            allow_stock=new_plan.allow_stock,
            allow_advanced_analysis=new_plan.allow_advanced_analysis
        )
        
        updated_client = Client(
            id=existing.id,
            user=existing.user,
            plan=new_plan_entity
        )
        
        updated = repo.update(updated_client)
        
        assert updated.plan.id == new_plan.id

    def test_delete_client(self, db_session, sample_client):
        """Testa deleção de cliente"""
        repo = ClientRepository(db_session)
        
        client_id = sample_client.id
        success = repo.delete(client_id)
        
        assert success is True
        
        # Verifica se foi deletado
        found = repo.get_by_id(client_id)
        assert found is None

    def test_delete_nonexistent_client(self, db_session):
        """Testa deleção de cliente inexistente"""
        repo = ClientRepository(db_session)
        
        success = repo.delete(99999)
        
        assert success is False
