from sqlalchemy import select
from sqlalchemy.orm import Session
from domain.entities import User
from domain.interface import UserInterface
from infra.models import UserModel
from utils.enum import UserRole

class UserRepository(UserInterface):

    def __init___(self, db_session: Session):
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
        user_orm = self._to_orm(user)
        self.db_session.add(user_orm)
        self.db_session.commit()

        return self._to_entity(user_orm)

    def get_by_id(self, user_id: str) -> User | None:
        stmt = select(UserModel).where(UserModel.uuid == user_id)

        return self._to_entity(self.db_session.scalars(stmt).first())
    
    