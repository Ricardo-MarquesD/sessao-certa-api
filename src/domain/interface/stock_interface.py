from abc import ABC, abstractmethod
from domain.entities.stock import StockProduct, StockMovement
from utils.enum.stock_enum import MovementType
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
    def list_all(self) -> list[StockProduct]:
        pass
    
    @abstractmethod
    def list_by_establishment_id(self, establishment_id: str) -> list[StockProduct]:
        pass
    
    @abstractmethod
    def list_available_by_establishment_id(self, establishment_id: str) -> list[StockProduct]:
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
    def list_all(self) -> list[StockMovement]:
        pass
    
    @abstractmethod
    def list_by_stock_product_id(self, stock_product_id: int) -> list[StockMovement]:
        pass
    
    @abstractmethod
    def list_by_movement_type(self, movement_type: MovementType) -> list[StockMovement]:
        pass
    
    @abstractmethod
    def list_by_date_range(self, start_date: datetime, end_date: datetime) -> list[StockMovement]:
        pass
    
    @abstractmethod
    def delete(self, stock_movement_id: int) -> bool:
        pass
