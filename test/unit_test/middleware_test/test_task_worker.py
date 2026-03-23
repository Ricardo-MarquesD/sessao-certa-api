from datetime import datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest

from domain.entities import Context, TaskQueue
from middleware.task_worker import TaskWorker
from utils.enum import TaskStatus, TaskType


class FakeSession:
    def close(self):
        return None


class FakeTaskQueueRepository:
    store: dict = {}
    updated_tasks: list = []

    def __init__(self, session):
        self.session = session

    @classmethod
    def seed(cls, tasks):
        cls.store = {task.id: task for task in tasks if task.id is not None}
        cls.updated_tasks = []

    def list_pending_by_priority(self, limit=15):
        pending = [task for task in self.store.values() if task.status == TaskStatus.PENDING]
        pending.sort(key=lambda task: (-task.priority, task.created_at or datetime.min))
        return pending[:limit]

    def list_retryable(self, cursor=None, limit=15):
        retryable = [task for task in self.store.values() if task.status == TaskStatus.FAILED and task.retry_count < task.max_retry]
        retryable.sort(key=lambda task: task.created_at or datetime.min)
        return SimpleNamespace(data=retryable[:limit])

    def get_by_id(self, task_id):
        return self.store.get(task_id)

    def update(self, task):
        self.store[task.id] = task
        self.updated_tasks.append(task)
        return task


class FakeContextRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, context_id):
        return self.session.contexts.get(context_id)


def make_context():
    return Context(
        id=uuid4(),
        establishments_id=3,
        customers_id=11,
        phone_number="11999990000",
        last_message_id=None,
        context_arrow=None,
        is_open=True,
        context_data={},
        created_at=datetime.now(),
        updated_at=datetime.now(),
        expires_at=datetime.now() + timedelta(days=1),
    )


def make_task(*, task_type, payload, priority=0, status=TaskStatus.PENDING, retry_count=0, max_retry=3, created_at=None, next_retry_at=None):
    return TaskQueue(
        id=uuid4(),
        establishments_id=3,
        task_type=task_type,
        priority=priority,
        status=status,
        payload=payload,
        retry_count=retry_count,
        max_retry=max_retry,
        error_mensage=None,
        next_retry_at=next_retry_at,
        result_data=None,
        created_at=created_at or datetime.now(),
        started_at=None,
        completed_at=None,
    )


def build_worker(monkeypatch, session_contexts, tasks, process_result=None, send_result=None):
    FakeTaskQueueRepository.seed(tasks)

    monkeypatch.setattr("middleware.task_worker.TaskQueueRepository", FakeTaskQueueRepository)
    monkeypatch.setattr("middleware.task_worker.ContextRepository", FakeContextRepository)

    async def fake_process_message(context, message, db):
        return process_result or {"answer": message, "context_id": str(context.id)}

    async def fake_send_message(chatbot_phone_number, wa_id, message, token):
        return send_result or {"chatbot_phone_number": chatbot_phone_number, "wa_id": wa_id, "message": message, "token": token}

    monkeypatch.setattr("middleware.task_worker.WhatsappService.process_message", staticmethod(fake_process_message))
    monkeypatch.setattr("middleware.task_worker.WhatsappService.send_message", staticmethod(fake_send_message))

    def make_session():
        session = FakeSession()
        session.contexts = session_contexts
        return session

    worker = TaskWorker(session_factory=make_session, concurrency=2, task_limit=10)
    return worker


def test_run_once_processes_message_and_send_tasks(monkeypatch):
    context = make_context()
    process_task = make_task(
        task_type=TaskType.PROCESS_MESSAGE,
        payload={"context_id": str(context.id), "message": "oi"},
        priority=10,
    )
    send_task = make_task(
        task_type=TaskType.SEND_MENSAGE,
        payload={
            "chatbot_phone_number": "5511999999999",
            "wa_id": "5511888888888",
            "message": "resposta",
            "token": "token-123",
        },
        priority=1,
    )

    worker = build_worker(monkeypatch, {context.id: context}, [process_task, send_task])

    processed = worker.run_once()

    processed_by_type = {task.task_type: task for task in processed}
    assert processed_by_type[TaskType.PROCESS_MESSAGE].status == TaskStatus.COMPLETED
    assert processed_by_type[TaskType.SEND_MENSAGE].status == TaskStatus.COMPLETED
    assert processed_by_type[TaskType.PROCESS_MESSAGE].result_data["answer"] == "oi"
    assert processed_by_type[TaskType.SEND_MENSAGE].result_data["message"] == "resposta"
    assert FakeTaskQueueRepository.store[process_task.id].completed_at is not None
    assert FakeTaskQueueRepository.store[send_task.id].completed_at is not None


def test_run_once_marks_failed_tasks_and_skips_future_retry(monkeypatch):
    context = make_context()
    failing_task = make_task(
        task_type=TaskType.SEND_MENSAGE,
        payload={"chatbot_phone_number": "5511999999999", "wa_id": "5511888888888", "message": "resposta"},
        status=TaskStatus.PENDING,
    )
    future_retry_task = make_task(
        task_type=TaskType.PROCESS_MESSAGE,
        payload={"context_id": str(context.id), "message": "oi"},
        status=TaskStatus.FAILED,
        retry_count=1,
        next_retry_at=datetime.now() + timedelta(hours=1),
    )

    worker = build_worker(monkeypatch, {context.id: context}, [failing_task, future_retry_task])

    processed = worker.run_once()

    assert len(processed) == 1
    stored_failed_task = FakeTaskQueueRepository.store[failing_task.id]
    assert stored_failed_task.status == TaskStatus.FAILED
    assert stored_failed_task.retry_count == 1
    assert stored_failed_task.error_mensage == "send_mensage task payload missing required fields"
    assert FakeTaskQueueRepository.store[future_retry_task.id].status == TaskStatus.FAILED
    assert FakeTaskQueueRepository.store[future_retry_task.id].retry_count == 1