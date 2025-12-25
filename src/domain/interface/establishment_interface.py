from abc import  ABC, abstractmethod
from domain.entities import Establishment

class EstablishmentInterface(ABC):

    @abstractmethod
    def create(self, establishment: Establishment) -> Establishment:
        pass

    @abstractmethod
    def update(self, establishment: Establishment) -> Establishment:
        pass

    @abstractmethod
    def get_by_id(self, establishment_id: str) -> Establishment | None:
        pass

    @abstractmethod
    def get_by_client_id(self, client_id: int) -> Establishment | None:
        pass

    @abstractmethod
    def get_by_cnpj(self, cnpj: str) -> Establishment | None:
        pass

    @abstractmethod
    def list_all(self) -> list[Establishment] | list[None]:
        pass

    @abstractmethod
    def list_by_establishment_name(self, establishment_name: str) -> list[Establishment] | list[None]:
        pass

    @abstractmethod
    def list_all_by_trial_active(self, trial_active: bool) -> list[Establishment] | list[None]:
        pass

    @abstractmethod
    def list_with_due_date_expired(self) -> list[Establishment] | None:
        pass

    @abstractmethod
    def delete(self, establishment_id: str) -> bool:
        pass