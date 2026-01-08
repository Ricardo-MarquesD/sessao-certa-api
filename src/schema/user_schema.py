from pydantic import BaseModel, EmailStr
from domain.entities import User
from utils.enum import UserRole

class CreateUserRequest(BaseModel):
    user_name: str
    email: EmailStr
    password: str
    phone_number: str
    role: UserRole
    img_url: str | None

class UserResponse(BaseModel):
    id: str
    user_name: str
    email: str
    phone_number: str
    role:  str
    active_status: bool
    img_url: str
    created_at: str | None

    @classmethod
    def from_entity(cls, user: User) -> UserResponse:
        return cls(
            id=user.id,
            user_name=user.user_name,
            email=user.email,
            phone_number=user. phone_number, 
            role=user.role. value,
            active_status=user.active_status or False,
            img_url=user.img_url,
            created_at=user.created_at. isoformat() if user.created_at else None
        )