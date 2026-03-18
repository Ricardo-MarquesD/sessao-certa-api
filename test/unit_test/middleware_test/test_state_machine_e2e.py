import pytest
from unittest.mock import MagicMock
from datetime import datetime, timedelta, date
from uuid import uuid4

from domain.entities import Context
from middleware.state_machine import StateMachine
from utils.enum import FlowState


def make_context():
    return Context(
        id=uuid4(),
        establishments_id=1,
        customers_id=10,
        phone_number="11999999999",
        last_message_id=None,
        context_arrow=FlowState.initial_message.value,
        is_open=True,
        context_data={},
        created_at=datetime.now(),
        updated_at=datetime.now(),
        expires_at=datetime.now() + timedelta(days=1),
    )


def test_state_machine_e2e_happy_path(monkeypatch):
    ctx = make_context()
    mock_db = MagicMock()

    # Prepare fake service
    fake_service = MagicMock()
    fake_service.id = uuid4()
    fake_service.service_name = "Corte"
    fake_service.time_duration = 30
    fake_service.calculate_end_time.side_effect = lambda start: start + timedelta(minutes=30)
    fake_service.establishment = MagicMock()

    # Prepare employees fallback
    fake_user = MagicMock()
    fake_user.user_name = "Ana"
    fake_emp = MagicMock()
    fake_emp.id = 3
    fake_emp.user = fake_user
    fake_emp.available_hours = {
        "monday": ["08:00", "18:00"],
        "tuesday": ["08:00", "18:00"],
        "wednesday": ["08:00", "18:00"],
        "thursday": ["08:00", "18:00"],
        "friday": ["08:00", "18:00"],
        "saturday": ["08:00", "12:00"],
        "sunday": ["08:00", "12:00"],
    }

    # Create repository mocks and inject into StateMachine instances later
    service_repo_mock = MagicMock()
    service_repo_mock.list_active_by_establishment_internal_id.return_value = [fake_service]
    service_repo_mock.get_by_id.return_value = fake_service

    employee_repo_mock = MagicMock()
    employee_repo_mock.list_by_establishment_internal_id.return_value = [fake_emp]
    employee_repo_mock.get_by_id.return_value = fake_emp

    establishment_repo_mock = MagicMock()
    mock_est = MagicMock()
    mock_est.available_hours = fake_emp.available_hours
    establishment_repo_mock.get_by_internal_id.return_value = mock_est

    scheduling_repo_mock = MagicMock()
    scheduling_repo_mock.list_active_by_day_and_scope.return_value = []
    scheduling_repo_mock.create = MagicMock()

    customer_repo_mock = MagicMock()
    customer_repo_mock.get_by_internal_id.return_value = MagicMock()

    # Patch Scheduling constructor to avoid strict entity validation in unit test
    monkeypatch.setattr("middleware.state_machine.Scheduling", MagicMock(return_value=MagicMock()))

    # 1) Menu inicial
    sm = StateMachine(context=ctx, message="", db=mock_db)
    ans = sm.initial_message(single=True, has_scheduling=True)
    assert "1 - Agendar" in ans.anwser

    # 2) Escolhe agendar -> escolhe serviço 1
    sm = StateMachine(context=ctx, message="1", db=mock_db)
    sm.service_repository = service_repo_mock
    sm.employee_repository = employee_repo_mock
    res = sm.service_message(single=False)
    # Service selection should have forwarded to employee prompt
    assert res.next_state == FlowState.employeee_message
    # Persist choice to context (controller would do this)
    ctx.context_data = res.data

    # 3) Sem preferência: obter dias disponíveis (controller faria a persistência entre estados)
    # Persist service choice (simula controller behavior)
    ctx.context_data = res.data

    sm = StateMachine(context=ctx, message="", db=mock_db)
    sm.establishment_repository = establishment_repo_mock
    sm.scheduling_repository = scheduling_repo_mock
    ans_date = sm.date_message(single=True, employee_id=None)
    assert ans_date.next_state == FlowState.date_message
    # Persist available_days in context (controller)
    ctx.context_data = ans_date.data

    # 4) Choose first available day
    # Controller would receive the chosen date and then call hour_message(single=True)
    chosen_date = ctx.context_data.get("available_days")[0]
    sm = StateMachine(context=ctx, message="", db=mock_db)
    sm.service_repository = service_repo_mock
    sm.scheduling_repository = scheduling_repo_mock
    sm.employee_repository = employee_repo_mock
    sm.establishment_repository = establishment_repo_mock
    ans_hour = sm.hour_message(single=True, scheduling_date=chosen_date, employee_id=None)
    assert ans_hour.next_state == FlowState.hour_message
    # Persist available slots as controller would
    ctx.context_data = ans_hour.data

    # 5) Choose first available hour
    sm = StateMachine(context=ctx, message="1", db=mock_db)
    sm.service_repository = service_repo_mock
    sm.scheduling_repository = scheduling_repo_mock
    sm.employee_repository = employee_repo_mock
    sm.establishment_repository = establishment_repo_mock
    ans_confirm = sm.hour_message(single=False)
    assert ans_confirm.next_state == FlowState.confirm_message
    ctx.context_data = ans_confirm.data

    # 6) Confirmar agendamento
    sm = StateMachine(context=ctx, message="1", db=mock_db)
    sm.service_repository = service_repo_mock
    sm.employee_repository = employee_repo_mock
    sm.customer_repository = customer_repo_mock
    sm.scheduling_repository = scheduling_repo_mock
    res = sm.confirm_message()

    sm.scheduling_repository.create.assert_called()
    assert res.next_state == FlowState.complete_message
    assert res.is_end is True


