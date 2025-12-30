from abc import ABC, abstractmethod
from domain.entities.scheduling import Scheduling
from utils.enum.appointment_enum import AppointmentStatus
from datetime import datetime

class SchedulingInterface(ABC):
    
    @abstractmethod
    def create(self, scheduling: Scheduling) -> Scheduling:
        pass
    
    @abstractmethod
    def update(self, scheduling: Scheduling) -> Scheduling:
        pass
    
    @abstractmethod
    def get_by_id(self, scheduling_id: str) -> Scheduling | None:
        pass
    
    @abstractmethod
    def list_all(self) -> list[Scheduling]:
        pass
    
    @abstractmethod
    def list_by_establishment_id(self, establishment_id: str) -> list[Scheduling]:
        pass
    
    @abstractmethod
    def list_by_employee_id(self, employee_id: str) -> list[Scheduling]:
        pass
    
    @abstractmethod
    def list_by_customer_id(self, customer_id: str) -> list[Scheduling]:
        pass
    
    @abstractmethod
    def list_by_date_range(self, start_date: datetime, end_date: datetime) -> list[Scheduling]:
        pass
    
    @abstractmethod
    def list_by_status(self, status: AppointmentStatus) -> list[Scheduling]:
        pass
    
    @abstractmethod
    def delete(self, scheduling_id: str) -> bool:
        pass
