import pytest
from datetime import datetime
from infra.repository import SchedulingRepository
from utils.enum import AppointmentStatus


class TestSchedulingRepository:
    """Testes para SchedulingRepository"""

    def test_get_by_id(self, db_session, sample_scheduling):
        """Testa busca por ID"""
        repo = SchedulingRepository(db_session)
        
        found = repo.get_by_id(sample_scheduling.uuid)
        
        assert found is not None
        assert found.id == sample_scheduling.uuid

    def test_list_all(self, db_session, sample_scheduling):
        """Testa listagem de todos os agendamentos"""
        repo = SchedulingRepository(db_session)
        
        result = repo.list_all(limit=10)
        
        assert result.data is not None
        assert len(result.data) > 0

    def test_list_by_establishment_id(self, db_session, sample_scheduling, sample_establishment):
        """Testa listagem por establishment_id"""
        repo = SchedulingRepository(db_session)
        
        result = repo.list_by_establishment_id(
            establishment_id=sample_establishment.uuid,
            limit=10
        )
        
        assert result.data is not None

    def test_list_by_employee_id(self, db_session, sample_scheduling, sample_employee):
        """Testa listagem por employee_id"""
        repo = SchedulingRepository(db_session)
        
        result = repo.list_by_employee_id(
            employee_id=sample_employee.id,
            limit=10
        )
        
        assert result.data is not None

    def test_list_by_customer_id(self, db_session, sample_scheduling, sample_customer):
        """Testa listagem por customer_id"""
        repo = SchedulingRepository(db_session)
        
        result = repo.list_by_customer_id(
            customer_id=sample_customer.uuid,
            limit=10
        )
        
        assert result.data is not None

    def test_list_by_date_range(self, db_session, sample_scheduling):
        """Testa listagem por intervalo de datas"""
        repo = SchedulingRepository(db_session)
        
        start_date = datetime(2026, 1, 1)
        end_date = datetime(2026, 12, 31)
        
        result = repo.list_by_date_range(
            start_date=start_date,
            end_date=end_date,
            limit=10
        )
        
        assert result.data is not None

    def test_list_by_status(self, db_session, sample_scheduling):
        """Testa listagem por status"""
        repo = SchedulingRepository(db_session)
        
        result = repo.list_by_status(
            status=AppointmentStatus.SCHEDULED,
            limit=10
        )
        
        assert result.data is not None

    def test_delete_scheduling(self, db_session, sample_scheduling):
        """Testa deleção de agendamento"""
        repo = SchedulingRepository(db_session)
        
        scheduling_uuid = sample_scheduling.uuid
        success = repo.delete(scheduling_uuid)
        
        assert success is True
        
        found = repo.get_by_id(scheduling_uuid)
        assert found is None
