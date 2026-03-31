import asyncio
from datetime import datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest

from domain.entities import Context
from utils.enum import FlowState, MachineAnwser
from domain.service import whatsapp_service as whatsapp_service_module
from domain.service.whatsapp_service import WhatsappService


class FakeContextRepository:
    def __init__(self):
        self.updated_contexts = []
        self.created_contexts = []

    def update(self, context):
        self.updated_contexts.append(context)
        return context

    def create(self, context):
        self.created_contexts.append(context)
        return context


class FakeRepositoryHolder:
    def __init__(self, *, has_scheduling=False):
        self.scheduling_repository = SimpleNamespace(
            list_active_by_customer_internal_id=lambda customer_id: [object()] if has_scheduling else []
        )
        self.establishment_repository = SimpleNamespace()
        self.customer_repository = SimpleNamespace()
        self.initial_message = asyncio.coroutine(lambda *args, **kwargs: None)


def make_context(*, arrow=FlowState.initial_message.value, customer_id=10, is_open=True):
    return Context(
        id=uuid4(),
        establishments_id=1,
        customers_id=customer_id,
        phone_number="11999999999",
        last_message_id=None,
        context_arrow=arrow,
        is_open=is_open,
        context_data={"foo": "bar"},
        created_at=datetime.now(),
        updated_at=datetime.now(),
        expires_at=datetime.now() + timedelta(days=1),
    )


@pytest.mark.parametrize(
    "current_state,method_name,answer,expected_has_scheduling",
    [
        (
            FlowState.initial_message.value,
            "initial_message",
            MachineAnwser(anwser="Olá", next_state=FlowState.service_message, is_end=False, data={"step": 1}),
            True,
        ),
        (
            FlowState.service_message.value,
            "service_message",
            MachineAnwser(anwser="Escolha um serviço", next_state=FlowState.confirm_message, is_end=True, data=None),
            False,
        ),
    ],
)
def test_process_message_routes_and_sends(monkeypatch, current_state, method_name, answer, expected_has_scheduling):
    context = make_context(arrow=current_state)
    db = object()
    fake_repo = FakeContextRepository()

    class FakeStateMachine:
        def __init__(self, context, message, db):
            self.context = context
            self.message = message
            self.db = db
            self.scheduling_repository = SimpleNamespace(
                list_active_by_customer_internal_id=lambda customer_id: [object()] if expected_has_scheduling else []
            )
            self.customer_repository = SimpleNamespace()
            self.establishment_repository = SimpleNamespace()
            setattr(self, method_name, self._method)

        def _method(self, *args, **kwargs):
            self.called_args = args
            self.called_kwargs = kwargs
            return answer

    fake_state_machine = FakeStateMachine(context, "oi", db)
    fake_state_machine._method = getattr(fake_state_machine, method_name)

    sent_messages = []

    async def fake_send_message(chatbot_phone_number, wa_id, message, token):
        sent_messages.append(
            {
                "chatbot_phone_number": chatbot_phone_number,
                "wa_id": wa_id,
                "message": message,
                "token": token,
            }
        )
        return {"ok": True}

    monkeypatch.setattr(whatsapp_service_module, "StateMachine", lambda context, message, db: fake_state_machine)
    monkeypatch.setattr(whatsapp_service_module.WhatsappService, "send_message", staticmethod(fake_send_message))
    monkeypatch.setattr(
        whatsapp_service_module.WhatsappService,
        "_resolve_recipient",
        staticmethod(lambda state_machine, context: ("5511999999999", "5511988888888", "token-123")),
    )
    monkeypatch.setattr(whatsapp_service_module, "ContextRepository", lambda db: fake_repo)

    result = asyncio.run(WhatsappService.process_message(context=context, message="oi", db=db))

    assert result == answer
    assert sent_messages == [
        {
            "chatbot_phone_number": "5511999999999",
            "wa_id": "5511988888888",
            "message": answer.anwser,
            "token": "token-123",
        }
    ]

    if answer.is_end:
        assert context.is_open is False
    else:
        assert context.is_open is True

    assert context.context_arrow == answer.next_state.value
    if answer.data not in (None, {}):
        assert context.context_data == answer.data
    else:
        assert context.context_data == {"foo": "bar"}

    assert fake_repo.updated_contexts or fake_repo.created_contexts


def test_process_message_falls_back_to_initial_state(monkeypatch):
    context = make_context(arrow="invalid_state")
    db = object()
    fake_repo = FakeContextRepository()

    class FakeStateMachine:
        def __init__(self, context, message, db):
            self.context = context
            self.message = message
            self.db = db
            self.scheduling_repository = SimpleNamespace(list_active_by_customer_internal_id=lambda customer_id: [])
            self.customer_repository = SimpleNamespace()
            self.establishment_repository = SimpleNamespace()

        def initial_message(self, *, single, has_scheduling):
            self.called = {"single": single, "has_scheduling": has_scheduling}
            return MachineAnwser(
                anwser="Menu inicial",
                next_state=FlowState.initial_message,
                is_end=False,
                data=None,
            )

    fake_state_machine = FakeStateMachine(context, "oi", db)

    sent_messages = []

    async def fake_send_message(chatbot_phone_number, wa_id, message, token):
        sent_messages.append(message)
        return {"ok": True}

    monkeypatch.setattr(whatsapp_service_module, "StateMachine", lambda context, message, db: fake_state_machine)
    monkeypatch.setattr(whatsapp_service_module.WhatsappService, "send_message", staticmethod(fake_send_message))
    monkeypatch.setattr(
        whatsapp_service_module.WhatsappService,
        "_resolve_recipient",
        staticmethod(lambda state_machine, context: ("5511999999999", "5511988888888", "token-123")),
    )
    monkeypatch.setattr(whatsapp_service_module, "ContextRepository", lambda db: fake_repo)

    result = asyncio.run(WhatsappService.process_message(context=context, message="oi", db=db))

    assert result.anwser == "Menu inicial"
    assert sent_messages == ["Menu inicial"]


def test_unsubscribe_webhook_success(monkeypatch):
    called = {}

    class FakeResponse:
        status = 200
        content_length = 0

        def raise_for_status(self):
            return None

        async def json(self):
            return {"success": True}

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

    class FakeSession:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        def delete(self, url, headers):
            called["url"] = url
            called["headers"] = headers
            return FakeResponse()

    monkeypatch.setattr(whatsapp_service_module.aiohttp, "ClientSession", FakeSession)

    result = asyncio.run(WhatsappService.unsubscribe_webhook("waba-123", "token-xyz"))

    assert result is None
    assert called["url"].endswith("/waba-123/subscribed_apps")
    assert called["headers"]["Authorization"] == "Bearer token-xyz"


def test_unsubscribe_webhook_meta_error(monkeypatch):
    class FakeResponse:
        status = 200
        content_length = 10

        def raise_for_status(self):
            return None

        async def json(self):
            return {"error": {"message": "Invalid token"}}

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

    class FakeSession:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        def delete(self, url, headers):
            return FakeResponse()

    monkeypatch.setattr(whatsapp_service_module.aiohttp, "ClientSession", FakeSession)

    with pytest.raises(ValueError, match="Meta API error"):
        asyncio.run(WhatsappService.unsubscribe_webhook("waba-123", "token-xyz"))
