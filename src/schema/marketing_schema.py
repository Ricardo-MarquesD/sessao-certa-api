from pydantic import BaseModel, Field
from domain.entities import MarketingMessage
from .establishment_schema import EstablishmentResponse

class CreateMarketingMessageRequest(BaseModel):
    establishment_id: str
    title: str | None = Field(default=None, max_length=255)
    content: str | None = Field(default=None, max_length=5000)

class UpdateMarketingMessageRequest(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    content: str | None = Field(default=None, max_length=5000)

class MarketingMessageResponse(BaseModel):
    id: int
    establishment_id: str
    title: str | None
    content: str | None
    
    @classmethod
    def from_entity(cls, message: MarketingMessage) -> MarketingMessageResponse:
        return cls(
            id=message.id,
            establishment_id=str(message.establishment.id),
            title=message.title,
            content=message.content
        )

class MarketingMessageDetailResponse(BaseModel):
    id: int
    establishment: EstablishmentResponse
    title: str | None
    content: str | None
    
    @classmethod
    def from_entity(cls, message: MarketingMessage) -> MarketingMessageDetailResponse:
        return cls(
            id=message.id,
            establishment=EstablishmentResponse.from_entity(message.establishment),
            title=message.title,
            content=message.content
        )