from abc import ABC, abstractmethod
from domain.entities.employee import Employee

class EmployeeInterface(ABC):
    
    @abstractmethod
    def create(self, employee: Employee) -> Employee:
        pass
    
    @abstractmethod
    def update(self, employee: Employee) -> Employee:
        pass
    
    @abstractmethod
    def get_by_id(self, employee_id: str) -> Employee | None:
        pass
    
    @abstractmethod
    def get_by_user_id(self, user_id: str) -> Employee | None:
        pass
    
    @abstractmethod
    def list_all(self) -> list[Employee] | list[None]:
        pass
    
    @abstractmethod
    def list_by_establishment_id(self, establishment_id: str) -> list[Employee] | list[None]:
        pass
    
    @abstractmethod
    def count_by_establishment_id(self, establishment_id: str) -> int:
        pass
    
    @abstractmethod
    def delete(self, employee_id: str) -> bool:
        pass