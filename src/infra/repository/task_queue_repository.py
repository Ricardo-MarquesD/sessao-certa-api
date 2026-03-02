from sqlalchemy import select, delete, func
from sqlalchemy.orm import Session
from domain.entities.task_queue import TaskQueue
from domain.interface.task_queue_interface import TaskQueueInterface
from infra.models.task_queue_orm import TaskQueueModel
from utils.enum import TaskStatus
from utils.value_object import PaginatedResponse, CursorEncoder
from uuid import UUID


class TaskQueueRepository(TaskQueueInterface):

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def _to_entity(self, model: TaskQueueModel) -> TaskQueue:
        return TaskQueue(
            id=model.uuid,
            establishments_id=model.establishments_id,
            task_type=model.task_type,
            priority=model.priority,
            status=model.status,
            payload=model.payload,
            retry_count=model.retry_count,
            max_retry=model.max_retry,
            error_mensage=model.error_mensage,
            next_retry_at=model.next_retry_at,
            result_data=model.result_data,
            created_at=model.created_at,
            started_at=model.started_at,
            completed_at=model.completed_at,
        )

    def _to_orm(self, task: TaskQueue) -> TaskQueueModel:
        return TaskQueueModel(
            uuid=task.id,
            establishments_id=task.establishments_id,
            task_type=task.task_type,
            priority=task.priority,
            status=task.status,
            payload=task.payload,
            retry_count=task.retry_count,
            max_retry=task.max_retry,
            error_mensage=task.error_mensage,
            next_retry_at=task.next_retry_at,
            result_data=task.result_data,
            created_at=task.created_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
        )

    def create(self, task: TaskQueue) -> TaskQueue:
        task_orm = self._to_orm(task)
        self.db_session.add(task_orm)
        self.db_session.commit()
        self.db_session.refresh(task_orm)
        return self._to_entity(task_orm)

    def update(self, task: TaskQueue) -> TaskQueue:
        stmt = select(TaskQueueModel).where(TaskQueueModel.uuid == task.id)
        task_orm = self.db_session.scalar(stmt)

        if not task_orm:
            raise ValueError(f"TaskQueue with id {task.id} not found")

        task_orm.establishments_id = task.establishments_id
        task_orm.task_type = task.task_type
        task_orm.priority = task.priority
        task_orm.status = task.status
        task_orm.payload = task.payload
        task_orm.retry_count = task.retry_count
        task_orm.max_retry = task.max_retry
        task_orm.error_mensage = task.error_mensage
        task_orm.next_retry_at = task.next_retry_at
        task_orm.result_data = task.result_data
        task_orm.started_at = task.started_at
        task_orm.completed_at = task.completed_at

        self.db_session.commit()
        self.db_session.refresh(task_orm)
        return self._to_entity(task_orm)

    def get_by_id(self, task_id: UUID) -> TaskQueue | None:
        stmt = select(TaskQueueModel).where(TaskQueueModel.uuid == task_id)
        result = self.db_session.scalar(stmt)
        return self._to_entity(result) if result else None

    def list_all(self, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[TaskQueue]:
        stmt = select(TaskQueueModel).order_by(TaskQueueModel.id)

        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(TaskQueueModel.id > last_id)

        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(t) for t in data]

        next_cursor = None
        if has_more and data:
            next_cursor = CursorEncoder.encode(data[-1].id, field_name="id")

        return PaginatedResponse(data=entities, cursor=next_cursor, has_more=has_more, total_count=None)

    def list_by_status(self, status: TaskStatus, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[TaskQueue]:
        stmt = select(TaskQueueModel).where(TaskQueueModel.status == status).order_by(TaskQueueModel.id)

        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(TaskQueueModel.id > last_id)

        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(t) for t in data]

        next_cursor = None
        if has_more and data:
            next_cursor = CursorEncoder.encode(data[-1].id, field_name="id")

        return PaginatedResponse(data=entities, cursor=next_cursor, has_more=has_more, total_count=None)

    def list_by_establishment_id(self, establishment_id: int, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[TaskQueue]:
        stmt = select(TaskQueueModel).where(TaskQueueModel.establishments_id == establishment_id).order_by(TaskQueueModel.id)

        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(TaskQueueModel.id > last_id)

        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(t) for t in data]

        next_cursor = None
        if has_more and data:
            next_cursor = CursorEncoder.encode(data[-1].id, field_name="id")

        return PaginatedResponse(data=entities, cursor=next_cursor, has_more=has_more, total_count=None)

    def list_pending_by_priority(self, limit: int = 15) -> list[TaskQueue]:
        stmt = (
            select(TaskQueueModel)
            .where(TaskQueueModel.status == TaskStatus.PENDING)
            .order_by(TaskQueueModel.priority.desc(), TaskQueueModel.created_at)
            .limit(limit)
        )
        results = self.db_session.scalars(stmt).all()
        return [self._to_entity(t) for t in results]

    def list_retryable(self, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[TaskQueue]:
        stmt = (
            select(TaskQueueModel)
            .where(
                TaskQueueModel.status == TaskStatus.FAILED,
                TaskQueueModel.retry_count < TaskQueueModel.max_retry
            )
            .order_by(TaskQueueModel.id)
        )

        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(TaskQueueModel.id > last_id)

        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(t) for t in data]

        next_cursor = None
        if has_more and data:
            next_cursor = CursorEncoder.encode(data[-1].id, field_name="id")

        return PaginatedResponse(data=entities, cursor=next_cursor, has_more=has_more, total_count=None)

    def delete(self, task_id: UUID) -> bool:
        stmt = delete(TaskQueueModel).where(TaskQueueModel.uuid == task_id)
        result = self.db_session.execute(stmt)
        self.db_session.commit()
        return result.rowcount > 0
