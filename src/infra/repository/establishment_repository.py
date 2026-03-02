from sqlalchemy import select, delete, func
from sqlalchemy.orm import Session
from domain.entities import Establishment
from domain.interface import EstablishmentInterface
from infra.models import EstablishmentModel, ClientModel
from utils.value_object import PaginatedResponse, CursorEncoder
from .entity_mapper import EntityMapper
from uuid import UUID
from datetime import datetime

class EstablishmentRepository(EstablishmentInterface):

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def _to_entity(self, establishment_model: EstablishmentModel) -> Establishment:
        return EntityMapper.establishment_to_entity(establishment_model)
    
    def _to_orm(self, establishment: Establishment) -> EstablishmentModel:
        return EstablishmentModel(
            uuid=establishment.id,
            clients_id=establishment.client.id,
            stripe_subscription_id=establishment.stripe_subscription_id,
            waba_id=establishment.waba_id,
            whatsapp_business_token=establishment.whatsapp_business_token,
            google_calendar_access_token=establishment.google_calendar_access_token,
            google_calendar_refresh_token=establishment.google_calendar_refresh_token,
            google_calendar_expiry=establishment.google_calendar_expiry,
            google_calendar_id=establishment.google_calendar_id,
            establishment_name=establishment.establishment_name,
            cnpj=establishment.cnpj,
            chatbot_phone_number=establishment.chatbot_phone_number,
            address=establishment.address,
            img_url=establishment.img_url,
            subscription_date=establishment.subscription_date,
            due_date=establishment.due_date,
            trial_active=establishment.trial_active
        )
    
    def create(self, establishment: Establishment) -> Establishment:
        establishment_orm = self._to_orm(establishment)
        self.db_session.add(establishment_orm)
        self.db_session.commit()
        self.db_session.refresh(establishment_orm)

        return self._to_entity(establishment_orm)
    
    def update(self, establishment: Establishment) -> Establishment:
        stmt = select(EstablishmentModel).where(EstablishmentModel.uuid == establishment.id)
        establishment_orm = self.db_session.scalar(stmt)
        
        if not establishment_orm:
            raise ValueError(f"Establishment with id {establishment.id} not found")
        
        establishment_orm.clients_id = establishment.client.id
        establishment_orm.stripe_subscription_id = establishment.stripe_subscription_id
        establishment_orm.waba_id = establishment.waba_id
        establishment_orm.whatsapp_business_token = establishment.whatsapp_business_token
        establishment_orm.google_calendar_access_token = establishment.google_calendar_access_token
        establishment_orm.google_calendar_refresh_token = establishment.google_calendar_refresh_token
        establishment_orm.google_calendar_expiry = establishment.google_calendar_expiry
        establishment_orm.google_calendar_id = establishment.google_calendar_id
        establishment_orm.establishment_name = establishment.establishment_name
        establishment_orm.cnpj = establishment.cnpj
        establishment_orm.chatbot_phone_number = establishment.chatbot_phone_number
        establishment_orm.address = establishment.address
        establishment_orm.img_url = establishment.img_url
        establishment_orm.due_date = establishment.due_date
        establishment_orm.trial_active = establishment.trial_active
        
        self.db_session.commit()
        self.db_session.refresh(establishment_orm)
        
        return self._to_entity(establishment_orm)

    def get_by_id(self, establishment_id: UUID) -> Establishment | None:
        stmt = select(EstablishmentModel).where(EstablishmentModel.uuid == establishment_id)
        result = self.db_session.scalar(stmt)
        
        return self._to_entity(result) if result else None
    
    def get_by_client_id(self, client_id: int) -> Establishment | None:
        stmt = select(EstablishmentModel).where(EstablishmentModel.clients_id == client_id)
        result = self.db_session.scalar(stmt)

        return self._to_entity(result) if result else None
    
    def get_by_cnpj(self, cnpj: str) -> Establishment | None:
        stmt = select(EstablishmentModel).where(EstablishmentModel.cnpj == cnpj)
        result = self.db_session.scalar(stmt)

        return self._to_entity(result) if result else None
    
    def list_all(self, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Establishment]:
        stmt = select(EstablishmentModel).order_by(EstablishmentModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(EstablishmentModel.id > last_id)

        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(establishment) for establishment in data]

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

    def list_all_by_trial_active(self, trial_active: bool, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Establishment]:
        stmt = select(EstablishmentModel).where(EstablishmentModel.trial_active == trial_active).order_by(EstablishmentModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(EstablishmentModel.id > last_id)
        
        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(establishment) for establishment in data]

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

    def list_with_due_date_expired(self, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Establishment]:
        now = datetime.now()
        stmt = select(EstablishmentModel).where(
            EstablishmentModel.due_date < now
        ).order_by(EstablishmentModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(EstablishmentModel.id > last_id)
        
        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(establishment) for establishment in data]

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

    def search_by_establishment_name(self, establishment_name: UUID, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Establishment]:
        stmt = select(EstablishmentModel).where(EstablishmentModel.establishment_name.ilike(f"%{establishment_name}%")).order_by(EstablishmentModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(EstablishmentModel.id > last_id)
        
        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()
        
        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(establishment) for establishment in data]
        
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

    def delete(self, establishment_id: UUID) -> bool:
        stmt = delete(EstablishmentModel).where(EstablishmentModel.uuid == establishment_id)
        result = self.db_session.execute(stmt)
        self.db_session.commit()
        
        return result.rowcount > 0
