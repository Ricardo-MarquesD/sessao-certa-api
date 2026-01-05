from sqlalchemy import select, delete, func
from sqlalchemy.orm import Session
from domain.entities import Payment
from domain.interface import PaymentInterface
from infra.models import PaymentModel, EstablishmentModel
from utils.enum import PaymentStatus, PaymentType
from utils.value_object import PaginatedResponse, CursorEncoder
from uuid import UUID
from datetime import datetime
from .entity_mapper import EntityMapper

class PaymentRepository(PaymentInterface):

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def _to_entity(self, payment_model: PaymentModel) -> Payment:
        establishment = EntityMapper.establishment_to_entity(payment_model.establishment)
        
        return Payment(
            id=payment_model.uuid,
            establishment=establishment,
            valor=payment_model.valor,
            payment_day=payment_model.payment_day,
            payment_status=payment_model.payment_status,
            payment_type=payment_model.payment_type,
            employee_quantity=payment_model.employee_quantity,
            gateway_transaction_id=payment_model.gateway_transaction_id
        )
    
    def _to_orm(self, payment: Payment) -> PaymentModel:
        stmt = select(EstablishmentModel.id).where(EstablishmentModel.uuid == payment.establishment.id)
        establishment_internal_id = self.db_session.scalar(stmt)
        
        if not establishment_internal_id:
            raise ValueError(f"Establishment with uuid {payment.establishment.id} not found")
        
        return PaymentModel(
            uuid=payment.id,
            establishments_id=establishment_internal_id,
            valor=payment.valor,
            payment_day=payment.payment_day,
            payment_status=payment.payment_status,
            payment_type=payment.payment_type,
            employee_quantity=payment.employee_quantity,
            gateway_transaction_id=payment.gateway_transaction_id
        )
    
    def create(self, payment: Payment) -> Payment:
        payment_orm = self._to_orm(payment)
        self.db_session.add(payment_orm)
        self.db_session.commit()
        self.db_session.refresh(payment_orm)

        return self._to_entity(payment_orm)
    
    def update(self, payment: Payment) -> Payment:
        stmt = select(PaymentModel).where(PaymentModel.uuid == payment.id)
        payment_orm = self.db_session.scalar(stmt)
        
        if not payment_orm:
            raise ValueError(f"Payment with id {payment.id} not found")
        
        stmt_est = select(EstablishmentModel.id).where(EstablishmentModel.uuid == payment.establishment.id)
        establishment_internal_id = self.db_session.scalar(stmt_est)
        
        if not establishment_internal_id:
            raise ValueError(f"Establishment with uuid {payment.establishment.id} not found")
        
        payment_orm.establishments_id = establishment_internal_id
        payment_orm.valor = payment.valor
        payment_orm.payment_day = payment.payment_day
        payment_orm.payment_status = payment.payment_status
        payment_orm.payment_type = payment.payment_type
        payment_orm.employee_quantity = payment.employee_quantity
        payment_orm.gateway_transaction_id = payment.gateway_transaction_id
        
        self.db_session.commit()
        self.db_session.refresh(payment_orm)
        
        return self._to_entity(payment_orm)

    def get_by_id(self, payment_id: UUID) -> Payment | None:
        stmt = select(PaymentModel).where(PaymentModel.uuid == payment_id)
        result = self.db_session.scalar(stmt)
        
        return self._to_entity(result) if result else None
    
    def list_all(self, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Payment]:
        stmt = select(PaymentModel).order_by(PaymentModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(PaymentModel.id > last_id)

        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(payment) for payment in data]

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

    def list_by_establishment_id(self, establishment_id: UUID, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Payment]:
        stmt = select(PaymentModel).where(PaymentModel.establishment.has(uuid=establishment_id)).order_by(PaymentModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(PaymentModel.id > last_id)
        
        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(payment) for payment in data]

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

    def list_by_status(self, status: PaymentStatus, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Payment]:
        stmt = select(PaymentModel).where(PaymentModel.payment_status == status).order_by(PaymentModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(PaymentModel.id > last_id)
        
        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(payment) for payment in data]

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

    def list_by_type(self, payment_type: PaymentType, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Payment]:
        stmt = select(PaymentModel).where(PaymentModel.payment_type == payment_type).order_by(PaymentModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(PaymentModel.id > last_id)
        
        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(payment) for payment in data]

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

    def list_by_due_date_range(self, start_date: datetime, end_date: datetime, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Payment]:
        stmt = select(PaymentModel).where(PaymentModel.payment_day >= start_date, PaymentModel.payment_day <= end_date).order_by(PaymentModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(PaymentModel.id > last_id)
        
        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(payment) for payment in data]

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

    def delete(self, payment_id: UUID) -> bool:
        stmt = delete(PaymentModel).where(PaymentModel.uuid == payment_id)
        result = self.db_session.execute(stmt)
        self.db_session.commit()
        
        return result.rowcount > 0
