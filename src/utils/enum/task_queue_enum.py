from enum import Enum

class TaskType(str, Enum):
    SEND_MENSAGE = "send_mensage"
    SYNC_CALENDAR = "sync_calendar"
    CLEANUP_CONTEXT = "cleanup_context"

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
