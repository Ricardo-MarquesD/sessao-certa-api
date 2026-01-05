from sqlalchemy import select, delete, func
from sqlalchemy.orm import Session
from domain.entities import StockProduct, StockMovement
from domain.interface import StockProductInterface, StockMovementInterface
from infra.models import StockProductModel, StockMovementModel, EstablishmentModel
from utils.enum import MovementType
from utils.value_object import PaginatedResponse, CursorEncoder
from .entity_mapper import EntityMapper
from datetime import datetime

class StockProductRepository(StockProductInterface):

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def _to_entity(self, stock_product_model: StockProductModel) -> StockProduct:
        establishment = EntityMapper.establishment_to_entity(stock_product_model.establishment)
        
        return StockProduct(
            id=stock_product_model.id,
            establishment=establishment,
            product_name=stock_product_model.product_name,
            quantity=stock_product_model.quantity,
            price=stock_product_model.price
        )
    
    def _to_orm(self, stock_product: StockProduct) -> StockProductModel:
        stmt = select(EstablishmentModel.id).where(EstablishmentModel.uuid == stock_product.establishment.id)
        establishment_internal_id = self.db_session.scalar(stmt)
        
        if not establishment_internal_id:
            raise ValueError(f"Establishment with uuid {stock_product.establishment.id} not found")
        
        return StockProductModel(
            id=stock_product.id,
            establishments_id=establishment_internal_id,
            product_name=stock_product.product_name,
            quantity=stock_product.quantity,
            price=stock_product.price
        )
    
    def create(self, stock_product: StockProduct) -> StockProduct:
        stock_product_orm = self._to_orm(stock_product)
        self.db_session.add(stock_product_orm)
        self.db_session.commit()
        self.db_session.refresh(stock_product_orm)

        return self._to_entity(stock_product_orm)
    
    def update(self, stock_product: StockProduct) -> StockProduct:
        stmt = select(StockProductModel).where(StockProductModel.id == stock_product.id)
        stock_product_orm = self.db_session.scalar(stmt)
        
        if not stock_product_orm:
            raise ValueError(f"StockProduct with id {stock_product.id} not found")
        
        stmt_est = select(EstablishmentModel.id).where(EstablishmentModel.uuid == stock_product.establishment.id)
        establishment_internal_id = self.db_session.scalar(stmt_est)
        
        if not establishment_internal_id:
            raise ValueError(f"Establishment with uuid {stock_product.establishment.id} not found")
        
        stock_product_orm.establishments_id = establishment_internal_id
        stock_product_orm.product_name = stock_product.product_name
        stock_product_orm.quantity = stock_product.quantity
        stock_product_orm.price = stock_product.price
        
        self.db_session.commit()
        self.db_session.refresh(stock_product_orm)
        
        return self._to_entity(stock_product_orm)

    def get_by_id(self, stock_product_id: int) -> StockProduct | None:
        stmt = select(StockProductModel).where(StockProductModel.id == stock_product_id)
        result = self.db_session.scalar(stmt)
        
        return self._to_entity(result) if result else None
    
    def get_by_name_and_establishment(self, product_name: str, establishment_id: str) -> StockProduct | None:
        stmt = select(StockProductModel).where(StockProductModel.product_name == product_name, StockProductModel.establishment.has(uuid=establishment_id))
        result = self.db_session.scalar(stmt)

        return self._to_entity(result) if result else None
    
    def list_all(self, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[StockProduct]:
        stmt = select(StockProductModel).order_by(StockProductModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(StockProductModel.id > last_id)

        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(product) for product in data]

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

    def list_by_establishment_id(self, establishment_id: str, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[StockProduct]:
        stmt = select(StockProductModel).where(StockProductModel.establishment.has(uuid=establishment_id)).order_by(StockProductModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(StockProductModel.id > last_id)
        
        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(product) for product in data]

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

    def list_available_by_establishment_id(self, establishment_id: str, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[StockProduct]:
        stmt = select(StockProductModel).where(StockProductModel.quantity > 0, StockProductModel.establishment.has(uuid=establishment_id)).order_by(StockProductModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(StockProductModel.id > last_id)
        
        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(product) for product in data]

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

    def delete(self, stock_product_id: int) -> bool:
        stmt = delete(StockProductModel).where(StockProductModel.id == stock_product_id)
        result = self.db_session.execute(stmt)
        self.db_session.commit()
        
        return result.rowcount > 0


class StockMovementRepository(StockMovementInterface):

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def _to_entity(self, stock_movement_model: StockMovementModel) -> StockMovement:
        establishment = EntityMapper.establishment_to_entity(stock_movement_model.stock_product.establishment)
        
        stock_product = StockProduct(
            id=stock_movement_model.stock_product.id,
            establishment=establishment,
            product_name=stock_movement_model.stock_product.product_name,
            quantity=stock_movement_model.stock_product.quantity,
            price=stock_movement_model.stock_product.price
        )
        
        return StockMovement(
            id=stock_movement_model.id,
            stock_product=stock_product,
            movement_type=stock_movement_model.movement_type,
            quantity=stock_movement_model.quantity,
            date=stock_movement_model.date
        )
    
    def _to_orm(self, stock_movement: StockMovement) -> StockMovementModel:
        return StockMovementModel(
            id=stock_movement.id,
            stock_products_id=stock_movement.stock_product.id,
            movement_type=stock_movement.movement_type,
            quantity=stock_movement.quantity,
            date=stock_movement.date
        )
    
    def create(self, stock_movement: StockMovement) -> StockMovement:
        stock_movement_orm = self._to_orm(stock_movement)
        self.db_session.add(stock_movement_orm)
        self.db_session.commit()
        self.db_session.refresh(stock_movement_orm)

        return self._to_entity(stock_movement_orm)
    
    def update(self, stock_movement: StockMovement) -> StockMovement:
        stmt = select(StockMovementModel).where(StockMovementModel.id == stock_movement.id)
        stock_movement_orm = self.db_session.scalar(stmt)
        
        if not stock_movement_orm:
            raise ValueError(f"StockMovement with id {stock_movement.id} not found")
        
        stock_movement_orm.stock_products_id = stock_movement.stock_product.id
        stock_movement_orm.movement_type = stock_movement.movement_type
        stock_movement_orm.quantity = stock_movement.quantity
        stock_movement_orm.date = stock_movement.date
        
        self.db_session.commit()
        self.db_session.refresh(stock_movement_orm)
        
        return self._to_entity(stock_movement_orm)

    def get_by_id(self, stock_movement_id: int) -> StockMovement | None:
        stmt = select(StockMovementModel).where(StockMovementModel.id == stock_movement_id)
        result = self.db_session.scalar(stmt)
        
        return self._to_entity(result) if result else None
    
    def list_all(self, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[StockMovement]:
        stmt = select(StockMovementModel).order_by(StockMovementModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(StockMovementModel.id > last_id)

        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(movement) for movement in data]

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

    def list_by_stock_product_id(self, stock_product_id: int, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[StockMovement]:
        stmt = select(StockMovementModel).where(StockMovementModel.stock_products_id == stock_product_id).order_by(StockMovementModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(StockMovementModel.id > last_id)
        
        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(movement) for movement in data]

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

    def list_by_movement_type(self, movement_type: MovementType, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[StockMovement]:
        stmt = select(StockMovementModel).where(StockMovementModel.movement_type == movement_type).order_by(StockMovementModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(StockMovementModel.id > last_id)
        
        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(movement) for movement in data]

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

    def list_by_date_range(self, start_date: datetime, end_date: datetime, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[StockMovement]:
        stmt = select(StockMovementModel).where(StockMovementModel.date >= start_date, StockMovementModel.date <= end_date).order_by(StockMovementModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(StockMovementModel.id > last_id)
        
        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(movement) for movement in data]

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

    def delete(self, stock_movement_id: int) -> bool:
        stmt = delete(StockMovementModel).where(StockMovementModel.id == stock_movement_id)
        self.db_session.execute(stmt)
        self.db_session.commit()
        
        stmt_verify = select(StockMovementModel).where(StockMovementModel.id == stock_movement_id)
        result = self.db_session.scalar(stmt_verify)

        return False if result is not None else True
