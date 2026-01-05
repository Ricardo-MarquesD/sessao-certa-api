import pytest
from datetime import datetime
from infra.repository import StockProductRepository, StockMovementRepository
from utils.enum import MovementType


class TestStockProductRepository:
    """Testes para StockProductRepository"""

    def test_get_by_id(self, db_session, sample_stock_product):
        """Testa busca por ID"""
        repo = StockProductRepository(db_session)
        
        found = repo.get_by_id(sample_stock_product.id)
        
        assert found is not None
        assert found.id == sample_stock_product.id

    def test_get_by_name_and_establishment(self, db_session, sample_stock_product, sample_establishment):
        """Testa busca por nome e estabelecimento"""
        repo = StockProductRepository(db_session)
        
        found = repo.get_by_name_and_establishment(
            product_name=sample_stock_product.product_name,
            establishment_id=str(sample_establishment.uuid)
        )
        
        assert found is not None
        assert found.product_name == sample_stock_product.product_name

    def test_list_all(self, db_session, sample_stock_product):
        """Testa listagem de todos os produtos"""
        repo = StockProductRepository(db_session)
        
        result = repo.list_all(limit=10)
        
        assert result.data is not None
        assert len(result.data) > 0

    def test_list_by_establishment_id(self, db_session, sample_stock_product, sample_establishment):
        """Testa listagem por establishment_id"""
        repo = StockProductRepository(db_session)
        
        result = repo.list_by_establishment_id(
            establishment_id=str(sample_establishment.uuid),
            limit=10
        )
        
        assert result.data is not None

    def test_list_available_by_establishment_id(self, db_session, sample_stock_product, sample_establishment):
        """Testa listagem de produtos disponíveis"""
        repo = StockProductRepository(db_session)
        
        result = repo.list_available_by_establishment_id(
            establishment_id=str(sample_establishment.uuid),
            limit=10
        )
        
        assert result.data is not None
        for product in result.data:
            assert product.quantity > 0

    def test_delete_stock_product(self, db_session, sample_stock_product):
        """Testa deleção de produto"""
        repo = StockProductRepository(db_session)
        
        product_id = sample_stock_product.id
        success = repo.delete(product_id)
        
        assert success is True
        
        found = repo.get_by_id(product_id)
        assert found is None


class TestStockMovementRepository:
    """Testes para StockMovementRepository"""

    def test_get_by_id(self, db_session, sample_stock_movement):
        """Testa busca por ID"""
        repo = StockMovementRepository(db_session)
        
        found = repo.get_by_id(sample_stock_movement.id)
        
        assert found is not None
        assert found.id == sample_stock_movement.id

    def test_list_all(self, db_session, sample_stock_movement):
        """Testa listagem de todas as movimentações"""
        repo = StockMovementRepository(db_session)
        
        result = repo.list_all(limit=10)
        
        assert result.data is not None
        assert len(result.data) > 0

    def test_list_by_stock_product_id(self, db_session, sample_stock_movement, sample_stock_product):
        """Testa listagem por stock_product_id"""
        repo = StockMovementRepository(db_session)
        
        result = repo.list_by_stock_product_id(
            stock_product_id=sample_stock_product.id,
            limit=10
        )
        
        assert result.data is not None

    def test_list_by_movement_type(self, db_session, sample_stock_movement):
        """Testa listagem por tipo de movimentação"""
        repo = StockMovementRepository(db_session)
        
        result = repo.list_by_movement_type(
            movement_type=MovementType.INPUT,
            limit=10
        )
        
        assert result.data is not None

    def test_list_by_date_range(self, db_session, sample_stock_movement):
        """Testa listagem por intervalo de datas"""
        repo = StockMovementRepository(db_session)
        
        start_date = datetime(2026, 1, 1)
        end_date = datetime(2026, 12, 31)
        
        result = repo.list_by_date_range(
            start_date=start_date,
            end_date=end_date,
            limit=10
        )
        
        assert result.data is not None

    def test_delete_stock_movement(self, db_session, sample_stock_movement):
        """Testa deleção de movimentação"""
        repo = StockMovementRepository(db_session)
        
        movement_id = sample_stock_movement.id
        success = repo.delete(movement_id)
        
        assert success is True
        
        found = repo.get_by_id(movement_id)
        assert found is None
