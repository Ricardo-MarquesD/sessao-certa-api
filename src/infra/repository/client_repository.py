from sqlalchemy import select, delete, func
from sqlalchemy.orm import Session
from domain.entities import Client
from domain.interface import ClientInterface
from infra.models import ClientModel, UserModel
from utils.value_object import PaginatedResponse, CursorEncoder
from .entity_mapper import EntityMapper
from uuid import UUID

class ClientRepository(ClientInterface):

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def _to_entity(self, client_model: ClientModel) -> Client:
        return EntityMapper.client_to_entity(client_model)
    
    def _to_orm(self, client: Client) -> ClientModel:
        stmt = select(UserModel.id).where(UserModel.uuid == client.user.id)
        user_internal_id = self.db_session.scalar(stmt)
        
        if not user_internal_id:
            raise ValueError(f"User with uuid {client.user.id} not found")
        
        return ClientModel(
            id=client.id,
            users_id=user_internal_id,
            plans_id=client.plan.id,
            stripe_customer_id=client.stripe_customer_id
        )
    
    def create(self, client: Client) -> Client:
        client_orm = self._to_orm(client)
        self.db_session.add(client_orm)
        self.db_session.commit()
        self.db_session.refresh(client_orm)

        return self._to_entity(client_orm)
    
    def update(self, client: Client) -> Client:
        stmt = select(ClientModel).where(ClientModel.id == client.id)
        client_orm = self.db_session.scalar(stmt)
        
        if not client_orm:
            raise ValueError(f"Client with id {client.id} not found")
        
        stmt_user = select(UserModel.id).where(UserModel.uuid == client.user.id)
        user_internal_id = self.db_session.scalar(stmt_user)
        
        if not user_internal_id:
            raise ValueError(f"User with uuid {client.user.id} not found")
        
        client_orm.users_id = user_internal_id
        client_orm.plans_id = client.plan.id
        client_orm.stripe_customer_id = client.stripe_customer_id
        
        self.db_session.commit()
        self.db_session.refresh(client_orm)
        
        return self._to_entity(client_orm)

    def get_by_id(self, client_id: int) -> Client | None:
        stmt = select(ClientModel).where(ClientModel.id == client_id)
        result = self.db_session.scalar(stmt)
        
        return self._to_entity(result) if result else None
    
    def get_by_user_id(self, user_id: UUID) -> Client | None:
        stmt = select(ClientModel).where(ClientModel.user.has(uuid=user_id))
        result = self.db_session.scalar(stmt)

        return self._to_entity(result) if result else None
    
    def list_all(self, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Client]:
        stmt = select(ClientModel).order_by(ClientModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(ClientModel.id > last_id)

        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(client) for client in data]

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

    def list_by_plan_id(self, plan_id: int, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Client]:
        stmt = select(ClientModel).where(ClientModel.plans_id == plan_id).order_by(ClientModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(ClientModel.id > last_id)
        
        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(client) for client in data]

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

    def delete(self, client_id: int) -> bool:
        stmt = delete(ClientModel).where(ClientModel.id == client_id)
        result = self.db_session.execute(stmt)
        self.db_session.commit()
        
        return result.rowcount > 0