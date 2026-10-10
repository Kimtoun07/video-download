"""Tests for the download engine."""

import pytest
from src.core.engine import DownloadEngine, DownloadOptions, VideoInfo


class TestVideoInfo:
    """Tests for VideoInfo dataclass."""

    def test_default_values(self):
        info = VideoInfo()
        assert info.id == ""
        assert info.title == ""
        assert info.duration == 0
        assert info.is_playlist is False

    def test_duration_str_minutes(self):
        info = VideoInfo(duration=125)
        assert info.duration_str == "2:05"

    def test_duration_str_hours(self):
        info = VideoInfo(duration=3661)
        assert info.duration_str == "1:01:01"

    def test_duration_str_unknown(self):
        info = VideoInfo(duration=0)
        assert info.duration_str == "Unknown"

    def test_best_resolution(self):
        info = VideoInfo(formats=[
            {"height": 720},
            {"height": 1080},
            {"height": 480},
        ])
        assert info.best_resolution == "1080p"


class TestDownloadOptions:
    """Tests for DownloadOptions."""

    def test_default_values(self):
        opts = DownloadOptions()
        assert opts.format_id == "best"
        assert opts.video_format == "mp4"
        assert opts.audio_format == "mp3"
        assert opts.max_retries == 3
        assert opts.audio_only is False

    def test_custom_values(self):
        opts = DownloadOptions(
            url="https://example.com",
            output_dir="/tmp",
            resolution="1080",
            audio_only=True,
        )
        assert opts.url == "https://example.com"
        assert opts.output_dir == "/tmp"
        assert opts.resolution == "1080"
        assert opts.audio_only is True
