"""Tests for the downloader."""

import pytest
from src.core.downloader import DownloadTask, DownloadState, DownloadProgress


class TestDownloadTask:
    """Tests for DownloadTask."""

    def test_default_state(self):
        task = DownloadTask(url="https://example.com")
        assert task.state == DownloadState.PENDING
        assert task.id != ""
        assert task.created_at > 0

    def test_is_terminal(self):
        task = DownloadTask()
        task.state = DownloadState.COMPLETED
        assert task.is_terminal is True

        task.state = DownloadState.DOWNLOADING
        assert task.is_terminal is False

        task.state = DownloadState.FAILED
        assert task.is_terminal is True

    def test_duration(self):
        import time
        task = DownloadTask()
        task.started_at = time.time() - 10
        task.completed_at = time.time()
        assert 9 < task.duration < 12


class TestDownloadProgress:
    """Tests for DownloadProgress."""

    def test_default_values(self):
        p = DownloadProgress()
        assert p.progress == 0
        assert p.speed == 0
        assert p.status == ""
