"""
Download manager for GrabVid.
Manages download queues, concurrency, and state tracking.
"""

import os
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from queue import Queue, Empty
from typing import Any, Callable, Dict, List, Optional

from .engine import DownloadEngine, DownloadOptions, VideoInfo
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DownloadState(Enum):
    """Download task states."""
    PENDING = "pending"
    QUEUED = "queued"
    DOWNLOADING = "downloading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


@dataclass
class DownloadProgress:
    """Real-time download progress information."""
    progress: float = 0.0
    downloaded: int = 0
    total: int = 0
    speed: float = 0.0
    eta: float = 0.0
    filename: str = ""
    status: str = ""


@dataclass
class DownloadTask:
    """Represents a single download task."""
    id: str = ""
    url: str = ""
    title: str = ""
    platform: str = ""
    thumbnail: str = ""
    state: DownloadState = DownloadState.PENDING
    progress: DownloadProgress = field(default_factory=DownloadProgress)
    options: Optional[DownloadOptions] = None
    video_info: Optional[VideoInfo] = None
    error: str = ""
    files: List[str] = field(default_factory=list)
    created_at: float = 0.0
    started_at: float = 0.0
    completed_at: float = 0.0
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]
        if not self.created_at:
            self.created_at = time.time()

    @property
    def duration(self) -> float:
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        elif self.started_at:
            return time.time() - self.started_at
        return 0

    @property
    def is_terminal(self) -> bool:
        return self.state in (DownloadState.COMPLETED, DownloadState.FAILED, DownloadState.CANCELLED)


