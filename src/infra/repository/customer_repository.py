from sqlalchemy import select, delete, func
from sqlalchemy.orm import Session
from domain.entities import Customer
from domain.interface import CustomerInterface
from infra.models import CustomerModel, EstablishmentModel
from utils.value_object import PaginatedResponse, CursorEncoder
from uuid import UUID
from .entity_mapper import EntityMapper

class CustomerRepository(CustomerInterface):

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def _to_entity(self, customer_model: CustomerModel) -> Customer:
        establishment = EntityMapper.establishment_to_entity(customer_model.establishment)
        
        return Customer(
            id=customer_model.uuid,
            customer_name=customer_model.customer_name,
            phone_number=customer_model.phone_number,
            establishment=establishment,
            wa_id=customer_model.wa_id
        )
    
    def _to_orm(self, customer: Customer) -> CustomerModel:
        stmt = select(EstablishmentModel.id).where(EstablishmentModel.uuid == customer.establishment.id)
        establishment_internal_id = self.db_session.scalar(stmt)
        
        if not establishment_internal_id:
            raise ValueError(f"Establishment with uuid {customer.establishment.id} not found")
        
        return CustomerModel(
            uuid=customer.id,
            customer_name=customer.customer_name,
            phone_number=customer.phone_number,
            establishments_id=establishment_internal_id,
            wa_id=customer.wa_id
        )
    
    def create(self, customer: Customer) -> Customer:
        customer_orm = self._to_orm(customer)
        self.db_session.add(customer_orm)
        self.db_session.commit()
        self.db_session.refresh(customer_orm)

        return self._to_entity(customer_orm)
    
    def update(self, customer: Customer) -> Customer:
        stmt = select(CustomerModel).where(CustomerModel.uuid == customer.id)
        customer_orm = self.db_session.scalar(stmt)
        
        if not customer_orm:
            raise ValueError(f"Customer with id {customer.id} not found")
        
        stmt_est = select(EstablishmentModel.id).where(EstablishmentModel.uuid == customer.establishment.id)
        establishment_internal_id = self.db_session.scalar(stmt_est)
        
        if not establishment_internal_id:
            raise ValueError(f"Establishment with uuid {customer.establishment.id} not found")
        
        customer_orm.customer_name = customer.customer_name
        customer_orm.phone_number = customer.phone_number
        customer_orm.establishments_id = establishment_internal_id
        customer_orm.wa_id = customer.wa_id
        
        self.db_session.commit()
        self.db_session.refresh(customer_orm)
        
        return self._to_entity(customer_orm)

    def get_by_id(self, customer_id: UUID) -> Customer | None:
        stmt = select(CustomerModel).where(CustomerModel.uuid == customer_id)
        result = self.db_session.scalar(stmt)
        
        return self._to_entity(result) if result else None
    
    def get_by_phone_number(self, phone_number: str, establishment_id: UUID) -> Customer | None:
        stmt = select(CustomerModel).where(
            CustomerModel.phone_number == phone_number,
            CustomerModel.establishment.has(uuid=establishment_id)
        )
        result = self.db_session.scalar(stmt)

        return self._to_entity(result) if result else None
    
    def list_all(self, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Customer]:
        stmt = select(CustomerModel).order_by(CustomerModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(CustomerModel.id > last_id)

        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(customer) for customer in data]

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

    def list_by_establishment_id(self, establishment_id: UUID, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Customer]:
        stmt = select(CustomerModel).where(CustomerModel.establishment.has(uuid=establishment_id)).order_by(CustomerModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(CustomerModel.id > last_id)
        
        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(customer) for customer in data]

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

    def search_by_name(self, name: str, establishment_id: UUID, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Customer]:
        stmt = select(CustomerModel).where(CustomerModel.customer_name.ilike(f"%{name}%"),CustomerModel.establishment.has(uuid=establishment_id)).order_by(CustomerModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(CustomerModel.id > last_id)
        
        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()
        
        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(customer) for customer in data]
        
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

    def delete(self, customer_id: UUID) -> bool:
        stmt = delete(CustomerModel).where(CustomerModel.uuid == customer_id)
        result = self.db_session.execute(stmt)
        self.db_session.commit()
        
        return result.rowcount > 0
