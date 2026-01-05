from abc import ABC, abstractmethod
from domain.entities import Scheduling
from utils.enum import AppointmentStatus
from utils.value_object import PaginatedResponse
from datetime import datetime
from uuid import UUID

class SchedulingInterface(ABC):
    
    @abstractmethod
    def create(self, scheduling: Scheduling) -> Scheduling:
        pass
    
    @abstractmethod
    def update(self, scheduling: Scheduling) -> Scheduling:
        pass
    
    @abstractmethod
    def get_by_id(self, scheduling_id: UUID) -> Scheduling | None:
        pass
    
    @abstractmethod
    def list_all(self, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Scheduling]:
        pass
    
    @abstractmethod
    def list_by_establishment_id(self, establishment_id: UUID, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Scheduling]:
        pass
    
    @abstractmethod
    def list_by_employee_id(self, employee_id: int, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Scheduling]:
        pass
    
    @abstractmethod
    def list_by_customer_id(self, customer_id: UUID, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Scheduling]:
        pass
    
    @abstractmethod
    def list_by_date_range(self, start_date: datetime, end_date: datetime, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Scheduling]:
        pass
    
    @abstractmethod
    def list_by_status(self, status: AppointmentStatus, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Scheduling]:
        pass
    
    @abstractmethod
    def delete(self, scheduling_id: UUID) -> bool:
        pass
