from pydantic import BaseModel, Field
from decimal import Decimal
from domain.entities import Service
from .establishment_schema import EstablishmentResponse

class CreateServiceRequest(BaseModel):
    establishment_id: str
    service_name: str = Field(min_length=1, max_length=255)
    description_service: str | None = Field(default=None, max_length=1000)
    time_duration: int = Field(gt=0)
    price: Decimal | None = Field(default=None, ge=0)
    active: bool = True

class UpdateServiceRequest(BaseModel):
    service_name: str | None = Field(default=None, min_length=1, max_length=255)
    description_service: str | None = Field(default=None, max_length=1000)
    time_duration: int | None = Field(default=None, gt=0)
    price: Decimal | None = Field(default=None, ge=0)

class UpdateServiceStatusRequest(BaseModel):
    active: bool

class ServiceResponse(BaseModel):
    id: str
    establishment_id: str
    service_name: str
    description_service: str | None
    time_duration: int
    price: str | None
    active: bool
    
    @classmethod
    def from_entity(cls, service: Service) -> "ServiceResponse":
        return cls(
            id=str(service.id),
            establishment_id=str(service.establishment.id),
            service_name=service.service_name,
            description_service=service.description_service,
            time_duration=service.time_duration,
            price=str(service.price) if service.price else None,
            active=service.is_active()
        )

class ServiceDetailResponse(BaseModel):
    id: str
    establishment: EstablishmentResponse
    service_name: str
    description_service: str | None
    time_duration: int
    time_duration_formatted: str
    price: str | None
    active: bool
    
    @classmethod
    def from_entity(cls, service: Service) -> ServiceDetailResponse:
        # Formatar duração
        hours = service.time_duration // 60
        minutes = service.time_duration % 60
        
        if hours > 0 and minutes > 0:
            duration_formatted = f"{hours}h {minutes}min"
        elif hours > 0:
            duration_formatted = f"{hours}h"
        else:
            duration_formatted = f"{minutes}min"
        
        return cls(
            id=str(service.id),
            establishment=EstablishmentResponse.from_entity(service.establishment),
            service_name=service.service_name,
            description_service=service.description_service,
            time_duration=service.time_duration,
            time_duration_formatted=duration_formatted,
            price=str(service.price) if service.price else None,
            active=service.is_active()
        )