from abc import ABC, abstractmethod
from domain.entities import User
from utils.enum import UserRole
from utils.value_object import PaginatedResponse
from uuid import UUID

class UserInterface(ABC):

    @abstractmethod
    def create(self, user: User) -> User:
        pass

    @abstractmethod
    def update(self, user: User) -> User:
        pass

    @abstractmethod
    def get_by_id(self, user_id: UUID) -> User | None:
        pass

    @abstractmethod
    def get_by_email(self, email:str) -> User | None:
        pass

    @abstractmethod
    def get_by_phone_number(self, phone_number:str) -> User | None:
        pass

    @abstractmethod
    def list_all(self, cursor: str | None = None, limit: int = 15, total_status: bool = None) -> PaginatedResponse[User]:
        pass

    @abstractmethod
    def list_all_by_active(self, active_status: bool, cursor: str | None = None, limit: int = 15, total_status: bool = None) -> PaginatedResponse[User]:
        pass

    @abstractmethod
    def list_by_role(self, role: UserRole, cursor: str | None = None, limit: int = 15, total_status: bool = None) -> PaginatedResponse[User]:
        pass

    @abstractmethod
    def search_by_user_name(self, user_name: str, cursor: str | None = None, limit: int = 15, total_status: bool = None) -> PaginatedResponse[User]:
        pass

    @abstractmethod
    def delete(self, user_id: UUID) -> bool:
        pass