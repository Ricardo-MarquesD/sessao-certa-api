import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from uuid import uuid4

from domain.entities import Context
from middleware.state_machine import StateMachine
from utils.enum import FlowState, AppointmentStatus

@pytest.fixture
def mock_db_session():
    return MagicMock()

@pytest.fixture
def ctx() -> Context:
    return Context(
        id=uuid4(),
        establishments_id=1,
        customers_id=None,
        phone_number="11999999999",
        last_message_id=None,
        context_arrow=FlowState.initial_message.value,
        is_open=True,
        context_data={},
        created_at=datetime.now(),
        updated_at=datetime.now(),
        expires_at=datetime.now()
    )

def test_initial_message_single_with_scheduling(mock_db_session, ctx):
    sm = StateMachine(context=ctx, message="", db=mock_db_session)
    result = sm.initial_message(single=True, has_scheduling=True)
    
    assert result.next_state == FlowState.initial_message
    assert result.is_end is False
    assert "1 - Agendar" in result.anwser
    assert "2 - Meus Agendamentos" in result.anwser
    assert result.data == {'phone_number': "11999999999"}

def test_initial_message_single_without_scheduling(mock_db_session, ctx):
    sm = StateMachine(context=ctx, message="", db=mock_db_session)
    result = sm.initial_message(single=True, has_scheduling=False)
    
    assert result.next_state == FlowState.initial_message
    assert result.is_end is False
    assert "1 - Agendar" in result.anwser
    assert "2 - Meus Agendamentos" not in result.anwser

@patch("middleware.state_machine.StateMachine.service_message")
def test_initial_message_choose_1(mock_service_message, mock_db_session, ctx):
    mock_service_message.return_value = "mocked_response"
    sm = StateMachine(context=ctx, message="1", db=mock_db_session)
    
    result = sm.initial_message(single=False, has_scheduling=False)
    mock_service_message.assert_called_once_with(single=1)
    assert result == "mocked_response"

@patch("middleware.state_machine.StateMachine.list_message")
def test_initial_message_choose_2(mock_list_message, mock_db_session, ctx):
    mock_list_message.return_value = "mocked_list"
    sm = StateMachine(context=ctx, message="2", db=mock_db_session)
    
    result = sm.initial_message(single=False, has_scheduling=True)
    mock_list_message.assert_called_once_with(single=1)
    assert result == "mocked_list"

def test_initial_message_invalid_choice(mock_db_session, ctx):
    sm = StateMachine(context=ctx, message="3", db=mock_db_session)
    result = sm.initial_message(single=False, has_scheduling=False)
    
    assert result.is_end is False
    assert "não foi possível identificar" in result.anwser.lower()


def test_list_message_without_customer_id(mock_db_session, ctx):
    sm = StateMachine(context=ctx, message="", db=mock_db_session)

    result = sm.list_message(single=True)

    assert "nenhum agendamento ativo" in result.anwser.lower()
    assert result.next_state == FlowState.list_message
    assert result.is_end is False


def test_list_message_with_active_scheduling(mock_db_session, ctx):
    ctx.customers_id = 10
    sm = StateMachine(context=ctx, message="", db=mock_db_session)

    fake_service = MagicMock()
    fake_service.service_name = "Corte de Cabelo"

    fake_employee_user = MagicMock()
    fake_employee_user.user_name = "João"

    fake_employee = MagicMock()
    fake_employee.user = fake_employee_user

    fake_sched = MagicMock()
    fake_sched.id = uuid4()
    fake_sched.service = fake_service
    fake_sched.employee = fake_employee
    fake_sched.appointment_date = datetime(2026, 3, 20, 15, 30)
    fake_sched.appointment_status = AppointmentStatus.SCHEDULED

    sm.scheduling_repository = MagicMock()
    sm.scheduling_repository.list_active_by_customer_internal_id.return_value = [fake_sched]

    result = sm.list_message(single=True)

    sm.scheduling_repository.list_active_by_customer_internal_id.assert_called_once_with(10)
    assert "olá, como posso te ajudar?" in result.anwser.lower()
    assert "corte de cabelo" in result.anwser.lower()
    assert "joão" in result.anwser.lower()
    assert "20/03/2026" in result.anwser
    assert "15:30" in result.anwser
    assert "2 - voltar" in result.anwser.lower()
    assert result.next_state == FlowState.list_message
    assert result.is_end is False
    assert result.data["active_scheduling_ids"] == [str(fake_sched.id)]


def test_ok_message_finishes_conversation(mock_db_session, ctx):
    sm = StateMachine(context=ctx, message="", db=mock_db_session)

    result = sm.ok_message()

    assert result.anwser.lower().startswith("ok")
    assert result.next_state == FlowState.ok_message
    assert result.is_end is True


