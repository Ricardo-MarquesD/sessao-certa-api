from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from domain.entities import Context
from middleware.task_queue import TaskQueueFactory
from utils.enum import TaskStatus, TaskType


@pytest.fixture
def sample_context():
    return Context(
        id=uuid4(),
        establishments_id=7,
        customers_id=15,
        phone_number="11999999999",
        last_message_id=None,
        context_arrow=None,
        is_open=True,
        context_data={},
        created_at=datetime.now(),
        updated_at=datetime.now(),
        expires_at=datetime.now() + timedelta(days=1),
    )


def test_process_message_factory_builds_normalized_task(sample_context):
    task = TaskQueueFactory.process_message(sample_context, "oi", priority=4, max_retry=5)

    assert task.task_type == TaskType.PROCESS_MESSAGE
    assert task.establishments_id == sample_context.establishments_id
    assert task.status == TaskStatus.PENDING
    assert task.priority == 4
    assert task.retry_count == 0
    assert task.max_retry == 5
    assert task.payload["context_id"] == str(sample_context.id)
    assert task.payload["message"] == "oi"
    assert task.created_at is not None
    assert task.id is not None


def test_process_message_factory_requires_context_id(sample_context):
    sample_context.id = None

    with pytest.raises(ValueError, match="Context id is required"):
        TaskQueueFactory.process_message(sample_context, "oi")


def test_send_message_factory_builds_normalized_task():
    task = TaskQueueFactory.send_message(
        establishments_id=9,
        chatbot_phone_number="5511999999999",
        wa_id="5511888888888",
        message="Resposta",
        token="token-123",
        priority=2,
        max_retry=6,
    )

    assert task.task_type == TaskType.SEND_MENSAGE
    assert task.establishments_id == 9
    assert task.status == TaskStatus.PENDING
    assert task.priority == 2
    assert task.max_retry == 6
    assert task.payload == {
        "chatbot_phone_number": "5511999999999",
        "wa_id": "5511888888888",
        "message": "Resposta",
        "token": "token-123",
    }