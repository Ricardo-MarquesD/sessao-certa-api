from sqlalchemy import select, delete, func
from sqlalchemy.orm import Session
from domain.entities.context import Context
from domain.interface.context_interface import ContextInterface
from infra.models.context_orm import ContextModel
from utils.value_object import PaginatedResponse, CursorEncoder
from datetime import datetime
from uuid import UUID


class ContextRepository(ContextInterface):

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def _to_entity(self, model: ContextModel) -> Context:
        return Context(
            id=model.uuid,
            establishments_id=model.establishments_id,
            customers_id=model.customers_id,
            phone_number=model.phone_number,
            last_message_id=model.last_message_id,
            context_arrow=model.context_arrow,
            is_open=bool(model.is_open),
            context_data=model.context_data,
            created_at=model.created_at,
            updated_at=model.updated_at,
            expires_at=model.expires_at,
        )

    def _to_orm(self, context: Context) -> ContextModel:
        return ContextModel(
            uuid=context.id,
            establishments_id=context.establishments_id,
            customers_id=context.customers_id,
            phone_number=context.phone_number,
            last_message_id=context.last_message_id,
            context_arrow=context.context_arrow,
            is_open=context.is_open,
            context_data=context.context_data,
            expires_at=context.expires_at,
        )

    def create(self, context: Context) -> Context:
        context_orm = self._to_orm(context)
        self.db_session.add(context_orm)
        self.db_session.commit()
        self.db_session.refresh(context_orm)
        return self._to_entity(context_orm)

    def update(self, context: Context) -> Context:
        stmt = select(ContextModel).where(ContextModel.uuid == context.id)
        context_orm = self.db_session.scalar(stmt)

        if not context_orm:
            raise ValueError(f"Context with id {context.id} not found")

        context_orm.customers_id = context.customers_id
        context_orm.phone_number = context.phone_number
        context_orm.last_message_id = context.last_message_id
        context_orm.context_arrow = context.context_arrow
        context_orm.is_open = context.is_open
        context_orm.context_data = context.context_data
        context_orm.expires_at = context.expires_at

        self.db_session.commit()
        self.db_session.refresh(context_orm)
        return self._to_entity(context_orm)

    def get_by_id(self, context_id: UUID) -> Context | None:
        stmt = select(ContextModel).where(ContextModel.uuid == context_id)
        result = self.db_session.scalar(stmt)
        return self._to_entity(result) if result else None

    def get_open_by_phone_number(self, phone_number: str, establishment_id: int) -> Context | None:
        stmt = select(ContextModel).where(
            ContextModel.phone_number == phone_number,
            ContextModel.establishments_id == establishment_id,
            ContextModel.is_open == True
        )
        result = self.db_session.scalar(stmt)
        return self._to_entity(result) if result else None

    def list_all(self, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Context]:
        stmt = select(ContextModel).order_by(ContextModel.id)

        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(ContextModel.id > last_id)

        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(c) for c in data]

        next_cursor = None
        if has_more and data:
            next_cursor = CursorEncoder.encode(data[-1].id, field_name="id")

        return PaginatedResponse(data=entities, cursor=next_cursor, has_more=has_more, total_count=None)

    def list_by_establishment_id(self, establishment_id: int, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Context]:
        stmt = select(ContextModel).where(ContextModel.establishments_id == establishment_id).order_by(ContextModel.id)

        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(ContextModel.id > last_id)

        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(c) for c in data]

        next_cursor = None
        if has_more and data:
            next_cursor = CursorEncoder.encode(data[-1].id, field_name="id")

        return PaginatedResponse(data=entities, cursor=next_cursor, has_more=has_more, total_count=None)

    def list_expired(self, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Context]:
        now = datetime.now()
        stmt = select(ContextModel).where(ContextModel.expires_at <= now).order_by(ContextModel.id)

        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(ContextModel.id > last_id)

        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(c) for c in data]

        next_cursor = None
        if has_more and data:
            next_cursor = CursorEncoder.encode(data[-1].id, field_name="id")

        return PaginatedResponse(data=entities, cursor=next_cursor, has_more=has_more, total_count=None)

    def delete(self, context_id: UUID) -> bool:
        stmt = delete(ContextModel).where(ContextModel.uuid == context_id)
        result = self.db_session.execute(stmt)
        self.db_session.commit()
        return result.rowcount > 0

    def delete_expired(self, establishment_id: int) -> int:
        now = datetime.now()
        stmt = delete(ContextModel).where(
            ContextModel.establishments_id == establishment_id,
            ContextModel.expires_at <= now
        )
        result = self.db_session.execute(stmt)
        self.db_session.commit()
        return result.rowcount
