from middleware.task_queue import TaskQueueFactory
from utils.enum import TaskStatus, TaskType


def test_sync_calendar_factory_builds_task():
    task = TaskQueueFactory.sync_calendar(
        establishments_id=7,
        scheduling_id="schedule-uuid-123",
        action="create",
        priority=2,
        max_retry=4,
    )

    assert task.task_type == TaskType.SYNC_CALENDAR
    assert task.status == TaskStatus.PENDING
    assert task.establishments_id == 7
    assert task.payload == {"scheduling_id": "schedule-uuid-123", "action": "create"}
    assert task.priority == 2
    assert task.max_retry == 4