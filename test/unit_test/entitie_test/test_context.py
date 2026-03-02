import pytest
from datetime import datetime, timedelta
from domain.entities.context import Context


class TestContextEntity:
    """Testes unitários para a entidade Context"""

    @pytest.fixture
    def valid_context(self):
        """Fixture para criar um contexto válido"""
        return Context(
            id="ctx-uuid-123",
            establishments_id=1,
            customers_id=10,
            phone_number="+5511999998888",
            last_message_id="msg-abc-001",
            context_arrow="AWAITING_SERVICE_CHOICE",
            is_open=True,
            context_data={"step": "greeting", "attempts": 0},
            created_at=datetime.now(),
            updated_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1),
        )

    def test_create_context_with_valid_data(self, valid_context):
        """Testa criação de context com dados válidos"""
        assert valid_context.phone_number == "+5511999998888"
        assert valid_context.is_open is True

    def test_create_context_with_short_phone_raises_error(self):
        """Testa que telefone muito curto levanta erro"""
        with pytest.raises(ValueError, match="Phone number is too short"):
            Context(
                id="ctx-123",
                establishments_id=1,
                customers_id=None,
                phone_number="123",
                last_message_id=None,
                context_arrow=None,
                is_open=False,
                context_data=None,
                created_at=None,
                updated_at=None,
                expires_at=datetime.now() + timedelta(hours=1),
            )

    def test_create_context_without_expires_at_raises_error(self):
        """Testa que expires_at inválido levanta erro"""
        with pytest.raises(ValueError, match="expires_at must be a datetime"):
            Context(
                id="ctx-123",
                establishments_id=1,
                customers_id=None,
                phone_number="11999998888",
                last_message_id=None,
                context_arrow=None,
                is_open=False,
                context_data=None,
                created_at=None,
                updated_at=None,
                expires_at="not-a-datetime",
            )

    def test_is_expired_returns_false_when_not_expired(self, valid_context):
        """Testa is_expired() retorna False quando contexto ainda válido"""
        assert valid_context.is_expired() is False

    def test_is_expired_returns_true_when_expired(self, valid_context):
        """Testa is_expired() retorna True quando contexto expirado"""
        valid_context.expires_at = datetime.now() - timedelta(minutes=5)
        assert valid_context.is_expired() is True

    def test_close_sets_is_open_to_false(self, valid_context):
        """Testa close() define is_open como False"""
        assert valid_context.is_open is True
        valid_context.close()
        assert valid_context.is_open is False

    def test_create_context_without_customer(self):
        """Testa criação de context sem customer (customers_id=None)"""
        context = Context(
            id="ctx-456",
            establishments_id=2,
            customers_id=None,
            phone_number="+5511988887777",
            last_message_id=None,
            context_arrow=None,
            is_open=True,
            context_data=None,
            created_at=None,
            updated_at=None,
            expires_at=datetime.now() + timedelta(hours=2),
        )

        assert context.customers_id is None
        assert context.is_open is True

    def test_to_dict_returns_correct_structure(self, valid_context):
        """Testa to_dict() retorna estrutura correta"""
        ctx_dict = valid_context.to_dict()
        assert ctx_dict["phone_number"] == "+5511999998888"
        assert ctx_dict["is_open"] is True
        assert ctx_dict["customers_id"] == 10
        assert "expires_at" in ctx_dict

    def test_from_dict_creates_context_correctly(self):
        """Testa from_dict() cria context corretamente"""
        expires_at = datetime.now() + timedelta(hours=3)
        data = {
            "id": "ctx-789",
            "establishments_id": 3,
            "customers_id": 5,
            "phone_number": "+5511977776666",
            "last_message_id": "msg-xyz",
            "context_arrow": "AWAITING_CONFIRM",
            "is_open": True,
            "context_data": {"key": "value"},
            "created_at": "2026-01-01T10:00:00",
            "updated_at": "2026-01-01T10:05:00",
            "expires_at": expires_at.isoformat(),
        }

        context = Context.from_dict(data)

        assert context.id == "ctx-789"
        assert context.customers_id == 5
        assert context.phone_number == "+5511977776666"
        assert context.is_open is True
