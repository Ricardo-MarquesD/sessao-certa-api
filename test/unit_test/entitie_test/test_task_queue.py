import pytest
from datetime import datetime, timedelta
from domain.entities.task_queue import TaskQueue
from utils.enum import TaskType, TaskStatus


class TestTaskQueueEntity:
    """Testes unitários para a entidade TaskQueue"""

    @pytest.fixture
    def valid_task(self):
        """Fixture para criar uma task válida"""
        return TaskQueue(
            id="task-uuid-123",
            establishments_id=1,
            task_type=TaskType.SEND_MENSAGE,
            priority=5,
            status=TaskStatus.PENDING,
            payload={"phone": "+5511999998888", "message": "Olá!"},
            retry_count=0,
            max_retry=3,
            error_mensage=None,
            next_retry_at=None,
            result_data=None,
            created_at=datetime.now(),
            started_at=None,
            completed_at=None,
        )

    def test_create_task_with_valid_data(self, valid_task):
        """Testa criação de task com dados válidos"""
        assert valid_task.task_type == TaskType.SEND_MENSAGE
        assert valid_task.status == TaskStatus.PENDING
        assert valid_task.priority == 5

    def test_create_task_with_invalid_task_type_raises_error(self):
        """Testa que task_type inválido levanta erro"""
        with pytest.raises(ValueError, match="task_type must be a TaskType enum"):
            TaskQueue(
                id="task-uuid-123",
                establishments_id=1,
                task_type="INVALID_TYPE",
                priority=0,
                status=TaskStatus.PENDING,
                payload={},
                retry_count=0,
                max_retry=3,
                error_mensage=None,
                next_retry_at=None,
                result_data=None,
                created_at=None,
                started_at=None,
                completed_at=None,
            )

    def test_create_task_with_invalid_status_raises_error(self):
        """Testa que status inválido levanta erro"""
        with pytest.raises(ValueError, match="status must be a TaskStatus enum"):
            TaskQueue(
                id="task-uuid-123",
                establishments_id=1,
                task_type=TaskType.SYNC_CALENDAR,
                priority=0,
                status="WRONG",
                payload={},
                retry_count=0,
                max_retry=3,
                error_mensage=None,
                next_retry_at=None,
                result_data=None,
                created_at=None,
                started_at=None,
                completed_at=None,
            )

    def test_create_task_with_invalid_payload_raises_error(self):
        """Testa que payload inválido levanta erro"""
        with pytest.raises(ValueError, match="payload must be a dict"):
            TaskQueue(
                id="task-uuid-123",
                establishments_id=1,
                task_type=TaskType.CLEANUP_CONTEXT,
                priority=0,
                status=TaskStatus.PENDING,
                payload="not a dict",
                retry_count=0,
                max_retry=3,
                error_mensage=None,
                next_retry_at=None,
                result_data=None,
                created_at=None,
                started_at=None,
                completed_at=None,
            )

    def test_create_task_with_negative_priority_raises_error(self):
        """Testa que prioridade negativa levanta erro"""
        with pytest.raises(ValueError, match="priority must be a non-negative integer"):
            TaskQueue(
                id="task-uuid-123",
                establishments_id=1,
                task_type=TaskType.SEND_MENSAGE,
                priority=-1,
                status=TaskStatus.PENDING,
                payload={},
                retry_count=0,
                max_retry=3,
                error_mensage=None,
                next_retry_at=None,
                result_data=None,
                created_at=None,
                started_at=None,
                completed_at=None,
            )

    def test_is_retryable_returns_true_when_failed_and_under_max(self, valid_task):
        """Testa is_retryable() retorna True quando falhou e ainda tem tentativas"""
        valid_task.status = TaskStatus.FAILED
        valid_task.retry_count = 1
        valid_task.max_retry = 3
        assert valid_task.is_retryable() is True

    def test_is_retryable_returns_false_when_max_retries_reached(self, valid_task):
        """Testa is_retryable() retorna False quando max_retry atingido"""
        valid_task.status = TaskStatus.FAILED
        valid_task.retry_count = 3
        valid_task.max_retry = 3
        assert valid_task.is_retryable() is False

    def test_is_retryable_returns_false_when_not_failed(self, valid_task):
        """Testa is_retryable() retorna False quando status não é FAILED"""
        valid_task.status = TaskStatus.COMPLETED
        assert valid_task.is_retryable() is False

    def test_can_process_returns_true_when_pending(self, valid_task):
        """Testa can_process() retorna True quando status é PENDING"""
        assert valid_task.can_process() is True

    def test_can_process_returns_false_when_not_pending(self, valid_task):
        """Testa can_process() retorna False quando status não é PENDING"""
        valid_task.status = TaskStatus.PROCESSING
        assert valid_task.can_process() is False

    def test_to_dict_returns_correct_structure(self, valid_task):
        """Testa to_dict() retorna estrutura correta"""
        task_dict = valid_task.to_dict()
        assert task_dict["task_type"] == TaskType.SEND_MENSAGE.value
        assert task_dict["status"] == TaskStatus.PENDING.value
        assert task_dict["priority"] == 5
        assert isinstance(task_dict["payload"], dict)

    def test_from_dict_creates_task_correctly(self):
        """Testa from_dict() cria task corretamente"""
        data = {
            "id": "task-456",
            "establishments_id": 2,
            "task_type": "sync_calendar",
            "priority": 10,
            "status": "PROCESSING",
            "payload": {"calendar_id": "cal123"},
            "retry_count": 1,
            "max_retry": 5,
            "error_mensage": None,
            "next_retry_at": None,
            "result_data": None,
            "created_at": "2026-01-01T10:00:00",
            "started_at": "2026-01-01T10:01:00",
            "completed_at": None,
        }

        task = TaskQueue.from_dict(data)

        assert task.id == "task-456"
        assert task.task_type == TaskType.SYNC_CALENDAR
        assert task.status == TaskStatus.PROCESSING
        assert task.priority == 10
