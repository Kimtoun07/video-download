"""
Batch download processing for GrabVid.
Supports multiple URLs, file-based URL lists, and smart queuing.
"""

import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set

from .downloader import DownloadManager, DownloadTask, DownloadState, DownloadProgress
from .engine import DownloadOptions
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class BatchConfig:
    """Configuration for batch download operations."""
    urls: List[str] = field(default_factory=list)
    options: Optional[DownloadOptions] = None
    delay_between: float = 1.0
    max_concurrent: int = 3
    stop_on_error: bool = False
    auto_detect_episodes: bool = True
    skip_duplicates: bool = True
    output_dir: str = ""
    create_subfolder: bool = True
    subfolder_name: str = ""


@dataclass
class BatchResult:
    """Result of a batch download operation."""
    total: int = 0
    completed: int = 0
    failed: int = 0
    cancelled: int = 0
    skipped: int = 0
    tasks: List[DownloadTask] = field(default_factory=list)
    errors: List[Dict] = field(default_factory=list)
    started_at: float = 0
    completed_at: float = 0
    total_size: int = 0

    @property
    def success_rate(self) -> float:
        if self.total == 0:
            return 0
        return (self.completed / self.total) * 100

    @property
    def duration(self) -> float:
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return 0


class BatchProcessor:
    """
    Handles batch download operations with intelligent queuing,
    duplicate detection, and episode management.
    """

    URL_REGEX = re.compile(
        r'https?://[^\s<>"\']+',
        re.IGNORECASE,
    )

    def __init__(self, manager: DownloadManager):
        self._manager = manager
        self._seen_urls: Set[str] = set()
        self._running = False
        self._on_batch_progress: Optional[Callable] = None
        self._on_batch_complete: Optional[Callable] = None

    def process(
        self,
        config: BatchConfig,
        progress_callback: Optional[Callable] = None,
        complete_callback: Optional[Callable] = None,
    ) -> BatchResult:
        """Process a batch of URLs."""
        self._on_batch_progress = progress_callback
        self._on_batch_complete = complete_callback
        self._running = True
        self._seen_urls.clear()

        result = BatchResult(started_at=time.time())
        urls = self._prepare_urls(config.urls, config.skip_duplicates)
        result.total = len(urls)

        if not urls:
            result.completed_at = time.time()
            return result

        logger.info(f"Starting batch download: {result.total} URLs")

        # Create tasks
        for i, url in enumerate(urls):
            if not self._running:
                break

            options = self._build_options(config, url, i)
            task = self._manager.add_task(url, options, auto_start=True)
            task.metadata["batch_index"] = i
            task.metadata["batch_total"] = result.total
            result.tasks.append(task)

            if self._on_batch_progress:
                self._on_batch_progress({
                    "type": "task_added",
                    "index": i + 1,
                    "total": result.total,
                    "url": url,
                    "task_id": task.id,
                })

            # Rate limiting between task submissions
            if config.delay_between > 0 and i < len(urls) - 1:
                time.sleep(config.delay_between)

        # Wait for all tasks to complete
        self._wait_for_tasks(result, config.stop_on_error)

        result.completed_at = time.time()

        if self._on_batch_complete:
            self._on_batch_complete(result)

        return result

    def process_file(
        self,
        filepath: str,
        config: Optional[BatchConfig] = None,
        progress_callback: Optional[Callable] = None,
        complete_callback: Optional[Callable] = None,
    ) -> BatchResult:
        """Process URLs from a text file (one URL per line)."""
        urls = self.load_urls_from_file(filepath)
        cfg = config or BatchConfig()
        cfg.urls = urls
        return self.process(cfg, progress_callback, complete_callback)

    def process_text(
        self,
        text: str,
        config: Optional[BatchConfig] = None,
        progress_callback: Optional[Callable] = None,
        complete_callback: Optional[Callable] = None,
    ) -> BatchResult:
        """Extract and process URLs from text."""
        urls = self.extract_urls(text)
        cfg = config or BatchConfig()
        cfg.urls = urls
        return self.process(cfg, progress_callback, complete_callback)

    def cancel(self):
        """Cancel the batch operation."""
        self._running = False
        self._manager.cancel_all()

    @classmethod
    def extract_urls(cls, text: str) -> List[str]:
        """Extract URLs from arbitrary text."""
        urls = cls.URL_REGEX.findall(text)
        # Clean up URLs
        cleaned = []
        for url in urls:
            url = url.rstrip(".,;:!?)]}")
            if url.startswith("http"):
                cleaned.append(url)
        return cleaned

    @classmethod
    def load_urls_from_file(cls, filepath: str) -> List[str]:
        """Load URLs from a text file."""
        urls = []
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Extract URL from the line (may contain comments)
                    found = cls.extract_urls(line)
                    urls.extend(found)

        return urls

    def _prepare_urls(self, urls: List[str], skip_duplicates: bool) -> List[str]:
        """Prepare and deduplicate URL list."""
        prepared = []
        for url in urls:
            url = url.strip()
            if not url or not url.startswith("http"):
                continue
            if skip_duplicates and url in self._seen_urls:
                continue
            self._seen_urls.add(url)
            prepared.append(url)
        return prepared

    def _build_options(self, config: BatchConfig, url: str, index: int) -> DownloadOptions:
        """Build download options for a specific URL in the batch."""
        if config.options:
            import copy
            options = copy.deepcopy(config.options)
        else:
            options = DownloadOptions()

        options.url = url

        if config.output_dir:
            output_dir = config.output_dir
            if config.create_subfolder and config.subfolder_name:
                output_dir = os.path.join(output_dir, config.subfolder_name)
            options.output_dir = output_dir

        return options

    def _wait_for_tasks(self, result: BatchResult, stop_on_error: bool):
        """Wait for all tasks to complete."""
        while self._running:
            all_done = True
            for task in result.tasks:
                current = self._manager.get_task(task.id)
                if current:
                    if current.state == DownloadState.COMPLETED:
                        if task.state != DownloadState.COMPLETED:
                            result.completed += 1
                            task.state = DownloadState.COMPLETED
                            task.files = current.files
                    elif current.state == DownloadState.FAILED:
                        if task.state not in (DownloadState.FAILED, DownloadState.COMPLETED):
                            result.failed += 1
                            task.state = DownloadState.FAILED
                            task.error = current.error
                            result.errors.append({
                                "url": task.url,
                                "error": current.error,
                            })
                            if stop_on_error:
                                self.cancel()
                                return
                    elif current.state == DownloadState.CANCELLED:
                        if task.state not in (DownloadState.CANCELLED, DownloadState.COMPLETED, DownloadState.FAILED):
                            result.cancelled += 1
                            task.state = DownloadState.CANCELLED
                    else:
                        all_done = False

                    if self._on_batch_progress:
                        self._on_batch_progress({
                            "type": "progress",
                            "completed": result.completed,
                            "failed": result.failed,
                            "total": result.total,
                            "task_id": task.id,
                            "task_progress": current.progress.progress if current.progress else 0,
                        })

            if all_done:
                break

            time.sleep(0.5)

    @property
    def is_running(self) -> bool:
        return self._running
