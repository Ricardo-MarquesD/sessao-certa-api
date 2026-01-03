from abc import ABC, abstractmethod
from domain.entities import Employee
from utils.value_object import PaginatedResponse
from uuid import UUID

class EmployeeInterface(ABC):
    
    @abstractmethod
    def create(self, employee: Employee) -> Employee:
        pass
    
    @abstractmethod
    def update(self, employee: Employee) -> Employee:
        pass
    
    @abstractmethod
    def get_by_id(self, employee_id: int) -> Employee | None:
        pass
    
    @abstractmethod
    def get_by_user_id(self, user_id: UUID) -> Employee | None:
        pass
    
    @abstractmethod
    def list_all(self, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Employee]:
        pass
    
    @abstractmethod
    def list_by_establishment_id(self, establishment_id: UUID, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Employee]:
        pass
    
    @abstractmethod
    def count_by_establishment_id(self, establishment_id: UUID) -> int:
        pass
    
    @abstractmethod
    def delete(self, employee_id: UUID) -> bool:
        pass