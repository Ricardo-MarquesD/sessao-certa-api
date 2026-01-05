import pytest
from uuid import uuid4
from domain.entities import User
from infra.repository import UserRepository
from utils.enum import UserRole


class TestUserRepository:
    """Testes para UserRepository"""

    def test_create_user(self, db_session):
        """Testa criação de usuário"""
        repo = UserRepository(db_session)
        
        user = User(
            id=None,
            user_name="João Silva",
            email="joao@test.com",
            phone_number="11987654321",
            password_hash="hashed_pwd",
            role=UserRole.CLIENT,
            active_status=True,
            img_url="http://example.com/image.jpg",
            created_at=None,
            updated_at=None
        )
        
        created = repo.create(user)
        
        assert created.id is not None
        assert created.user_name == "João Silva"
        assert created.email == "joao@test.com"
        assert created.role == UserRole.CLIENT

    def test_update_user(self, db_session, sample_user):
        """Testa atualização de usuário"""
        repo = UserRepository(db_session)
        
        user_entity = User(
            id=sample_user.uuid,
            user_name="Nome Atualizado",
            email="novo@test.com",
            phone_number="11999998888",
            password_hash="new_hash",
            role=UserRole.ADMIN,
            active_status=False,
            img_url="/uploads/new.png",
            created_at=sample_user.create_in,
            updated_at=sample_user.update_in
        )
        
        updated = repo.update(user_entity)
        
        assert updated.user_name == "Nome Atualizado"
        assert updated.email == "novo@test.com"
        assert updated.role == UserRole.ADMIN
        assert updated.active_status is False

    def test_get_by_id(self, db_session, sample_user):
        """Testa busca por ID"""
        repo = UserRepository(db_session)
        
        found = repo.get_by_id(sample_user.uuid)
        
        assert found is not None
        assert found.id == sample_user.uuid
        assert found.user_name == sample_user.user_name

    def test_get_by_id_not_found(self, db_session):
        """Testa busca por ID inexistente"""
        repo = UserRepository(db_session)
        
        found = repo.get_by_id(uuid4())
        
        assert found is None

    def test_get_by_email(self, db_session, sample_user):
        """Testa busca por email"""
        repo = UserRepository(db_session)
        
        found = repo.get_by_email(sample_user.email)
        
        assert found is not None
        assert found.email == sample_user.email

    def test_get_by_email_not_found(self, db_session):
        """Testa busca por email inexistente"""
        repo = UserRepository(db_session)
        
        found = repo.get_by_email("naoexiste@test.com")
        
        assert found is None

    def test_get_by_phone_number(self, db_session, sample_user):
        """Testa busca por telefone"""
        repo = UserRepository(db_session)
        
        found = repo.get_by_phone_number(sample_user.phone_number)
        
        assert found is not None
        assert found.phone_number == sample_user.phone_number

    def test_list_all(self, db_session, sample_user):
        """Testa listagem de todos os usuários"""
        repo = UserRepository(db_session)
        
        result = repo.list_all(limit=10)
        
        assert result.data is not None
        assert len(result.data) > 0
        assert result.has_more is not None

    def test_list_all_with_cursor(self, db_session, sample_user):
        """Testa listagem com cursor"""
        repo = UserRepository(db_session)
        
        # Primeira página
        page1 = repo.list_all(limit=1)
        assert len(page1.data) == 1
        
        # Se houver mais dados
        if page1.has_more:
            page2 = repo.list_all(cursor=page1.cursor, limit=1)
            assert len(page2.data) <= 1

    def test_list_all_by_active(self, db_session, sample_user):
        """Testa listagem por status ativo"""
        repo = UserRepository(db_session)
        
        result = repo.list_all_by_active(active_status=True, limit=10)
        
        assert result.data is not None
        for user in result.data:
            assert user.active_status is True

    def test_list_by_role(self, db_session, sample_user):
        """Testa listagem por role"""
        repo = UserRepository(db_session)
        
        result = repo.list_by_role(role=UserRole.CLIENT, limit=10)
        
        assert result.data is not None
        for user in result.data:
            assert user.role == UserRole.CLIENT

    def test_search_by_user_name(self, db_session, sample_user):
        """Testa busca parcial por nome"""
        repo = UserRepository(db_session)
        
        result = repo.search_by_user_name("Test", limit=10)
        
        assert result.data is not None
        assert len(result.data) > 0

    def test_delete_user(self, db_session, sample_user):
        """Testa deleção de usuário"""
        repo = UserRepository(db_session)
        
        user_uuid = sample_user.uuid
        success = repo.delete(user_uuid)
        
        # O delete só funciona se active_status=False, sample_user tem True
        assert success is False
        
        # Verifica que não foi deletado (pois active_status=True)
        found = repo.get_by_id(user_uuid)
        assert found is not None

    def test_delete_nonexistent_user(self, db_session):
        """Testa deleção de usuário inexistente"""
        repo = UserRepository(db_session)
        
        success = repo.delete(uuid4())
        
        # Deve retornar False pois o usuário não existe
        assert success is False
