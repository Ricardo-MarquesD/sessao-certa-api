from abc import  ABC, abstractmethod
from domain.entities import Establishment
from utils.value_object import PaginatedResponse
from uuid import UUID

class EstablishmentInterface(ABC):

    @abstractmethod
    def create(self, establishment: Establishment) -> Establishment:
        pass

    @abstractmethod
    def update(self, establishment: Establishment) -> Establishment:
        pass

    @abstractmethod
    def get_by_id(self, establishment_id: UUID) -> Establishment | None:
        pass

    @abstractmethod
    def get_by_client_id(self, client_id: int) -> Establishment | None:
        pass

    @abstractmethod
    def get_by_cnpj(self, cnpj: str) -> Establishment | None:
        pass

    @abstractmethod
    def list_all(self, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Establishment]:
        pass

    @abstractmethod
    def list_all_by_trial_active(self, trial_active: bool, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Establishment]:
        pass

    @abstractmethod
    def list_with_due_date_expired(self, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Establishment]:
        pass

    @abstractmethod
    def search_by_establishment_name(self, establishment_name: UUID, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Establishment]:
        pass

    @abstractmethod
    def delete(self, establishment_id: UUID) -> bool:
        pass