def test_cancel_message_yes_cancels_scheduling(mock_db_session, ctx):
    sched_id = uuid4()
    ctx.context_data = {"scheduling_id": str(sched_id)}

    sm = StateMachine(context=ctx, message="1", db=mock_db_session)

    fake_sched = MagicMock()
    fake_sched.can_cancel.return_value = True

    sm.scheduling_repository = MagicMock()
    sm.scheduling_repository.get_by_id.return_value = fake_sched

    result = sm.cancel_message()

    sm.scheduling_repository.get_by_id.assert_called_once()
    sm.scheduling_repository.update.assert_called_once_with(fake_sched)
    assert result.anwser.startswith("Sessão desmarcada")
    assert result.next_state == FlowState.unmarked_message
    assert result.is_end is True


def test_cancel_message_no_keeps_scheduling(mock_db_session, ctx):
    ctx.context_data = {"scheduling_id": str(uuid4())}

    sm = StateMachine(context=ctx, message="2", db=mock_db_session)

    result = sm.cancel_message()

    assert result.anwser.lower().startswith("ok")
    assert result.next_state == FlowState.ok_message
    assert result.is_end is True


def test_confirm_message_conflict_detected(mock_db_session, ctx):
    ctx.customers_id = 10
    ctx.context_data = {
        "service_id": str(uuid4()),
        "scheduling_date": "2026-03-20",
        "scheduling_time": "15:00",
        "employee_id": 5,
    }

    sm = StateMachine(context=ctx, message="1", db=mock_db_session)

    # Serviço de 60 minutos
    fake_service = MagicMock()
    fake_service.calculate_end_time.side_effect = lambda start: start.replace(hour=start.hour + 1)

    # Agendamento existente das 15:30 às 16:00 (30 minutos)
    existing = MagicMock()
    existing.appointment_date = datetime(2026, 3, 20, 15, 30)
    existing.service.time_duration = 30

    sm.service_repository = MagicMock()
    sm.service_repository.get_by_id.return_value = fake_service

    sm.employee_repository = MagicMock()
    sm.employee_repository.get_by_id.return_value = MagicMock(id=5)

    sm.customer_repository = MagicMock()
    sm.customer_repository.get_by_internal_id.return_value = MagicMock()

    sm.employee_repository.list_by_establishment_internal_id.return_value = [MagicMock(id=5)]

    # hora_message(single=True) em caso de conflito usa a janela de horário
    sm.employee_repository.get_by_id.return_value.available_hours = {"friday": ["08:00", "18:00"]}

    sm.scheduling_repository = MagicMock()
    sm.scheduling_repository.list_active_by_day_and_scope.side_effect = [
        [existing],
        [existing],
    ]

    result = sm.confirm_message()

    assert sm.service_repository.get_by_id.call_count >= 1
    assert sm.scheduling_repository.list_active_by_day_and_scope.call_count >= 1
    assert "conflito de horário" in result.anwser.lower()
    assert result.next_state == FlowState.hour_message
    assert result.is_end is False


@patch("middleware.state_machine.Scheduling")
def test_confirm_message_no_conflict_completes(mock_scheduling_entity, mock_db_session, ctx):
    ctx.customers_id = 10
    ctx.context_data = {
        "service_id": str(uuid4()),
        "scheduling_date": "2026-03-20",
        "scheduling_time": "08:00",
        "employee_id": 3,
    }

    sm = StateMachine(context=ctx, message="1", db=mock_db_session)

    fake_service = MagicMock()
    fake_service.calculate_end_time.side_effect = lambda start: start.replace(hour=start.hour + 1)
    fake_service.establishment = MagicMock()

    sm.service_repository = MagicMock()
    sm.service_repository.get_by_id.return_value = fake_service

    fake_employee = MagicMock()
    fake_employee.id = 3
    sm.employee_repository = MagicMock()
    sm.employee_repository.get_by_id.return_value = fake_employee

    sm.customer_repository = MagicMock()
    sm.customer_repository.get_by_internal_id.return_value = MagicMock()

    sm.scheduling_repository = MagicMock()
    sm.scheduling_repository.list_active_by_day_and_scope.return_value = []

    mock_scheduling_entity.return_value = MagicMock()
    result = sm.confirm_message()

    sm.scheduling_repository.create.assert_called_once()
    assert "agendamento feito com sucesso" in result.anwser.lower()
    assert result.next_state == FlowState.complete_message
    assert result.is_end is True


def test_confirm_message_cancel_branch(mock_db_session, ctx):
    sm = StateMachine(context=ctx, message="2", db=mock_db_session)

    result = sm.confirm_message()

    assert "sessão desmarcada" in result.anwser.lower()
    assert result.next_state == FlowState.unmarked_message
    assert result.is_end is True


