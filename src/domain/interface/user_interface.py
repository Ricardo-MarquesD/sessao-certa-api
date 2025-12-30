from abc import ABC, abstractmethod
from domain.entities import User
from utils.enum import UserRole

class UserInterface(ABC):

    @abstractmethod
    def create(self, user: User) -> User:
        pass

    @abstractmethod
    def update(self, user: User) -> User:
        pass

    @abstractmethod
    def get_by_id(self, user_id: str) -> User | None:
        pass

    @abstractmethod
    def get_by_email(self, email:str) -> User | None:
        pass

    @abstractmethod
    def get_by_phone_number(self, phone_number:str) -> User | None:
        pass

    @abstractmethod
    def list_all(self) -> list[User]:
        pass

    @abstractmethod
    def list_all_by_active(self, active_status: bool) -> list[User]:
        pass

    @abstractmethod
    def list_by_role(self, role: UserRole) -> list[User]:
        pass

    @abstractmethod
    def search_by_user_name(self, user_name: str) -> list[User]:
        pass

    @abstractmethod
    def delete(self, user_id: str) -> bool:
        pass