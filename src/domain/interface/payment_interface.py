from abc import ABC, abstractmethod
from domain.entities.payment import Payment
from utils.enum.payment_enum import PaymentStatus, PaymentType
from datetime import datetime

class PaymentInterface(ABC):
    
    @abstractmethod
    def create(self, payment: Payment) -> Payment:
        pass
    
    @abstractmethod
    def update(self, payment: Payment) -> Payment:
        pass
    
    @abstractmethod
    def get_by_id(self, payment_id: str) -> Payment | None:
        pass
    
    @abstractmethod
    def list_all(self) -> list[Payment]:
        pass
    
    @abstractmethod
    def list_by_establishment_id(self, establishment_id: str) -> list[Payment]:
        pass
    
    @abstractmethod
    def list_by_status(self, status: PaymentStatus) -> list[Payment]:
        pass
    
    @abstractmethod
    def list_by_type(self, payment_type: PaymentType) -> list[Payment]:
        pass
    
    @abstractmethod
    def list_by_due_date_range(self, start_date: datetime, end_date: datetime) -> list[Payment]:
        pass
    
    @abstractmethod
    def delete(self, payment_id: str) -> bool:
        pass
