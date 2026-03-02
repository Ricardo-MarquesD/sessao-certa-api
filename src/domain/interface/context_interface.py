from abc import ABC, abstractmethod
from domain.entities.context import Context
from utils.value_object import PaginatedResponse
from uuid import UUID


class ContextInterface(ABC):

    @abstractmethod
    def create(self, context: Context) -> Context:
        pass

    @abstractmethod
    def update(self, context: Context) -> Context:
        pass

    @abstractmethod
    def get_by_id(self, context_id: UUID) -> Context | None:
        pass

    @abstractmethod
    def get_open_by_phone_number(self, phone_number: str, establishment_id: int) -> Context | None:
        pass

    @abstractmethod
    def list_all(self, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Context]:
        pass

    @abstractmethod
    def list_by_establishment_id(self, establishment_id: int, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Context]:
        pass

    @abstractmethod
    def list_expired(self, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Context]:
        pass

    @abstractmethod
    def delete(self, context_id: UUID) -> bool:
        pass

    @abstractmethod
    def delete_expired(self, establishment_id: int) -> int:
        """Delete all expired contexts for an establishment. Returns the number of deleted rows."""
        pass
