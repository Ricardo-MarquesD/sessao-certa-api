import os
import sys
import time
from pathlib import Path


def _ensure_path() -> None:
    root = Path(__file__).resolve().parents[1]
    src = root / "src"
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


def main() -> None:
    _ensure_path()
    from config.db import Session
    from middleware.task_worker import TaskWorker
    from middleware.task_queue import TaskQueueFactory
    from infra.repository import EstablishmentRepository, TaskQueueRepository

    interval = float(os.getenv("WORKER_INTERVAL_SECONDS", "5"))
    deactivation_interval = float(os.getenv("DEACTIVATION_JOB_INTERVAL_SECONDS", "86400"))
    worker = TaskWorker(session_factory=Session, concurrency=1, task_limit=20)
    last_deactivation_run = 0.0

    print("Worker loop started. Press Ctrl+C to stop.")
    try:
        while True:
            now = time.time()
            if now - last_deactivation_run >= deactivation_interval:
                session = Session()
                try:
                    establishment_repo = EstablishmentRepository(session)
                    task_repo = TaskQueueRepository(session)
                    cursor = None
                    total_enqueued = 0

                    while True:
                        page = establishment_repo.list_with_due_date_expired(cursor=cursor, limit=100)
                        for establishment in page.data:
                            internal_id = establishment_repo.get_internal_id_by_id(establishment.id)
                            if internal_id is None:
                                continue
                            task = TaskQueueFactory.deactivate_establishment(
                                establishments_id=internal_id,
                                establishment_id=str(establishment.id),
                            )
                            task_repo.create(task)
                            total_enqueued += 1

                        if not page.has_more or not page.cursor:
                            break
                        cursor = page.cursor
                finally:
                    session.close()

                if total_enqueued:
                    print(f"Enqueued {total_enqueued} deactivation task(s)")
                last_deactivation_run = now

            processed = worker.run_once()
            if processed:
                print(f"Processed {len(processed)} task(s)")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Worker stopped.")


if __name__ == "__main__":
    main()
