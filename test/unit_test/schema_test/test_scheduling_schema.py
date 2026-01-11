import pytest
from pydantic import ValidationError
from schema.scheduling_schema import (
    CreateSchedulingRequest,
    UpdateSchedulingRequest,
    UpdateSchedulingStatusRequest,
    CancelSchedulingRequest,
    SchedulingResponse
)
from utils.enum import AppointmentStatus
from datetime import datetime, timedelta
from uuid import uuid4

class TestCreateSchedulingRequest:
    """Testes para CreateSchedulingRequest"""
    
    def test_create_scheduling_request_valid(self):
        """Deve criar scheduling request válido"""
        future_date = datetime.now() + timedelta(days=1)
        data = {
            "establishment_id": uuid4(),
            "employee_id": 1,
            "customer_id": uuid4(),
            "service_id": uuid4(),
            "appointment_date": future_date
        }
        scheduling = CreateSchedulingRequest(**data)
        assert scheduling.employee_id == 1
        assert scheduling.appointment_date > datetime.now()
    
    def test_create_scheduling_request_past_date_fails(self):
        """Deve falhar com data no passado"""
        past_date = datetime.now() - timedelta(days=1)
        data = {
            "establishment_id": uuid4(),
            "employee_id": 1,
            "customer_id": uuid4(),
            "service_id": uuid4(),
            "appointment_date": past_date
        }
        with pytest.raises(ValidationError) as exc:
            CreateSchedulingRequest(**data)
        assert "Appointment date must be in the future" in str(exc.value)

class TestUpdateSchedulingRequest:
    """Testes para UpdateSchedulingRequest"""
    
    def test_update_scheduling_request_valid(self):
        """Deve atualizar scheduling"""
        future_date = datetime.now() + timedelta(days=2)
        data = {
            "appointment_date": future_date,
            "employee_id": 2
        }
        update = UpdateSchedulingRequest(**data)
        assert update.employee_id == 2
        assert update.appointment_date > datetime.now()
    
    def test_update_scheduling_request_past_date_fails(self):
        """Deve falhar com data no passado"""
        past_date = datetime.now() - timedelta(hours=1)
        data = {"appointment_date": past_date}
        with pytest.raises(ValidationError) as exc:
            UpdateSchedulingRequest(**data)
        assert "Appointment date must be in the future" in str(exc.value)
    
    def test_update_scheduling_request_empty(self):
        """Deve aceitar objeto vazio"""
        update = UpdateSchedulingRequest()
        assert update.appointment_date is None
        assert update.employee_id is None

class TestUpdateSchedulingStatusRequest:
    """Testes para UpdateSchedulingStatusRequest"""
    
    def test_update_scheduling_status_request_valid(self):
        """Deve atualizar status"""
        data = {"appointment_status": AppointmentStatus.CONFIRMED}
        update = UpdateSchedulingStatusRequest(**data)
        assert update.appointment_status == AppointmentStatus.CONFIRMED

class TestCancelSchedulingRequest:
    """Testes para CancelSchedulingRequest"""
    
    def test_cancel_scheduling_request_valid(self):
        """Deve cancelar com motivo"""
        data = {"reason": "Cliente não pode comparecer"}
        cancel = CancelSchedulingRequest(**data)
        assert cancel.reason == "Cliente não pode comparecer"
    
    def test_cancel_scheduling_request_without_reason(self):
        """Deve aceitar cancelamento sem motivo"""
        data = {}
        cancel = CancelSchedulingRequest(**data)
        assert cancel.reason is None
    
    def test_cancel_scheduling_request_reason_too_long_fails(self):
        """Deve falhar com motivo muito longo"""
        data = {"reason": "a" * 501}
        with pytest.raises(ValidationError):
            CancelSchedulingRequest(**data)

class TestSchedulingResponse:
    """Testes para SchedulingResponse"""
    
    def test_scheduling_response_valid(self):
        """Deve criar response válido"""
        scheduling_id = uuid4()
        establishment_id = uuid4()
        customer_id = uuid4()
        service_id = uuid4()
        appointment_date = datetime.now() + timedelta(days=1)
        end_time = appointment_date + timedelta(minutes=30)
        
        data = {
            "id": scheduling_id,
            "establishment_id": establishment_id,
            "employee_id": 1,
            "customer_id": customer_id,
            "service_id": service_id,
            "appointment_date": appointment_date,
            "appointment_end_time": end_time,
            "appointment_status": "SCHEDULED",
            "notification_sent": False,
            "created_at": datetime.now(),
            "can_cancel": True
        }
        response = SchedulingResponse(**data)
        assert response.id == scheduling_id
        assert response.appointment_status == "SCHEDULED"
        assert response.can_cancel == True
