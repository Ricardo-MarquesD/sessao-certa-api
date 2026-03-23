from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from domain.entities import Context, TaskQueue
from utils.enum import TaskStatus, TaskType


class TaskQueueFactory:

    DEFAULT_PRIORITY = 0
    DEFAULT_MAX_RETRY = 3

    @staticmethod
    def _build_task(*, establishments_id: int, task_type: TaskType, payload: dict, priority: int, max_retry: int) -> TaskQueue:
        now = datetime.now()
        return TaskQueue(
            id=uuid4(),
            establishments_id=establishments_id,
            task_type=task_type,
            priority=priority,
            status=TaskStatus.PENDING,
            payload=payload,
            retry_count=0,
            max_retry=max_retry,
            error_mensage=None,
            next_retry_at=None,
            result_data=None,
            created_at=now,
            started_at=None,
            completed_at=None,
        )

    @staticmethod
    def process_message(context: Context, message: str, *, priority: int = DEFAULT_PRIORITY, max_retry: int = DEFAULT_MAX_RETRY) -> TaskQueue:
        if context.id is None:
            raise ValueError("Context id is required to create a process_message task")

        payload = {
            "context_id": str(context.id),
            "message": message,
        }
        return TaskQueueFactory._build_task(
            establishments_id=context.establishments_id,
            task_type=TaskType.PROCESS_MESSAGE,
            payload=payload,
            priority=priority,
            max_retry=max_retry,
        )

    @staticmethod
    def send_message(
        *,
        establishments_id: int,
        chatbot_phone_number: str,
        wa_id: str,
        message: str,
        token: str,
        priority: int = DEFAULT_PRIORITY,
        max_retry: int = DEFAULT_MAX_RETRY,
    ) -> TaskQueue:
        payload = {
            "chatbot_phone_number": chatbot_phone_number,
            "wa_id": wa_id,
            "message": message,
            "token": token,
        }
        return TaskQueueFactory._build_task(
            establishments_id=establishments_id,
            task_type=TaskType.SEND_MENSAGE,
            payload=payload,
            priority=priority,
            max_retry=max_retry,
        )
