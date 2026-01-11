from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic_extra_types.phone_numbers import PhoneNumber
from domain.entities import User, Client, Employee
from utils.enum import UserRole
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from schema.plan_schema import PlanResponse
    from schema.establishment_schema import EstablishmentResponse

class _UserBase(BaseModel):
    user_name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    phone_number: PhoneNumber = Field(json_schema_extra={'default_region': 'BR'})
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
    phone_number: PhoneNumber | None = Field(default=None, json_schema_extra={'default_region': 'BR'})
    active_status: bool | None = None

class UserResponse(_UserBase):
    id: UUID
    active_status: bool
    img_url: str | None
    created_at: datetime | None
    updated_at: datetime | None

    @classmethod
    def from_entity(cls, user: User) -> UserResponse:
        return cls(
            id=user.id,
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
    user_id: UUID
    plan_id: int

class UpdateClientRequest(BaseModel):
    plan_id: int 

class ClientResponse(BaseModel):
    id: int
    user: UserResponse
    plan: PlanResponse
    
    @classmethod
    def from_entity(cls, client: Client) -> ClientResponse:
        from schema import PlanResponse
        return cls(
            id=client.id,
            user=UserResponse.from_entity(client.user),
            plan=PlanResponse.from_entity(client.plan)
        )
    
class CreateEmployeeRequest(BaseModel):
    user_id: UUID
    establishment_id: UUID
    percentage_commission: Decimal | None = Field(default=None, ge=0, le=100)
    available_hours: Dict[str, List[str]] | None = None
    
    @field_validator('percentage_commission')
    @classmethod
    def validate_commission(cls, v: Decimal | None):
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Commission must be between 0 and 100")
        return v

class UpdateEmployeeRequest(BaseModel):
    percentage_commission: Decimal | None = Field(default=None, ge=0, le=100)
    available_hours: Dict[str, List[str]] | None = None

class UpdateEmployeeAvailabilityRequest(BaseModel):
    available_hours: Dict[str, List[str]]
    # Exemplo: 
    # {
    #   "monday": ["09:00-18:00"],
    #   "tuesday": ["09:00-12:00", "14:00-18:00"],
    #   "wednesday": [],  # Não trabalha
    #   "thursday": ["09:00-18:00"],
    #   "friday": ["09:00-17:00"]
    # }

class EmployeeResponse(BaseModel):
    id: int
    user_id: UUID
    establishment_id: UUID
    percentage_commission: str | None
    available_hours: Dict[str, List[str]] | None
    
    @classmethod
    def from_entity(cls, employee: Employee) -> EmployeeResponse:
        return cls(
            id=employee.id,
            user_id=employee.user.id,
            establishment_id=employee.establishment.id,
            percentage_commission=str(employee.percentage_commission) if employee.percentage_commission else None,
            available_hours=employee.available_hours
        )

class EmployeeDetailResponse(BaseModel):
    id: int
    user: UserResponse
    establishment: EstablishmentResponse
    percentage_commission: str | None
    available_hours: Dict[str, List[str]] | None
    
    @classmethod
    def from_entity(cls, employee: Employee) -> EmployeeDetailResponse:
        from schema import EstablishmentResponse
        return cls(
            id=employee.id,
            user=UserResponse.from_entity(employee.user),
            establishment=EstablishmentResponse.from_entity(employee.establishment),
            percentage_commission=str(employee.percentage_commission) if employee.percentage_commission else None,
            available_hours=employee.available_hours
        )

class EmployeeCommissionResponse(BaseModel):
    employee_id: int
    service_price: str
    commission_percentage: str
    commission_value: str