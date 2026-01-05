from utils.value_object import PaginatedResponse, CursorEncoder
from sqlalchemy import select, delete, func
from sqlalchemy.orm import Session
from domain.entities import User
from domain.interface import UserInterface
from infra.models import UserModel
from utils.enum import UserRole
from uuid import UUID

class UserRepository(UserInterface):

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def _to_entity(self, user_model: UserModel) -> User:
        return User(
            id=user_model.uuid,
            user_name=user_model.user_name,
            email=user_model.email,
            phone_number=user_model.phone_number,
            password_hash=user_model.password_hash,
            role=user_model.role,
            active_status=user_model.active_status,
            img_url=user_model.img_url,
            created_at=user_model.create_in,
            updated_at=user_model.update_in
        )
    
    def _to_orm(self, user: User) -> UserModel:
        return UserModel(
            uuid=user.id,
            user_name=user.user_name,
            email=user.email,
            phone_number=user.phone_number,
            password_hash=user.password_hash,
            role=user.role,
            active_status=user.active_status,
            img_url=user.img_url
        )
    
    def create(self, user: User) -> User:
        user_orm = self._to_orm(user)
        self.db_session.add(user_orm)
        self.db_session.commit()

        return self._to_entity(user_orm)
    
    def update(self, user: User) -> User:
        stmt = select(UserModel).where(UserModel.uuid == user.id)
        user_orm = self.db_session.scalar(stmt)
        
        if not user_orm:
            raise ValueError(f"User with id {user.id} not found")
        
        user_orm.user_name = user.user_name
        user_orm.email = user.email
        user_orm.phone_number = user.phone_number
        user_orm.password_hash = user.password_hash
        user_orm.role = user.role
        user_orm.active_status = user.active_status
        user_orm.img_url = user.img_url
        
        self.db_session.commit()
        self.db_session.refresh(user_orm)
        
        return self._to_entity(user_orm)

    def get_by_id(self, user_id: UUID) -> User | None:
        stmt = select(UserModel).where(UserModel.uuid == user_id)
        result = self.db_session.scalar(stmt)
        
        return self._to_entity(result) if result else None
    
    def get_by_email(self, email:str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email)
        result = self.db_session.scalar(stmt)

        return self._to_entity(result) if result else None
    
    def get_by_phone_number(self, phone_number:str) -> User | None:
        stmt = select(UserModel).where(UserModel.phone_number == phone_number)
        result = self.db_session.scalar(stmt)

        return self._to_entity(result) if result else None
    
    def list_all(self, cursor: str | None = None, limit: int = 15, total_status: bool = None) -> PaginatedResponse[User]:
        stmt = select(UserModel).order_by(UserModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(UserModel.id > last_id)

        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(user) for user in data]

        next_cursor = None
        if has_more:
            last_item = data[-1]
            next_cursor = CursorEncoder.encode(last_item.id, field_name="id")

        total_count = None
        if total_status:
            stmt_count = select(func.count()).select_from(UserModel)
            total_count = self.db_session.scalar(stmt_count)

        return PaginatedResponse(
            data= entities,
            cursor = next_cursor,
            has_more = has_more,
            total_count = total_count
        )

    def list_all_by_active(self, active_status: bool, cursor: str | None = None, limit: int = 15, total_status: bool = None) -> PaginatedResponse[User]:
        stmt = select(UserModel).order_by(UserModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(UserModel.id > last_id, UserModel.active_status == active_status)
        else:
            stmt = stmt.where(UserModel.active_status == active_status)
        
        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(user) for user in data]

        next_cursor = None
        if has_more:
            last_item = data[-1]
            next_cursor = CursorEncoder.encode(last_item.id, field_name="id")    

        total_count = None
        if total_status:
            stmt_count = select(func.count()).select_from(UserModel).where(UserModel.active_status == active_status)
            total_count = self.db_session.scalar(stmt_count)    

        return PaginatedResponse(
            data= entities,
            cursor = next_cursor,
            has_more = has_more,
            total_count = total_count
        )

    def list_by_role(self, role: UserRole, cursor: str | None = None, limit: int = 15, total_status: bool = None) -> PaginatedResponse[User]:
        stmt = select(UserModel).order_by(UserModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(UserModel.id > last_id, UserModel.role == role)
        else:
            stmt = stmt.where(UserModel.role == role)
        
        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()

        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(user) for user in data]

        next_cursor = None
        if has_more:
            last_item = data[-1]
            next_cursor = CursorEncoder.encode(last_item.id, field_name="id")    

        total_count = None
        if total_status:
            stmt_count = select(func.count()).select_from(UserModel).where(UserModel.role == role)
            total_count = self.db_session.scalar(stmt_count)

        return PaginatedResponse(
            data= entities,
            cursor = next_cursor,
            has_more = has_more,
            total_count = total_count
        )

    def search_by_user_name(self, user_name: str, cursor: str | None = None, limit: int = 15, total_status: bool = None) -> PaginatedResponse[User]:
        stmt = select(UserModel).where(UserModel.user_name.ilike(f"%{user_name}%")).order_by(UserModel.id)
        
        if cursor:
            cursor_data = CursorEncoder.decode(cursor)
            last_id = int(cursor_data.get("id"))
            stmt = stmt.where(UserModel.id > last_id)
        
        stmt = stmt.limit(limit + 1)
        results = self.db_session.scalars(stmt).all()
        
        has_more = len(results) > limit
        data = results[:limit]
        entities = [self._to_entity(user) for user in data]
        
        next_cursor = None
        if has_more and data:
            last_item = data[-1]
            next_cursor = CursorEncoder.encode(last_item.id, field_name="id")
        
        total_count = None
        if total_status:
            stmt_count = select(func.count()).select_from(UserModel).where(UserModel.user_name.ilike(f"%{user_name}%"))
            total_count = self.db_session.scalar(stmt_count)
        
        return PaginatedResponse(
            data=entities,
            cursor=next_cursor,
            has_more=has_more,
            total_count=total_count
        )

    def delete(self, user_id: UUID) -> bool:
        stmt = delete(UserModel).where(UserModel.uuid == user_id, UserModel.active_status == False)
        result = self.db_session.execute(stmt)
        self.db_session.commit()
        
        return result.rowcount > 0