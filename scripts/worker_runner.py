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

    interval = float(os.getenv("WORKER_INTERVAL_SECONDS", "5"))
    worker = TaskWorker(session_factory=Session, concurrency=1, task_limit=20)

    print("Worker loop started. Press Ctrl+C to stop.")
    try:
        while True:
            processed = worker.run_once()
            if processed:
                print(f"Processed {len(processed)} task(s)")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Worker stopped.")


if __name__ == "__main__":
    main()
