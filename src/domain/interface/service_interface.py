from abc import ABC, abstractmethod
from domain.entities.service import Service

class ServiceInterface(ABC):
    
    @abstractmethod
    def create(self, service: Service) -> Service:
        pass
    
    @abstractmethod
    def update(self, service: Service) -> Service:
        pass
    
    @abstractmethod
    def get_by_id(self, service_id: str) -> Service | None:
        pass
    
    @abstractmethod
    def list_all(self) -> list[Service] | list[None]:
        pass
    
    @abstractmethod
    def list_by_establishment_id(self, establishment_id: str) -> list[Service] | list[None]:
        pass
    
    @abstractmethod
    def list_active_by_establishment_id(self, active: bool, establishment_id: str) -> list[Service] | list[None]:
        pass
    
    @abstractmethod
    def delete(self, service_id: str) -> bool:
        pass