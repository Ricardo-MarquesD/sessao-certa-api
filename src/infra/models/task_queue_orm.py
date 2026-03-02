from sqlalchemy import Column, Integer, DateTime, ForeignKey, func, Text, Enum, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR
from config import Base
from utils.enum import TaskType, TaskStatus
import uuid

class TaskQueueModel(Base):
    __tablename__ = "tasks_queue"

    id = Column(Integer, primary_key=True, nullable=False)
    uuid = Column(CHAR(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False)
    establishments_id = Column(Integer, ForeignKey("establishments.id", ondelete="CASCADE"), nullable=False)
    task_type = Column(Enum(TaskType), nullable=False)
    priority = Column(Integer, nullable=False, server_default="0")
    status = Column(Enum(TaskStatus), nullable=False, server_default="PENDING")
    payload = Column(JSON, nullable=False)
    retry_count = Column(Integer, server_default="0")
    max_retry = Column(Integer, server_default="3")
    error_mensage = Column(Text, nullable=True)
    next_retry_at = Column(DateTime, nullable=True)
    result_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    establishment = relationship("EstablishmentModel", backref="tasks_queue", foreign_keys=[establishments_id])

    __table_args__ = (
        Index("idx_task_processing", "status", "priority", "created_at"),
    )

    def __repr__(self):
        return (
            f"<TaskQueue(id={self.id}, uuid={self.uuid}, task_type={self.task_type.value}, "
            f"status={self.status.value}, priority={self.priority})>"
        )

    def to_dict(self):
        return {
            "id": self.uuid,
            "establishments_id": self.establishments_id,
            "task_type": self.task_type.value,
            "priority": self.priority,
            "status": self.status.value,
            "payload": self.payload,
            "retry_count": self.retry_count,
            "max_retry": self.max_retry,
            "error_mensage": self.error_mensage,
            "next_retry_at": self.next_retry_at.strftime("%Y-%m-%d %H:%M:%S") if self.next_retry_at else None,
            "result_data": self.result_data,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "started_at": self.started_at.strftime("%Y-%m-%d %H:%M:%S") if self.started_at else None,
            "completed_at": self.completed_at.strftime("%Y-%m-%d %H:%M:%S") if self.completed_at else None,
        }
