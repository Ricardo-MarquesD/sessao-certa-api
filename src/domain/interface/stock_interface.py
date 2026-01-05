from abc import ABC, abstractmethod
from domain.entities import StockProduct, StockMovement
from utils.enum import MovementType
from utils.value_object import PaginatedResponse
from datetime import datetime

class StockProductInterface(ABC):
    
    @abstractmethod
    def create(self, stock_product: StockProduct) -> StockProduct:
        pass
    
    @abstractmethod
    def update(self, stock_product: StockProduct) -> StockProduct:
        pass
    
    @abstractmethod
    def get_by_id(self, stock_product_id: int) -> StockProduct | None:
        pass
    
    @abstractmethod
    def get_by_name_and_establishment(self, product_name: str, establishment_id: str) -> StockProduct | None:
        pass

    @abstractmethod
    def list_all(self, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[StockProduct]:
        pass
    
    @abstractmethod
    def list_by_establishment_id(self, establishment_id: str, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[StockProduct]:
        pass
    
    @abstractmethod
    def list_available_by_establishment_id(self, establishment_id: str, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[StockProduct]:
        pass
    
    @abstractmethod
    def delete(self, stock_product_id: int) -> bool:
        pass


class StockMovementInterface(ABC):
    
    @abstractmethod
    def create(self, stock_movement: StockMovement) -> StockMovement:
        pass
    
    @abstractmethod
    def update(self, stock_movement: StockMovement) -> StockMovement:
        pass
    
    @abstractmethod
    def get_by_id(self, stock_movement_id: int) -> StockMovement | None:
        pass
    
    @abstractmethod
    def list_all(self, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[StockMovement]:
        pass
    
    @abstractmethod
    def list_by_stock_product_id(self, stock_product_id: int, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[StockMovement]:
        pass
    
    @abstractmethod
    def list_by_movement_type(self, movement_type: MovementType, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[StockMovement]:
        pass
    
    @abstractmethod
    def list_by_date_range(self, start_date: datetime, end_date: datetime, cursor: str | None = None, limit: int = 15) -> PaginatedResponse[StockMovement]:
        pass
    
    @abstractmethod
    def delete(self, stock_movement_id: int) -> bool:
        pass
