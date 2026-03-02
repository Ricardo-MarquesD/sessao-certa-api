from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import Any
from utils.enum import TaskType, TaskStatus


@dataclass
class TaskQueue:
    id: UUID | None
    establishments_id: int
    task_type: TaskType
    priority: int
    status: TaskStatus
    payload: dict
    retry_count: int
    max_retry: int
    error_mensage: str | None
    next_retry_at: datetime | None
    result_data: dict | None
    created_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None

    def __post_init__(self):
        if not isinstance(self.task_type, TaskType):
            raise ValueError("task_type must be a TaskType enum")
        if not isinstance(self.status, TaskStatus):
            raise ValueError("status must be a TaskStatus enum")
        if not isinstance(self.payload, dict):
            raise ValueError("payload must be a dict")
        if self.priority < 0:
            raise ValueError("priority must be a non-negative integer")

    def is_retryable(self) -> bool:
        return self.retry_count < self.max_retry and self.status == TaskStatus.FAILED

    def can_process(self) -> bool:
        return self.status == TaskStatus.PENDING

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "establishments_id": self.establishments_id,
            "task_type": self.task_type.value,
            "priority": self.priority,
            "status": self.status.value,
            "payload": self.payload,
            "retry_count": self.retry_count,
            "max_retry": self.max_retry,
            "error_mensage": self.error_mensage,
            "next_retry_at": self.next_retry_at.isoformat() if self.next_retry_at else None,
            "result_data": self.result_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    @staticmethod
    def from_dict(data: dict) -> TaskQueue:
        task_type_data = data.get("task_type")
        status_data = data.get("status")

        return TaskQueue(
            id=data.get("id"),
            establishments_id=data.get("establishments_id"),
            task_type=TaskType(task_type_data) if isinstance(task_type_data, str) else task_type_data,
            priority=data.get("priority", 0),
            status=TaskStatus(status_data) if isinstance(status_data, str) else status_data,
            payload=data.get("payload", {}),
            retry_count=data.get("retry_count", 0),
            max_retry=data.get("max_retry", 3),
            error_mensage=data.get("error_mensage"),
            next_retry_at=datetime.fromisoformat(data["next_retry_at"]) if data.get("next_retry_at") else None,
            result_data=data.get("result_data"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
        )
