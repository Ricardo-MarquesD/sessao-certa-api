from abc import ABC, abstractmethod
from domain.entities.customer import Customer

class CustomerInterface(ABC):
    
    @abstractmethod
    def create(self, customer: Customer) -> Customer:
        pass
    
    @abstractmethod
    def update(self, customer: Customer) -> Customer:
        pass
    
    @abstractmethod
    def get_by_id(self, customer_id: str) -> Customer | None:
        pass
    
    @abstractmethod
    def get_by_phone_number(self, phone_number: str, establishment_id: str) -> Customer | None:
        pass
    
    @abstractmethod
    def list_all(self) -> list[Customer]:
        pass
    
    @abstractmethod
    def list_by_establishment_id(self, establishment_id: str) -> list[Customer]:
        pass
    
    @abstractmethod
    def search_by_name(self, name: str, establishment_id: str) -> list[Customer]:
        pass
    
    @abstractmethod
    def delete(self, customer_id: str) -> bool:
        pass