from abc import ABC, abstractmethod
from domain.entities import Plan
from utils.enum import TypePlan
from utils.value_object import PaginatedResponse

class PlanInterface(ABC):

    @abstractmethod
    def create(self, plan: Plan) -> Plan:
        pass

    @abstractmethod
    def update(self, plan: Plan) -> Plan:
        pass

    @abstractmethod
    def get_by_id(self, plan_id: int) -> Plan | None:
        pass

    @abstractmethod
    def get_by_max_employee(self, max_employee: int) -> Plan | None:
        pass

    @abstractmethod
    def list_all(self, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Plan]:
        pass

    @abstractmethod
    def list_by_type(self, type_plan: TypePlan, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Plan]:
        pass

    @abstractmethod
    def list_by_allow_stock(self, allow_stock: bool, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Plan]:
        pass

    @abstractmethod
    def list_by_allow_advanced_analysis(self, allow_advanced_analysis: bool, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Plan]:
        pass

    @abstractmethod
    def list_by_max_employee(self, max_employee: int, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[Plan]:
        pass

    @abstractmethod
    def delete(self, plan_id: int) -> bool:
        pass