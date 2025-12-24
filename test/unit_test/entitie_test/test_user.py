import pytest
from datetime import datetime
from decimal import Decimal
from domain.entities import User
from utils.enum import UserRole


class TestUserEntity:
    """Testes unitários para a entidade User"""
    
    def test_create_user_with_valid_data(self):
        """Testa criação de usuário com dados válidos"""
        user = User(
            id="123e4567-e89b-12d3-a456-426614174000",
            user_name="João Silva",
            email="joao@example.com",
            phone_number="11987654321",
            password_hash="$2b$12$hashedpassword",
            role=UserRole.CLIENT,
            active_status=True,
            img_url="https://example.com/img.jpg",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert user.user_name == "João Silva"
        assert user.email == "joao@example.com"
        assert user.role == UserRole.CLIENT
        assert user.active_status is True
    
    def test_create_user_with_invalid_email_raises_error(self):
        """Testa que email sem @ levanta erro"""
        with pytest.raises(ValueError, match="Email must contain '@'"):
            User(
                id=None,
                user_name="João Silva",
                email="invalid-email",  # Sem @
                phone_number="11987654321",
                password_hash="$2b$12$hashedpassword",
                role=UserRole.CLIENT,
                active_status=True,
                img_url=None,
                created_at=None,
                updated_at=None
            )
    
    def test_create_user_with_short_email_raises_error(self):
        """Testa que email muito curto levanta erro"""
        with pytest.raises(ValueError, match="Email is too short"):
            User(
                id=None,
                user_name="João Silva",
                email="a@b.c",  # Menos de 10 caracteres
                phone_number="11987654321",
                password_hash="$2b$12$hashedpassword",
                role=UserRole.CLIENT,
                active_status=None,
                img_url=None,
                created_at=None,
                updated_at=None
            )
    
    def test_create_user_with_short_phone_raises_error(self):
        """Testa que telefone muito curto levanta erro"""
        with pytest.raises(ValueError, match="Phone number is too short"):
            User(
                id=None,
                user_name="João Silva",
                email="joao@example.com",
                phone_number="123",  # Menos de 8 caracteres
                password_hash="$2b$12$hashedpassword",
                role=UserRole.CLIENT,
                active_status=None,
                img_url=None,
                created_at=None,
                updated_at=None
            )
    
    def test_create_user_with_invalid_role_raises_error(self):
        """Testa que role inválido levanta erro"""
        with pytest.raises(ValueError, match="User Role is incorrect"):
            User(
                id=None,
                user_name="João Silva",
                email="joao@example.com",
                phone_number="11987654321",
                password_hash="$2b$12$hashedpassword",
                role="INVALID_ROLE",  # Não é um UserRole
                active_status=None,
                img_url=None,
                created_at=None,
                updated_at=None
            )
    
    def test_is_active_returns_true_when_active(self):
        """Testa is_active() retorna True quando ativo"""
        user = User(
            id=None,
            user_name="João Silva",
            email="joao@example.com",
            phone_number="11987654321",
            password_hash="$2b$12$hashedpassword",
            role=UserRole.CLIENT,
            active_status=True,
            img_url=None,
            created_at=None,
            updated_at=None
        )
        
        assert user.is_active() is True
    
    def test_is_active_returns_false_when_inactive(self):
        """Testa is_active() retorna False quando inativo"""
        user = User(
            id=None,
            user_name="João Silva",
            email="joao@example.com",
            phone_number="11987654321",
            password_hash="$2b$12$hashedpassword",
            role=UserRole.CLIENT,
            active_status=False,
            img_url=None,
            created_at=None,
            updated_at=None
        )
        
        assert user.is_active() is False
    
    def test_is_active_returns_false_when_none(self):
        """Testa is_active() retorna False quando None"""
        user = User(
            id=None,
            user_name="João Silva",
            email="joao@example.com",
            phone_number="11987654321",
            password_hash="$2b$12$hashedpassword",
            role=UserRole.CLIENT,
            active_status=None,
            img_url=None,
            created_at=None,
            updated_at=None
        )
        
        assert user.is_active() is False
    
    def test_activate_sets_status_to_true(self):
        """Testa activate() define active_status como True"""
        user = User(
            id=None,
            user_name="João Silva",
            email="joao@example.com",
            phone_number="11987654321",
            password_hash="$2b$12$hashedpassword",
            role=UserRole.CLIENT,
            active_status=False,
            img_url=None,
            created_at=None,
            updated_at=None
        )
        
        user.activate()
        
        assert user.active_status is True
    
    def test_deactivate_sets_status_to_false(self):
        """Testa deactivate() define active_status como False"""
        user = User(
            id=None,
            user_name="João Silva",
            email="joao@example.com",
            phone_number="11987654321",
            password_hash="$2b$12$hashedpassword",
            role=UserRole.CLIENT,
            active_status=True,
            img_url=None,
            created_at=None,
            updated_at=None
        )
        
        user.deactivate()
        
        assert user.active_status is False
    
    def test_update_password_changes_password_hash(self):
        """Testa update_password() altera o password_hash"""
        user = User(
            id=None,
            user_name="João Silva",
            email="joao@example.com",
            phone_number="11987654321",
            password_hash="old_hash",
            role=UserRole.CLIENT,
            active_status=True,
            img_url=None,
            created_at=None,
            updated_at=None
        )
        
        user.update_password("NewPassword123")
        
        assert user.password_hash != "old_hash"
        assert user.password_hash.startswith("$2b$")  # bcrypt hash
    
    def test_to_dict_returns_correct_structure(self):
        """Testa to_dict() retorna dicionário correto"""
        now = datetime.now()
        user = User(
            id="123",
            user_name="João Silva",
            email="joao@example.com",
            phone_number="11987654321",
            password_hash="$2b$12$hashedpassword",
            role=UserRole.CLIENT,
            active_status=True,
            img_url="https://example.com/img.jpg",
            created_at=now,
            updated_at=now
        )
        
        user_dict = user.to_dict()
        
        assert user_dict["id"] == "123"
        assert user_dict["user_name"] == "João Silva"
        assert user_dict["email"] == "joao@example.com"
        assert user_dict["role"] == "CLIENT"
        assert user_dict["active_status"] is True
    
    def test_from_dict_creates_user_correctly(self):
        """Testa from_dict() cria usuário corretamente"""
        data = {
            "id": "123",
            "user_name": "João Silva",
            "email": "joao@example.com",
            "phone_number": "11987654321",
            "password_hash": "$2b$12$hashedpassword",
            "role": "CLIENT",
            "active_status": True,
            "img_url": "https://example.com/img.jpg",
            "created_at": "2025-12-24 10:00:00",
            "updated_at": "2025-12-24 10:00:00"
        }
        
        user = User.from_dict(data)
        
        assert user.id == "123"
        assert user.user_name == "João Silva"
        assert user.role == UserRole.CLIENT
        assert user.active_status is True
