from pydantic import BaseModel, Field, field_validator
from pydantic_extra_types.phone_numbers import PhoneNumber
from datetime import datetime
from domain.entities import Establishment
from uuid import UUID
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from schema.user_schema import ClientResponse

class CreateEstablishmentRequest(BaseModel):
    client_id: int
    establishment_name: str = Field(min_length=1, max_length=255)
    cnpj: str = Field(min_length=14, max_length=18)
    chatbot_phone_number: PhoneNumber | None = Field(default=None, default_region='BR')
    address: str | None = Field(default=None, max_length=500)
    trial_active: bool = True
    
    @field_validator('cnpj')
    @classmethod
    def validate_cnpj(cls, v: str):
        cnpj_digits = ''.join(filter(str.isdigit, v))
        if len(cnpj_digits) != 14:
            raise ValueError("CNPJ must have exactly 14 digits")
        return cnpj_digits

class UpdateEstablishmentRequest(BaseModel):
    establishment_name: str | None = Field(default=None, min_length=1, max_length=255)
    chatbot_phone_number: PhoneNumber | None = Field(default=None, default_region='BR')
    address: str | None = Field(default=None, max_length=500)
    due_date: datetime | None = None
    trial_active: bool | None = None

class UpdateEstablishmentImgRequest(BaseModel):
    img_url: str = Field(max_length=500)

class EstablishmentResponse(BaseModel):
    id: UUID
    client_id: int
    establishment_name: str
    cnpj: str
    chatbot_phone_number: str | None
    address: str | None
    img_url: str | None
    subscription_date: datetime | None
    due_date: datetime | None
    trial_active: bool
    is_subscription_valid: bool
    
    @classmethod
    def from_entity(cls, establishment: Establishment) -> EstablishmentResponse:
        return cls(
            id=establishment.id,
            client_id=establishment.client.id,
            establishment_name=establishment.establishment_name,
            cnpj=establishment.cnpj,
            chatbot_phone_number=establishment.chatbot_phone_number,
            address=establishment.address,
            img_url=establishment.img_url,
            subscription_date=establishment.subscription_date,
            due_date=establishment.due_date,
            trial_active=establishment.is_trial_active(),
            is_subscription_valid=establishment.is_subscription_valid()
        )

class EstablishmentDetailResponse(BaseModel):
    id: UUID
    client: ClientResponse
    establishment_name: str
    cnpj: str
    chatbot_phone_number: str | None
    address: str | None
    img_url: str | None
    subscription_date: datetime | None
    due_date: datetime | None
    trial_active: bool
    is_subscription_valid: bool
    days_until_due: int | None
    
    @classmethod
    def from_entity(cls, establishment: Establishment) -> EstablishmentDetailResponse:
        from schema import ClientResponse
        time_until_due = establishment.time_until_due()
        
        return cls(
            id=establishment.id,
            client=ClientResponse.from_entity(establishment.client),
            establishment_name=establishment.establishment_name,
            cnpj=establishment.cnpj,
            chatbot_phone_number=establishment.chatbot_phone_number,
            address=establishment.address,
            img_url=establishment.img_url,
            subscription_date=establishment.subscription_date,
            due_date=establishment.due_date,
            trial_active=establishment.is_trial_active(),
            is_subscription_valid=establishment.is_subscription_valid(),
            days_until_due=time_until_due.days if time_until_due else None
        )