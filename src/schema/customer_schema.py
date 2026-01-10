from pydantic import BaseModel, Field
from pydantic_extra_types.phone_numbers import PhoneNumber
from domain.entities import Customer
from uuid import UUID
from schema.establishment_schema import EstablishmentResponse

class CreateCustomerRequest(BaseModel):
    establishment_id: UUID
    customer_name: str = Field(min_length=1, max_length=255)
    phone_number: PhoneNumber = Field(default_region='BR')

class UpdateCustomerRequest(BaseModel):
    customer_name: str | None = Field(default=None, min_length=1, max_length=255)
    phone_number: PhoneNumber | None = Field(default=None, default_region='BR')

class CustomerResponse(BaseModel):
    id: UUID
    establishment_id: UUID
    customer_name: str
    phone_number: str
    
    @classmethod
    def from_entity(cls, customer: Customer) -> CustomerResponse:
        return cls(
            id=customer.id,
            establishment_id=customer.establishment.id,
            customer_name=customer.customer_name,
            phone_number=customer.phone_number
        )

class CustomerDetailResponse(BaseModel):
    id: UUID
    establishment: EstablishmentResponse
    customer_name: str
    phone_number: str
    
    @classmethod
    def from_entity(cls, customer: Customer) -> CustomerDetailResponse:
        return cls(
            id=customer.id,
            establishment=EstablishmentResponse.from_entity(customer.establishment),
            customer_name=customer.customer_name,
            phone_number=customer.phone_number
        )