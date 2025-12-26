from abc import ABC, abstractmethod
from domain.entities.marketing_message import MarketingMessage

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
    def list_all(self) -> list[MarketingMessage] | list[None]:
        pass
    
    @abstractmethod
    def list_by_establishment_id(self, establishment_id: str) -> list[MarketingMessage] | list[None]:
        pass
    
    @abstractmethod
    def delete(self, marketing_message_id: int) -> bool:
        pass
