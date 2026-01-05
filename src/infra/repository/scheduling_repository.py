from sqlalchemy import select, delete, func
from sqlalchemy.orm import Session
from domain.entities import Scheduling
from domain.interface import SchedulingInterface
from infra.models import SchedulingModel, EstablishmentModel, CustomerModel, ServiceModel
from utils.enum import AppointmentStatus
from utils.value_object import PaginatedResponse, CursorEncoder
from .entity_mapper import EntityMapper
from uuid import UUID
from datetime import datetime

class SchedulingRepository(SchedulingInterface):

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def _to_entity(self, scheduling_model: SchedulingModel) -> Scheduling:
        from domain.entities import Employee, Customer, Service
        
        establishment = EntityMapper.establishment_to_entity(scheduling_model.establishment)
        
        employee_user = EntityMapper.user_to_entity(scheduling_model.employee.user)
        employee = Employee(
            id=scheduling_model.employee.id,
            user=employee_user,
            establishment=establishment,
            percentage_commission=scheduling_model.employee.percentage_commission,
            available_hours=scheduling_model.employee.available_hours
        )
        
        customer = Customer(
            id=scheduling_model.customer.uuid,
            customer_name=scheduling_model.customer.customer_name,
            phone_number=scheduling_model.customer.phone_number,
            establishment=establishment
        )
        
        service = Service(
            id=scheduling_model.service.uuid,
            establishment=establishment,
            service_name=scheduling_model.service.service_name,
            description_service=scheduling_model.service.description_service,
            time_duration=scheduling_model.service.time_duration,
            price=scheduling_model.service.price,
            active=scheduling_model.service.active
        )
        
        return Scheduling(
            id=scheduling_model.uuid,
            establishment=establishment,
            employee=employee,
            customer=customer,
            service=service,
            created_at=scheduling_model.created_at,
            appointment_date=scheduling_model.appointment_date,
            appointment_status=scheduling_model.appointment_status,
            notification_sent=scheduling_model.notification_sent
        )
    
    def _to_orm(self, scheduling: Scheduling) -> SchedulingModel:
        stmt = select(EstablishmentModel.id).where(EstablishmentModel.uuid == scheduling.establishment.id)
        establishment_internal_id = self.db_session.scalar(stmt)
        
        if not establishment_internal_id:
            raise ValueError(f"Establishment with uuid {scheduling.establishment.id} not found")
        
        stmt = select(CustomerModel.id).where(CustomerModel.uuid == scheduling.customer.id)
        customer_internal_id = self.db_session.scalar(stmt)
        
        if not customer_internal_id:
            raise ValueError(f"Customer with uuid {scheduling.customer.id} not found")
        
        stmt = select(ServiceModel.id).where(ServiceModel.uuid == scheduling.service.id)
        service_internal_id = self.db_session.scalar(stmt)
        
        if not service_internal_id:
            raise ValueError(f"Service with uuid {scheduling.service.id} not found")
        
        return SchedulingModel(
            uuid=scheduling.id,
            establishments_id=establishment_internal_id,
            employees_id=scheduling.employee.id,
            customers_id=customer_internal_id,
            services_id=service_internal_id,
            created_at=scheduling.created_at,
            appointment_date=scheduling.appointment_date,
            appointment_status=scheduling.appointment_status,
            notification_sent=scheduling.notification_sent
        )
    
    def create(self, scheduling: Scheduling) -> Scheduling:
        scheduling_orm = self._to_orm(scheduling)
        self.db_session.add(scheduling_orm)
        self.db_session.commit()
        self.db_session.refresh(scheduling_orm)

        return self._to_entity(scheduling_orm)
    
    def update(self, scheduling: Scheduling) -> Scheduling:
        stmt = select(SchedulingModel).where(SchedulingModel.uuid == scheduling.id)
        scheduling_orm = self.db_session.scalar(stmt)
        
        if not scheduling_orm:
            raise ValueError(f"Scheduling with id {scheduling.id} not found")
        
        stmt_est = select(EstablishmentModel.id).where(EstablishmentModel.uuid == scheduling.establishment.id)
        establishment_internal_id = self.db_session.scalar(stmt_est)
        
        if not establishment_internal_id:
            raise ValueError(f"Establishment with uuid {scheduling.establishment.id} not found")
        
        stmt_cust = select(CustomerModel.id).where(CustomerModel.uuid == scheduling.customer.id)
        customer_internal_id = self.db_session.scalar(stmt_cust)
        
        if not customer_internal_id:
            raise ValueError(f"Customer with uuid {scheduling.customer.id} not found")
        
        stmt_serv = select(ServiceModel.id).where(ServiceModel.uuid == scheduling.service.id)
        service_internal_id = self.db_session.scalar(stmt_serv)
        
        if not service_internal_id:
            raise ValueError(f"Service with uuid {scheduling.service.id} not found")
        
        scheduling_orm.establishments_id = establishment_internal_id
        scheduling_orm.employees_id = scheduling.employee.id
        scheduling_orm.customers_id = customer_internal_id
        scheduling_orm.services_id = service_internal_id
        scheduling_orm.appointment_date = scheduling.appointment_date
        scheduling_orm.appointment_status = scheduling.appointment_status
        scheduling_orm.notification_sent = scheduling.notification_sent
        
        self.db_session.commit()
        self.db_session.refresh(scheduling_orm)
        
        return self._to_entity(scheduling_orm)

    def get_by_id(self, scheduling_id: UUID) -> Scheduling | None:
        stmt = select(SchedulingModel).where(SchedulingModel.uuid == scheduling_id)
        result = self.db_session.scalar(stmt)
        
        return self._to_entity(result) if result else None
    
    def list_all(self, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Scheduling]:
        stmt = select(SchedulingModel).order_by(SchedulingModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(SchedulingModel.id > last_id)

        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(scheduling) for scheduling in data]

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

    def list_by_establishment_id(self, establishment_id: UUID, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Scheduling]:
        stmt = select(SchedulingModel).where(SchedulingModel.establishment.has(uuid=establishment_id)).order_by(SchedulingModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(SchedulingModel.id > last_id)
        
        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(scheduling) for scheduling in data]

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

    def list_by_employee_id(self, employee_id: int, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Scheduling]:
        stmt = select(SchedulingModel).where(SchedulingModel.employees_id == employee_id).order_by(SchedulingModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(SchedulingModel.id > last_id)
        
        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(scheduling) for scheduling in data]

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

    def list_by_customer_id(self, customer_id: UUID, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Scheduling]:
        stmt = select(SchedulingModel).where(SchedulingModel.customer.has(uuid=customer_id)).order_by(SchedulingModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(SchedulingModel.id > last_id)
        
        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(scheduling) for scheduling in data]

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

    def list_by_date_range(self, start_date: datetime, end_date: datetime, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Scheduling]:
        stmt = select(SchedulingModel).where(SchedulingModel.appointment_date >= start_date, SchedulingModel.appointment_date <= end_date).order_by(SchedulingModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(SchedulingModel.id > last_id)
        
        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(scheduling) for scheduling in data]

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

    def list_by_status(self, status: AppointmentStatus, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Scheduling]:
        stmt = select(SchedulingModel).where(SchedulingModel.appointment_status == status).order_by(SchedulingModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(SchedulingModel.id > last_id)
        
        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(scheduling) for scheduling in data]

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

    def delete(self, scheduling_id: UUID) -> bool:
        stmt = delete(SchedulingModel).where(SchedulingModel.uuid == scheduling_id)
        result = self.db_session.execute(stmt)
        self.db_session.commit()
        
        return result.rowcount > 0
