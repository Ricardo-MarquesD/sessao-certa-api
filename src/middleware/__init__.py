from .task_queue import TaskQueueFactory

__all__ = ["TaskQueueFactory", "TaskWorker"]


def __getattr__(name: str):
	if name == "TaskWorker":
		from .task_worker import TaskWorker

		return TaskWorker

	raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
