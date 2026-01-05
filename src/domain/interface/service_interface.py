from abc import ABC, abstractmethod
from domain.entities import Service
from utils.value_object import PaginatedResponse
from uuid import UUID

class ServiceInterface(ABC):
    
    @abstractmethod
    def create(self, service: Service) -> Service:
        pass
    
    @abstractmethod
    def update(self, service: Service) -> Service:
        pass
    
    @abstractmethod
    def get_by_id(self, service_id: UUID) -> Service | None:
        pass
    
    @abstractmethod
    def list_all(self, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Service]:
        pass
    
    @abstractmethod
    def list_by_establishment_id(self, establishment_id: UUID, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Service]:
        pass
    
    @abstractmethod
    def list_active_by_establishment_id(self, active: bool, establishment_id: UUID, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Service]:
        pass
    
    @abstractmethod
    def delete(self, service_id: UUID) -> bool:
        pass