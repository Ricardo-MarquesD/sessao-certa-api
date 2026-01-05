import pytest
from infra.repository import EmployeeRepository


class TestEmployeeRepository:
    """Testes para EmployeeRepository"""

    def test_get_by_id(self, db_session, sample_employee):
        """Testa busca por ID"""
        repo = EmployeeRepository(db_session)
        
        found = repo.get_by_id(sample_employee.id)
        
        assert found is not None
        assert found.id == sample_employee.id

    def test_get_by_user_id(self, db_session, sample_employee, sample_employee_user):
        """Testa busca por user_id"""
        repo = EmployeeRepository(db_session)
        
        found = repo.get_by_user_id(sample_employee_user.uuid)
        
        assert found is not None
        assert found.user.id == sample_employee_user.uuid

    def test_list_all(self, db_session, sample_employee):
        """Testa listagem de todos os funcionários"""
        repo = EmployeeRepository(db_session)
        
        result = repo.list_all(limit=10)
        
        assert result.data is not None
        assert len(result.data) > 0

    def test_list_by_establishment_id(self, db_session, sample_employee, sample_establishment):
        """Testa listagem por establishment_id"""
        repo = EmployeeRepository(db_session)
        
        result = repo.list_by_establishment_id(
            establishment_id=sample_establishment.uuid,
            limit=10
        )
        
        assert result.data is not None

    def test_count_by_establishment_id(self, db_session, sample_employee, sample_establishment):
        """Testa contagem por establishment_id"""
        repo = EmployeeRepository(db_session)
        
        count = repo.count_by_establishment_id(sample_establishment.uuid)
        
        assert count >= 1

    def test_delete_employee(self, db_session, sample_employee):
        """Testa deleção de funcionário"""
        repo = EmployeeRepository(db_session)
        
        employee_id = sample_employee.id
        success = repo.delete(employee_id)
        
        assert success is True
        
        found = repo.get_by_id(employee_id)
        assert found is None
