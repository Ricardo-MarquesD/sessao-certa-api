from abc import ABC, abstractmethod
from domain.entities import Payment
from utils.enum import PaymentStatus, PaymentType
from utils.value_object import PaginatedResponse
from datetime import datetime
from uuid import UUID

class PaymentInterface(ABC):
    
    @abstractmethod
    def create(self, payment: Payment) -> Payment:
        pass
    
    @abstractmethod
    def update(self, payment: Payment) -> Payment:
        pass
    
    @abstractmethod
    def get_by_id(self, payment_id: UUID) -> Payment | None:
        pass
    
    @abstractmethod
    def list_all(self, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Payment]:
        pass
    
    @abstractmethod
    def list_by_establishment_id(self, establishment_id: UUID, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Payment]:
        pass
    
    @abstractmethod
    def list_by_status(self, status: PaymentStatus, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Payment]:
        pass
    
    @abstractmethod
    def list_by_type(self, payment_type: PaymentType, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Payment]:
        pass
    
    @abstractmethod
    def list_by_due_date_range(self, start_date: datetime, end_date: datetime, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Payment]:
        pass
    
    @abstractmethod
    def delete(self, payment_id: UUID) -> bool:
        pass
