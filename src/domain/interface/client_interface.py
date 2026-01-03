from abc import ABC, abstractmethod
from domain.entities import Client
from uuid import UUID
from utils.value_object.pagination import PaginatedResponse

class ClientInterface(ABC):

    @abstractmethod
    def create(self, client: Client) -> Client:
        pass

    @abstractmethod
    def update(self, client: Client) -> Client:
        pass

    @abstractmethod
    def get_by_id(self, client_id: int) -> Client | None:
        pass
    
    @abstractmethod
    def get_by_user_id(self, user_id: UUID) -> Client | None:
        pass

    @abstractmethod
    def list_all(self, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Client]:
        pass
    
    @abstractmethod
    def list_by_plan_id(self, plan_id: int, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Client]:
        pass

    @abstractmethod
    def delete(self, client_id: int) -> bool:
        pass