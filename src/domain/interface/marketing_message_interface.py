from abc import ABC, abstractmethod
from domain.entities import MarketingMessage
from utils.value_object import PaginatedResponse
from uuid import UUID

class MarketingMessageInterface(ABC):
    
    @abstractmethod
    def create(self, marketing_message: MarketingMessage) -> MarketingMessage:
        pass
    
    @abstractmethod
    def update(self, marketing_message: MarketingMessage) -> MarketingMessage:
        pass
    
    @abstractmethod
    def get_by_id(self, marketing_message_id: int) -> MarketingMessage | None:
        pass
    
    @abstractmethod
    def list_all(self, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[MarketingMessage]:
        pass
    
    @abstractmethod
    def list_by_establishment_id(self, establishment_id: UUID, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[MarketingMessage]:
        pass
    
    @abstractmethod
    def delete(self, marketing_message_id: int) -> bool:
        pass