def test_full_conversation_flows_with_mocks(mock_db_session, ctx):
        """Teste maior simulando fluxos de conversa principais usando mocks.

        Verifica:
        - Menu inicial.
        - Rota alternativa A: listar último agendamento, confirmar desmarcação,
            e garantir chamada de update no repositório.
        - Rota de confirmação com conflito: tentativa de novo agendamento em
            horário conflitante, retornando mensagem de conflito.
        """

        # ---------- Menu inicial ----------
        sm = StateMachine(context=ctx, message="", db=mock_db_session)
        ans = sm.initial_message(single=True, has_scheduling=True)

        assert "1 - agendar" in ans.anwser.lower()
        assert "2 - meus agendamentos" in ans.anwser.lower()

        # ---------- Rota alternativa A: listar + desmarcar ----------
        ctx.customers_id = 10

        fake_service = MagicMock()
        fake_service.service_name = "Corte"

        fake_employee_user = MagicMock()
        fake_employee_user.user_name = "Maria"

        fake_employee = MagicMock()
        fake_employee.user = fake_employee_user

        fake_sched = MagicMock()
        fake_sched.id = uuid4()
        fake_sched.service = fake_service
        fake_sched.employee = fake_employee
        fake_sched.appointment_date = datetime(2026, 1, 1, 10, 0)
        fake_sched.appointment_status = AppointmentStatus.SCHEDULED
        fake_sched.can_cancel.return_value = True

        sm = StateMachine(context=ctx, message="", db=mock_db_session)
        sched_repo_mock = MagicMock()
        sched_repo_mock.list_active_by_customer_internal_id.return_value = [fake_sched]
        sm.scheduling_repository = sched_repo_mock

        # Usuário escolhe "2 - Meus agendamentos" no menu
        ans_list = sm.list_message(single=True)
        assert "olá, como posso te ajudar" in ans_list.anwser.lower()
        sched_id = ans_list.data["active_scheduling_ids"][0]

        # Controller persiste no contexto para próxima etapa
        ctx.context_data = {"scheduling_id": sched_id}

        # Usuário confirma desmarcar (1 - Sim)
        sm = StateMachine(context=ctx, message="1", db=mock_db_session)
        sm.scheduling_repository = sched_repo_mock  # reaproveita o mesmo mock
        sm.scheduling_repository.get_by_id.return_value = fake_sched

        ans_cancel = sm.cancel_message()

        sm.scheduling_repository.get_by_id.assert_called_once()
        sm.scheduling_repository.update.assert_called_once_with(fake_sched)
        assert "sessão desmarcada" in ans_cancel.anwser.lower()
        assert ans_cancel.next_state == FlowState.unmarked_message

        # ---------- Fluxo de confirmação com conflito ----------
        ctx.context_data = {
                "service_id": str(uuid4()),
                "scheduling_date": "2026-01-02",
                "scheduling_time": "09:00",
                "employee_id": 5,
        }

        sm = StateMachine(context=ctx, message="1", db=mock_db_session)

        fake_service_conflict = MagicMock()
        fake_service_conflict.calculate_end_time.side_effect = lambda start: start.replace(hour=start.hour + 1)

        existing = MagicMock()
        existing.appointment_date = datetime(2026, 1, 2, 9, 30)
        existing.service.time_duration = 30

        sm.service_repository = MagicMock()
        sm.service_repository.get_by_id.return_value = fake_service_conflict

        sm.employee_repository = MagicMock()
        conflict_employee = MagicMock(id=5)
        conflict_employee.available_hours = {"friday": ["08:00", "18:00"]}
        sm.employee_repository.get_by_id.return_value = conflict_employee
        sm.employee_repository.list_by_establishment_internal_id.return_value = [conflict_employee]

        sm.customer_repository = MagicMock()
        sm.customer_repository.get_by_internal_id.return_value = MagicMock()

        sm.scheduling_repository = MagicMock()
        sm.scheduling_repository.list_active_by_day_and_scope.side_effect = [
            [existing],
            [existing],
        ]

        ans_conflict = sm.confirm_message()

        assert sm.service_repository.get_by_id.call_count >= 1
        assert sm.scheduling_repository.list_active_by_day_and_scope.call_count >= 1
        assert "conflito de horário" in ans_conflict.anwser.lower()
        assert ans_conflict.next_state == FlowState.hour_message


def test_list_message_selection_routes_to_cancel(mock_db_session, ctx):
    ctx.customers_id = 10
    fake_sched = MagicMock()
    fake_sched.id = uuid4()

    ctx.context_data = {"active_scheduling_ids": [str(fake_sched.id)]}
    sm = StateMachine(context=ctx, message="1", db=mock_db_session)

    result = sm.list_message(single=False)

    assert "gostaria de desmarcar" in result.anwser.lower()
    assert result.next_state == FlowState.cancel_message
    assert result.is_end is False
    assert result.data["scheduling_id"] == str(fake_sched.id)


def test_list_message_back_to_initial(mock_db_session, ctx):
    ctx.customers_id = 10
    ctx.context_data = {"active_scheduling_ids": [str(uuid4())]}
    sm = StateMachine(context=ctx, message="2", db=mock_db_session)

    result = sm.list_message(single=False)

    assert "1 - agendar" in result.anwser.lower()
    assert "2 - meus agendamentos" in result.anwser.lower()
    assert result.next_state == FlowState.initial_message
