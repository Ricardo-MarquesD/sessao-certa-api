from sqlalchemy import select, delete, func
from sqlalchemy.orm import Session
from domain.entities import Service
from domain.interface import ServiceInterface
from infra.models import ServiceModel, EstablishmentModel
from utils.value_object import PaginatedResponse, CursorEncoder
from uuid import UUID
from .entity_mapper import EntityMapper

class ServiceRepository(ServiceInterface):

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def _to_entity(self, service_model: ServiceModel) -> Service:
        establishment = EntityMapper.establishment_to_entity(service_model.establishment)
        
        return Service(
            id=service_model.uuid,
            establishment=establishment,
            service_name=service_model.service_name,
            description_service=service_model.description_service,
            time_duration=service_model.time_duration,
            price=service_model.price,
            active=service_model.active
        )
    
    def _to_orm(self, service: Service) -> ServiceModel:
        stmt = select(EstablishmentModel.id).where(EstablishmentModel.uuid == service.establishment.id)
        establishment_internal_id = self.db_session.scalar(stmt)
        
        if not establishment_internal_id:
            raise ValueError(f"Establishment with uuid {service.establishment.id} not found")
        
        return ServiceModel(
            uuid=service.id,
            establishments_id=establishment_internal_id,
            service_name=service.service_name,
            description_service=service.description_service,
            time_duration=service.time_duration,
            price=service.price,
            active=service.active
        )
    
    def create(self, service: Service) -> Service:
        service_orm = self._to_orm(service)
        self.db_session.add(service_orm)
        self.db_session.commit()
        self.db_session.refresh(service_orm)

        return self._to_entity(service_orm)
    
    def update(self, service: Service) -> Service:
        stmt = select(ServiceModel).where(ServiceModel.uuid == service.id)
        service_orm = self.db_session.scalar(stmt)
        
        if not service_orm:
            raise ValueError(f"Service with id {service.id} not found")
        
        stmt_est = select(EstablishmentModel.id).where(EstablishmentModel.uuid == service.establishment.id)
        establishment_internal_id = self.db_session.scalar(stmt_est)
        
        if not establishment_internal_id:
            raise ValueError(f"Establishment with uuid {service.establishment.id} not found")
        
        service_orm.establishments_id = establishment_internal_id
        service_orm.service_name = service.service_name
        service_orm.description_service = service.description_service
        service_orm.time_duration = service.time_duration
        service_orm.price = service.price
        service_orm.active = service.active
        
        self.db_session.commit()
        self.db_session.refresh(service_orm)
        
        return self._to_entity(service_orm)

    def get_by_id(self, service_id: UUID) -> Service | None:
        stmt = select(ServiceModel).where(ServiceModel.uuid == service_id)
        result = self.db_session.scalar(stmt)
        
        return self._to_entity(result) if result else None
    
    def list_all(self, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Service]:
        stmt = select(ServiceModel).order_by(ServiceModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(ServiceModel.id > last_id)

        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(service) for service in data]

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

    def list_by_establishment_id(self, establishment_id: UUID, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Service]:
        stmt = select(ServiceModel).where(ServiceModel.establishment.has(uuid=establishment_id)).order_by(ServiceModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(ServiceModel.id > last_id)
        
        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(service) for service in data]

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

    def list_active_by_establishment_id(self, active: bool, establishment_id: UUID, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Service]:
        stmt = select(ServiceModel).where(ServiceModel.active == active, ServiceModel.establishment.has(uuid=establishment_id)).order_by(ServiceModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(ServiceModel.id > last_id)
        
        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(service) for service in data]

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

    def delete(self, service_id: UUID) -> bool:
        stmt = delete(ServiceModel).where(ServiceModel.uuid == service_id)
        result = self.db_session.execute(stmt)
        self.db_session.commit()
        
        return result.rowcount > 0
