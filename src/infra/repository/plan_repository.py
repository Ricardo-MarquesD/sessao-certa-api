from utils.value_object import PaginatedResponse, CursorEncoder
from sqlalchemy import select, delete, func
from sqlalchemy.orm import Session
from domain.entities import Plan
from domain.interface import PlanInterface
from infra.models import PlanModel
from utils.enum import TypePlan


class PlanRepository(PlanInterface):

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def _to_entity(self, plan_model: PlanModel) -> Plan:
        return Plan(
            id = plan_model.id,
            type_plan = plan_model.type_plan,
            basic_price = plan_model.basic_price,
            max_employee = plan_model.max_employee,
            allow_stock = plan_model.allow_stock,
            allow_advanced_analysis = plan_model.allow_advanced_analysis
        )
    
    def _to_orm(self, plan: Plan) -> PlanModel:
        return PlanModel(
            id = plan.id,
            type_plan = plan.type_plan,
            basic_price = plan.basic_price,
            max_employee = plan.max_employee,
            allow_stock = plan.allow_stock,
            allow_advanced_analysis = plan.allow_advanced_analysis
        )
    
    def create(self, plan: Plan) -> Plan:
        plan_orm = self._to_orm(plan)
        self.db_session.add(plan_orm)
        self.db_session.commit()
        self.db_session.refresh(plan_orm)

        return self._to_entity(plan_orm)
    
    def update(self, plan: Plan) -> Plan:
        stmt = select(PlanModel).where(PlanModel.id == plan.id)
        plan_orm = self.db_session.scalar(stmt)

        if not plan_orm:
            raise ValueError(f"Plan with id {plan.id} not found")
        
        plan_orm.type_plan = plan.type_plan
        plan_orm.basic_price = plan.basic_price
        plan_orm.max_employee = plan.max_employee
        plan_orm.allow_stock = plan.allow_stock
        plan_orm.allow_advanced_analysis = plan.allow_advanced_analysis

        self.db_session.commit()
        self.db_session.refresh(plan_orm)

        return self._to_entity(plan_orm)

    def get_by_id(self, plan_id: int) -> Plan | None:
        stmt = select(PlanModel).where(PlanModel.id == plan_id)
        result = self.db_session.scalar(stmt)
        
        return self._to_entity(result) if result else None
    
    def get_by_max_employee(self, max_employee: int) -> Plan | None:
        stmt = select(PlanModel).where(PlanModel.max_employee == max_employee)
        result = self.db_session.scalar(stmt)

        return self._to_entity(result) if result else None
    
    def list_all(self, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Plan]:
        stmt = select(PlanModel).order_by(PlanModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(PlanModel.id > last_id)

        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(plan) for plan in data]

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

    def list_by_type(self, type_plan: TypePlan, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Plan]:
        stmt = select(PlanModel).where(PlanModel.type_plan == type_plan).order_by(PlanModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(PlanModel.id > last_id)
        
        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(plan) for plan in data]

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

    def list_by_allow_stock(self, allow_stock: bool, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Plan]:
        stmt = select(PlanModel).where(PlanModel.allow_stock == allow_stock).order_by(PlanModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(PlanModel.id > last_id)
        
        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(plan) for plan in data]

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

    def list_by_allow_advanced_analysis(self, allow_advanced_analysis: bool, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Plan]:
        stmt = select(PlanModel).where(PlanModel.allow_advanced_analysis == allow_advanced_analysis).order_by(PlanModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(PlanModel.id > last_id)
        
        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(plan) for plan in data]

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

    def list_by_max_employee(self, max_employee: int, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Plan]:
        stmt = select(PlanModel).where(PlanModel.max_employee >= max_employee).order_by(PlanModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(PlanModel.id > last_id)
        
        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(plan) for plan in data]

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

    def delete(self, plan_id: int) -> bool:
        stmt = delete(PlanModel).where(PlanModel.id == plan_id)
        result = self.db_session.execute(stmt)
        self.db_session.commit()
        
        return result.rowcount > 0
