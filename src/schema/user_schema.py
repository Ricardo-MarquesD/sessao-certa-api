from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic_extra_types.phone_numbers import PhoneNumber
from domain.entities import User, Client
from schema import PlanResponse
from utils.enum import UserRole
from datetime import datetime

class _UserBase(BaseModel):
    user_name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    phone_number: PhoneNumber = Field(default_region='BR')
    role: UserRole

    @field_validator('role')
    @classmethod
    def role_verify(cls, v: UserRole):
        if v == UserRole.ADMIN:
            raise ValueError("Request cannot put Admin status")


class CreateUserRequest(_UserBase):
    password: str

class UpdateUserRequest(BaseModel):
    user_name: str | None = Field(default=None, min_length=1, max_length=150)
    email: EmailStr | None = None
    phone_number: PhoneNumber | None = Field(default=None, default_region='BR')
    active_status: bool | None = None

class UserResponse(_UserBase):
    id: str
    active_status: bool
    img_url: str | None
    created_at: datetime | None
    updated_at: datetime | None

    @classmethod
    def from_entity(cls, user: User) -> UserResponse:
        return cls(
            id=str(user.id),
            user_name=user.user_name,
            email=user.email,
            phone_number=user.phone_number,
            role=user.role,
            active_status=user.active_status or False,
            img_url=user.img_url,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
class UpdateImgRequest(BaseModel):
    img_url: str = Field(max_length=500)

class UpdateRoleRequest(BaseModel):
    role: UserRole

class CreateClientRequest(BaseModel):
    user_id: str
    plan_id: int

class UpdateClientRequest(BaseModel):
    plan_id: int 

class ClientResponse(BaseModel):
    id: int
    user: UserResponse
    plan: PlanResponse
    
    @classmethod
    def from_entity(cls, client: Client) -> ClientResponse:
        return cls(
            id=client.id,
            user=UserResponse.from_entity(client.user),
            plan=PlanResponse.from_entity(client.plan)
        )