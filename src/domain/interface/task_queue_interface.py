from abc import ABC, abstractmethod
from domain.entities.task_queue import TaskQueue
from utils.enum import TaskStatus, TaskType
from utils.value_object import PaginatedResponse
from uuid import UUID
from datetime import datetime


class TaskQueueInterface(ABC):

    @abstractmethod
    def create(self, task: TaskQueue) -> TaskQueue:
        pass

    @abstractmethod
    def update(self, task: TaskQueue) -> TaskQueue:
        pass

    @abstractmethod
    def get_by_id(self, task_id: UUID) -> TaskQueue | None:
        pass

    @abstractmethod
    def list_all(self, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[TaskQueue]:
        pass

    @abstractmethod
    def list_by_status(self, status: TaskStatus, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[TaskQueue]:
        pass

    @abstractmethod
    def list_by_establishment_id(self, establishment_id: int, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[TaskQueue]:
        pass

    @abstractmethod
    def list_pending_by_priority(self, limit: int = 15) -> list[TaskQueue]:
        pass

    @abstractmethod
    def list_retryable(self, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[TaskQueue]:
        pass

    @abstractmethod
    def delete(self, task_id: UUID) -> bool:
        pass
