from __future__ import annotations

from dataclasses import is_dataclass
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Callable
from uuid import UUID

from sqlalchemy.orm import Session

from domain.entities import Context, TaskQueue
from domain.service.whatsapp_service import WhatsappService
from domain.service.google_calendar_service import GoogleCalendarService
from infra.repository import ContextRepository, TaskQueueRepository
from utils.enum import MachineAnwser, TaskStatus, TaskType


class TaskWorker:

    def __init__(self, session_factory: Callable[[], Session], *, concurrency: int = 4, task_limit: int = 20):
        self.session_factory = session_factory
        self.concurrency = max(1, concurrency)
        self.task_limit = max(1, task_limit)
        self._handlers = {
            TaskType.PROCESS_MESSAGE: self._handle_process_message,
            TaskType.SEND_MENSAGE: self._handle_send_message,
            TaskType.SYNC_CALENDAR: self._handle_sync_calendar,
        }

    def run_once(self) -> list[TaskQueue]:
        session = self.session_factory()
        try:
            repository = TaskQueueRepository(session)
            pending_tasks = repository.list_pending_by_priority(limit=self.task_limit)
            retryable_tasks = repository.list_retryable(limit=self.task_limit).data
            candidates = self._filter_ready_tasks(pending_tasks + retryable_tasks)
        finally:
            session.close()

        if not candidates:
            return []

        processed_tasks: list[TaskQueue] = []
        with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            futures = [executor.submit(self._process_task, task.id) for task in candidates if task.id is not None]
            for future in as_completed(futures):
                processed_tasks.append(future.result())

        return processed_tasks

    def _filter_ready_tasks(self, tasks: list[TaskQueue]) -> list[TaskQueue]:
        now = datetime.now()
        ready_tasks: dict[UUID, TaskQueue] = {}

        for task in tasks:
            if task.id is None:
                continue

            if task.status == TaskStatus.FAILED and task.next_retry_at and task.next_retry_at > now:
                continue

            if task.status == TaskStatus.PENDING or task.is_retryable():
                ready_tasks[task.id] = task

        return list(ready_tasks.values())

    def _process_task(self, task_id: UUID) -> TaskQueue:
        session = self.session_factory()
        try:
            repository = TaskQueueRepository(session)
            task = repository.get_by_id(task_id)
            if task is None:
                raise ValueError(f"TaskQueue with id {task_id} not found")

            if not self._is_processable(task):
                return task

            task.started_at = datetime.now()
            task.status = TaskStatus.PROCESSING
            repository.update(task)

            try:
                result = self._dispatch(task, session)
            except Exception as exc:
                task.retry_count += 1
                task.status = TaskStatus.FAILED
                task.error_mensage = str(exc)
                task.next_retry_at = datetime.now()
                repository.update(task)
                return task

            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result_data = self._serialize_result(result)
            task.error_mensage = None
            task.next_retry_at = None
            repository.update(task)
            return task
        finally:
            session.close()

    def _is_processable(self, task: TaskQueue) -> bool:
        now = datetime.now()

        if task.status == TaskStatus.PENDING:
            return True

        if task.status == TaskStatus.FAILED and task.is_retryable():
            return task.next_retry_at is None or task.next_retry_at <= now

        return False

    def _dispatch(self, task: TaskQueue, session: Session):
        handler = self._handlers.get(task.task_type)
        if handler is None:
            raise ValueError(f"Unsupported task type: {task.task_type.value}")

        return handler(task, session)

    def _serialize_result(self, result):
        if isinstance(result, dict):
            return result

        if is_dataclass(result):
            return {
                "anwser": result.anwser,
                "next_state": result.next_state.value if result.next_state is not None else None,
                "is_end": result.is_end,
                "data": result.data,
            }

        return {"result": str(result)}

    def _handle_process_message(self, task: TaskQueue, session: Session) -> MachineAnwser:
        payload = task.payload or {}
        context_id = payload.get("context_id")
        message = payload.get("message", "")

        if not context_id:
            raise ValueError("process_message task payload missing context_id")

        context = ContextRepository(session).get_by_id(UUID(str(context_id)))
        if context is None:
            raise ValueError(f"Context with id {context_id} not found")

        return asyncio.run(WhatsappService.process_message(context=context, message=message, db=session))

    def _handle_send_message(self, task: TaskQueue, session: Session):
        payload = task.payload or {}
        chatbot_phone_number = payload.get("chatbot_phone_number")
        wa_id = payload.get("wa_id")
        message = payload.get("message")
        token = payload.get("token")

        if not all([chatbot_phone_number, wa_id, message, token]):
            raise ValueError("send_mensage task payload missing required fields")

        return asyncio.run(
            WhatsappService.send_message(
                chatbot_phone_number=chatbot_phone_number,
                wa_id=wa_id,
                message=message,
                token=token,
            )
        )

    def _handle_sync_calendar(self, task: TaskQueue, session: Session):
        payload = task.payload or {}
        scheduling_id = payload.get("scheduling_id")
        action = payload.get("action")

        if not scheduling_id:
            raise ValueError("sync_calendar task payload missing scheduling_id")

        if action not in {"create", "update", "cancel"}:
            raise ValueError("sync_calendar task payload missing valid action")

        return asyncio.run(GoogleCalendarService.sync_scheduling(UUID(str(scheduling_id)), action, session))