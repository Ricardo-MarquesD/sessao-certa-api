from sqlalchemy import select, delete, func
from sqlalchemy.orm import Session
from domain.entities import Employee
from domain.interface import EmployeeInterface
from infra.models import EmployeeModel, UserModel, EstablishmentModel
from utils.value_object import PaginatedResponse, CursorEncoder
from .entity_mapper import EntityMapper
from uuid import UUID

class EmployeeRepository(EmployeeInterface):

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def _to_entity(self, employee_model: EmployeeModel) -> Employee:
        user = EntityMapper.user_to_entity(employee_model.user)
        establishment = EntityMapper.establishment_to_entity(employee_model.establishment)
        
        return Employee(
            id=employee_model.id,
            user=user,
            establishment=establishment,
            percentage_commission=employee_model.percentage_commission,
            available_hours=employee_model.available_hours
        )
    
    def _to_orm(self, employee: Employee) -> EmployeeModel:
        stmt = select(UserModel.id).where(UserModel.uuid == employee.user.id)
        user_internal_id = self.db_session.scalar(stmt)
        
        if not user_internal_id:
            raise ValueError(f"User with uuid {employee.user.id} not found")
        
        stmt = select(EstablishmentModel.id).where(EstablishmentModel.uuid == employee.establishment.id)
        establishment_internal_id = self.db_session.scalar(stmt)
        
        if not establishment_internal_id:
            raise ValueError(f"Establishment with uuid {employee.establishment.id} not found")
        
        return EmployeeModel(
            id=employee.id,
            users_id=user_internal_id,
            establishments_id=establishment_internal_id,
            percentage_commission=employee.percentage_commission,
            available_hours=employee.available_hours
        )
    
    def create(self, employee: Employee) -> Employee:
        employee_orm = self._to_orm(employee)
        self.db_session.add(employee_orm)
        self.db_session.commit()
        self.db_session.refresh(employee_orm)

        return self._to_entity(employee_orm)
    
    def update(self, employee: Employee) -> Employee:
        stmt = select(EmployeeModel).where(EmployeeModel.id == employee.id)
        employee_orm = self.db_session.scalar(stmt)
        
        if not employee_orm:
            raise ValueError(f"Employee with id {employee.id} not found")
        
        stmt_user = select(UserModel.id).where(UserModel.uuid == employee.user.id)
        user_internal_id = self.db_session.scalar(stmt_user)
        
        if not user_internal_id:
            raise ValueError(f"User with uuid {employee.user.id} not found")
        
        stmt_est = select(EstablishmentModel.id).where(EstablishmentModel.uuid == employee.establishment.id)
        establishment_internal_id = self.db_session.scalar(stmt_est)
        
        if not establishment_internal_id:
            raise ValueError(f"Establishment with uuid {employee.establishment.id} not found")
        
        employee_orm.users_id = user_internal_id
        employee_orm.establishments_id = establishment_internal_id
        employee_orm.percentage_commission = employee.percentage_commission
        employee_orm.available_hours = employee.available_hours
        
        self.db_session.commit()
        self.db_session.refresh(employee_orm)
        
        return self._to_entity(employee_orm)

    def get_by_id(self, employee_id: int) -> Employee | None:
        stmt = select(EmployeeModel).where(EmployeeModel.id == employee_id)
        result = self.db_session.scalar(stmt)
        
        return self._to_entity(result) if result else None
    
    def get_by_user_id(self, user_id: UUID) -> Employee | None:
        stmt = select(EmployeeModel).where(EmployeeModel.user.has(uuid=user_id))
        result = self.db_session.scalar(stmt)

        return self._to_entity(result) if result else None
    
    def list_all(self, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Employee]:
        stmt = select(EmployeeModel).order_by(EmployeeModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(EmployeeModel.id > last_id)

        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(employee) for employee in data]

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

    def list_by_establishment_id(self, establishment_id: UUID, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Employee]:
        stmt = select(EmployeeModel).where(EmployeeModel.establishment.has(uuid=establishment_id)).order_by(EmployeeModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(EmployeeModel.id > last_id)
        
        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(employee) for employee in data]

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

    def count_by_establishment_id(self, establishment_id: UUID) -> int:
        stmt = select(func.count()).select_from(EmployeeModel).where(EmployeeModel.establishment.has(uuid=establishment_id))
        count = self.db_session.scalar(stmt)
        return count if count else 0

    def delete(self, employee_id: UUID) -> bool:
        stmt = delete(EmployeeModel).where(EmployeeModel.id == employee_id)
        result = self.db_session.execute(stmt)
        self.db_session.commit()
        
        return result.rowcount > 0