class DownloadManager:
    """
    Manages download queue with concurrent execution.
    Thread-safe with callback support for UI integration.
    """

    def __init__(
        self,
        max_concurrent: int = 3,
        engine: Optional[DownloadEngine] = None,
    ):
        self._engine = engine or DownloadEngine()
        self._max_concurrent = max_concurrent
        self._tasks: Dict[str, DownloadTask] = {}
        self._queue: Queue = Queue()
        self._active_threads: List[threading.Thread] = []
        self._lock = threading.Lock()
        self._running = True

        # Callbacks
        self._on_progress: Optional[Callable] = None
        self._on_state_change: Optional[Callable] = None
        self._on_complete: Optional[Callable] = None
        self._on_error: Optional[Callable] = None

        # Start worker threads
        self._start_workers()

    def _start_workers(self):
        """Start worker threads for processing downloads."""
        for i in range(self._max_concurrent):
            t = threading.Thread(
                target=self._worker_loop,
                name=f"DownloadWorker-{i}",
                daemon=True,
            )
            t.start()
            self._active_threads.append(t)

    def _worker_loop(self):
        """Worker loop for processing download tasks."""
        while self._running:
            try:
                task = self._queue.get(timeout=1)
                if task is None:
                    break
                self._process_task(task)
                self._queue.task_done()
            except Empty:
                continue
            except Exception as e:
                logger.error(f"Worker error: {e}")

    def _process_task(self, task: DownloadTask):
        """Process a single download task."""
        self._update_state(task, DownloadState.DOWNLOADING)
        task.started_at = time.time()

        try:
            options = task.options or DownloadOptions(url=task.url)
            options.url = task.url

            def progress_callback(progress_data):
                task.progress = DownloadProgress(
                    progress=progress_data.get("progress", 0),
                    downloaded=progress_data.get("downloaded", 0),
                    total=progress_data.get("total", 0),
                    speed=progress_data.get("speed", 0),
                    eta=progress_data.get("eta", 0),
                    filename=progress_data.get("filename", ""),
                    status=progress_data.get("status", ""),
                )
                if progress_data.get("status") == "finished":
                    self._update_state(task, DownloadState.PROCESSING)
                if self._on_progress:
                    self._on_progress(task)

            result = self._engine.download(
                options=options,
                progress_callback=progress_callback,
            )

            if result["success"]:
                task.files = result.get("files", [])
                task.video_info = result.get("info")
                task.progress.progress = 100
                task.completed_at = time.time()
                self._update_state(task, DownloadState.COMPLETED)
                if self._on_complete:
                    self._on_complete(task)
            else:
                error = result.get("error", "Unknown error")
                if task.retry_count < task.max_retries:
                    task.retry_count += 1
                    task.error = f"Retry {task.retry_count}/{task.max_retries}: {error}"
                    logger.info(f"Retrying task {task.id}: {task.error}")
                    time.sleep(2 ** task.retry_count)
                    self._queue.put(task)
                else:
                    task.error = error
                    self._update_state(task, DownloadState.FAILED)
                    if self._on_error:
                        self._on_error(task)

        except Exception as e:
            task.error = str(e)
            self._update_state(task, DownloadState.FAILED)
            if self._on_error:
                self._on_error(task)

    def _update_state(self, task: DownloadTask, state: DownloadState):
        """Update task state and notify callbacks."""
        task.state = state
        if self._on_state_change:
            self._on_state_change(task)

    def add_task(
        self,
        url: str,
        options: Optional[DownloadOptions] = None,
        auto_start: bool = True,
    ) -> DownloadTask:
        """Add a new download task."""
        task = DownloadTask(
            url=url,
            options=options,
            max_retries=options.max_retries if options else 3,
        )

        with self._lock:
            self._tasks[task.id] = task

        if auto_start:
            self.start_task(task.id)

        return task

    def start_task(self, task_id: str):
        """Start or resume a download task."""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                raise ValueError(f"Task {task_id} not found")
            if task.state in (DownloadState.PENDING, DownloadState.PAUSED, DownloadState.QUEUED):
                self._update_state(task, DownloadState.QUEUED)
                self._queue.put(task)

    def cancel_task(self, task_id: str):
        """Cancel a download task."""
        with self._lock:
            task = self._tasks.get(task_id)
            if task and not task.is_terminal:
                self._engine.cancel()
                self._update_state(task, DownloadState.CANCELLED)

    def cancel_all(self):
        """Cancel all active downloads."""
        with self._lock:
            for task in self._tasks.values():
                if not task.is_terminal:
                    self._update_state(task, DownloadState.CANCELLED)
            self._engine.cancel()

    def remove_task(self, task_id: str):
        """Remove a task from the manager."""
        self.cancel_task(task_id)
        with self._lock:
            self._tasks.pop(task_id, None)

    def get_task(self, task_id: str) -> Optional[DownloadTask]:
        """Get a task by ID."""
        with self._lock:
            return self._tasks.get(task_id)

    def get_all_tasks(self) -> List[DownloadTask]:
        """Get all tasks."""
        with self._lock:
            return list(self._tasks.values())

    def get_active_tasks(self) -> List[DownloadTask]:
        """Get currently active tasks."""
        with self._lock:
            return [t for t in self._tasks.values()
                    if t.state in (DownloadState.DOWNLOADING, DownloadState.QUEUED, DownloadState.PROCESSING)]

    def get_completed_tasks(self) -> List[DownloadTask]:
        """Get completed tasks."""
        with self._lock:
            return [t for t in self._tasks.values() if t.state == DownloadState.COMPLETED]

    def clear_completed(self):
        """Remove all completed tasks."""
        with self._lock:
            to_remove = [tid for tid, t in self._tasks.items() if t.is_terminal]
            for tid in to_remove:
                del self._tasks[tid]

    @property
    def on_progress(self):
        return self._on_progress

    @on_progress.setter
    def on_progress(self, callback: Callable):
        self._on_progress = callback

    @property
    def on_state_change(self):
        return self._on_state_change

    @on_state_change.setter
    def on_state_change(self, callback: Callable):
        self._on_state_change = callback

    @property
    def on_complete(self):
        return self._on_complete

    @on_complete.setter
    def on_complete(self, callback: Callable):
        self._on_complete = callback

    @property
    def on_error(self):
        return self._on_error

    @on_error.setter
    def on_error(self, callback: Callable):
        self._on_error = callback

    def shutdown(self):
        """Shutdown the download manager."""
        self._running = False
        self.cancel_all()
        for _ in self._active_threads:
            self._queue.put(None)

    @property
    def active_count(self) -> int:
        return len(self.get_active_tasks())

    @property
    def total_count(self) -> int:
        with self._lock:
            return len(self._tasks)