def test_state_machine_e2e_conflict_on_confirm():
    ctx = make_context()
    mock_db = MagicMock()

    # prepare service that lasts 60 minutes
    fake_service = MagicMock()
    fake_service.id = uuid4()
    fake_service.time_duration = 60
    fake_service.calculate_end_time.side_effect = lambda start: start + timedelta(minutes=60)

    # existing appointment overlaps
    existing = MagicMock()
    existing.appointment_date = datetime(2026, 3, 20, 15, 30)
    existing.service = MagicMock()
    existing.service.time_duration = 30

    # repo mocks
    service_repo = MagicMock()
    service_repo.get_by_id.return_value = fake_service

    employee_repo = MagicMock()
    emp_obj = MagicMock(id=5)
    emp_obj.available_hours = {"friday": ["08:00", "18:00"]}
    employee_repo.get_by_id.return_value = emp_obj

    customer_repo = MagicMock()
    customer_repo.get_by_internal_id.return_value = MagicMock()

    sched_repo = MagicMock()
    sched_repo.list_active_by_day_and_scope.return_value = [existing]
    sched_repo.create = MagicMock()

    # context with chosen slot that will conflict
    ctx.context_data = {
        "service_id": str(uuid4()),
        "scheduling_date": "2026-03-20",
        "scheduling_time": "15:00",
        "employee_id": 5,
    }

    sm = StateMachine(context=ctx, message="1", db=mock_db)
    sm.service_repository = service_repo
    sm.employee_repository = employee_repo
    sm.customer_repository = customer_repo
    sm.scheduling_repository = sched_repo

    ans = sm.confirm_message()

    assert "conflito de horário" in ans.anwser.lower()
    assert ans.next_state == FlowState.hour_message
    sched_repo.create.assert_not_called()


def test_state_machine_e2e_list_and_cancel():
    ctx = make_context()
    mock_db = MagicMock()

    # prepare two active schedulings
    s1 = MagicMock()
    s1.id = uuid4()
    s1.service = MagicMock(service_name="Corte")
    s1.employee = MagicMock(user=MagicMock(user_name="Joao"))
    s1.appointment_date = datetime(2026, 3, 21, 10, 0)
    s1.appointment_status = MagicMock()
    s1.can_cancel.return_value = True

    sched_repo = MagicMock()
    sched_repo.list_active_by_customer_internal_id.return_value = [s1]
    sched_repo.get_by_id.return_value = s1
    sched_repo.update = MagicMock()

    sm = StateMachine(context=ctx, message="", db=mock_db)
    sm.scheduling_repository = sched_repo

    # list_message single should show options
    ctx.customers_id = 10
    ans = sm.list_message(single=True)
    assert "meus agendamentos" in ans.anwser.lower() or "olá" in ans.anwser.lower()
    assert ans.data and "active_scheduling_ids" in ans.data

    # simulate user choosing the first item and confirming cancel
    ctx.context_data = {"scheduling_id": str(s1.id)}
    sm = StateMachine(context=ctx, message="1", db=mock_db)
    sm.scheduling_repository = sched_repo
    ans_cancel = sm.cancel_message()

    sched_repo.get_by_id.assert_called_once()
    sched_repo.update.assert_called_once_with(s1)
    assert "sessão desmarcada" in ans_cancel.anwser.lower()


def test_state_machine_e2e_invalid_inputs():
    ctx = make_context()
    mock_db = MagicMock()
    sm = StateMachine(context=ctx, message="nao sei", db=mock_db)

    # calling initial_message with invalid (non-single) should go to error
    ans = sm.initial_message(single=False, has_scheduling=False)
    assert "não foi possível identificar" in ans.anwser.lower()
