from sqlalchemy import select, delete, func
from sqlalchemy.orm import Session
from domain.entities import MarketingMessage
from domain.interface import MarketingMessageInterface
from infra.models import MarketingMessageModel, EstablishmentModel
from utils.value_object import PaginatedResponse, CursorEncoder
from .entity_mapper import EntityMapper
from uuid import UUID

class MarketingMessageRepository(MarketingMessageInterface):

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def _to_entity(self, marketing_message_model: MarketingMessageModel) -> MarketingMessage:
        establishment = EntityMapper.establishment_to_entity(marketing_message_model.establishment)
        
        return MarketingMessage(
            id=marketing_message_model.id,
            establishment=establishment,
            title=marketing_message_model.title,
            content=marketing_message_model.content
        )
    
    def _to_orm(self, marketing_message: MarketingMessage) -> MarketingMessageModel:
        stmt = select(EstablishmentModel.id).where(EstablishmentModel.uuid == marketing_message.establishment.id)
        establishment_internal_id = self.db_session.scalar(stmt)
        
        if not establishment_internal_id:
            raise ValueError(f"Establishment with uuid {marketing_message.establishment.id} not found")
        
        return MarketingMessageModel(
            id=marketing_message.id,
            establishments_id=establishment_internal_id,
            title=marketing_message.title,
            content=marketing_message.content
        )
    
    def create(self, marketing_message: MarketingMessage) -> MarketingMessage:
        marketing_message_orm = self._to_orm(marketing_message)
        self.db_session.add(marketing_message_orm)
        self.db_session.commit()
        self.db_session.refresh(marketing_message_orm)

        return self._to_entity(marketing_message_orm)
    
    def update(self, marketing_message: MarketingMessage) -> MarketingMessage:
        stmt = select(MarketingMessageModel).where(MarketingMessageModel.id == marketing_message.id)
        marketing_message_orm = self.db_session.scalar(stmt)
        
        if not marketing_message_orm:
            raise ValueError(f"MarketingMessage with id {marketing_message.id} not found")
        
        stmt_est = select(EstablishmentModel.id).where(EstablishmentModel.uuid == marketing_message.establishment.id)
        establishment_internal_id = self.db_session.scalar(stmt_est)
        
        if not establishment_internal_id:
            raise ValueError(f"Establishment with uuid {marketing_message.establishment.id} not found")
        
        marketing_message_orm.establishments_id = establishment_internal_id
        marketing_message_orm.title = marketing_message.title
        marketing_message_orm.content = marketing_message.content
        
        self.db_session.commit()
        self.db_session.refresh(marketing_message_orm)
        
        return self._to_entity(marketing_message_orm)

    def get_by_id(self, marketing_message_id: int) -> MarketingMessage | None:
        stmt = select(MarketingMessageModel).where(MarketingMessageModel.id == marketing_message_id)
        result = self.db_session.scalar(stmt)
        
        return self._to_entity(result) if result else None
    
    def list_all(self, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[MarketingMessage]:
        stmt = select(MarketingMessageModel).order_by(MarketingMessageModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(MarketingMessageModel.id > last_id)

        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(msg) for msg in data]

        next_cursor = None
        if has_more and data:
            last_item = data[-1]
            next_cursor = CursorEncoder.encode(last_item.id, field_name="id")

        return PaginatedResponse(
            data=entities,
            cursor=next_cursor,
            has_more=has_more,
            total_count=None
        )

    def list_by_establishment_id(self, establishment_id: UUID, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[MarketingMessage]:
        stmt = select(MarketingMessageModel).where(MarketingMessageModel.establishment.has(uuid=establishment_id)).order_by(MarketingMessageModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(MarketingMessageModel.id > last_id)
        
        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(msg) for msg in data]

        next_cursor = None
        if has_more and data:
            last_item = data[-1]
            next_cursor = CursorEncoder.encode(last_item.id, field_name="id")

        return PaginatedResponse(
            data=entities,
            cursor=next_cursor,
            has_more=has_more,
            total_count=None
        )

    def delete(self, marketing_message_id: int) -> bool:
        stmt = delete(MarketingMessageModel).where(MarketingMessageModel.id == marketing_message_id)
        result = self.db_session.execute(stmt)
        self.db_session.commit()
        
        return result.rowcount > 0
