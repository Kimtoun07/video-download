"""Tests for batch processing."""

import pytest
from src.core.batch import BatchProcessor, BatchConfig


class TestBatchProcessor:
    """Tests for BatchProcessor."""

    def test_extract_urls(self):
        text = """
        Check out these videos:
        https://youtube.com/watch?v=abc123
        https://vimeo.com/456
        And this one https://bilibili.com/video/BV123
        """
        urls = BatchProcessor.extract_urls(text)
        assert len(urls) == 3
        assert "https://youtube.com/watch?v=abc123" in urls
        assert "https://vimeo.com/456" in urls
        assert "https://bilibili.com/video/BV123" in urls

    def test_extract_urls_empty(self):
        urls = BatchProcessor.extract_urls("no urls here")
        assert len(urls) == 0

    def test_extract_urls_clean(self):
        text = "Visit https://youtube.com/watch?v=abc123."
        urls = BatchProcessor.extract_urls(text)
        assert len(urls) == 1
        assert urls[0] == "https://youtube.com/watch?v=abc123"

    def test_batch_config_defaults(self):
        config = BatchConfig()
        assert config.delay_between == 1.0
        assert config.max_concurrent == 3
        assert config.stop_on_error is False
        assert config.skip_duplicates is True
