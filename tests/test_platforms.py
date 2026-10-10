"""Tests for platform detection."""

import pytest
from src.core.platforms import PlatformDetector, PlatformInfo


class TestPlatformDetector:
    """Tests for PlatformDetector."""

    def test_detect_youtube(self):
        info = PlatformDetector.detect("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert info is not None
        assert info.name == "YouTube"

    def test_detect_youtu_be(self):
        info = PlatformDetector.detect("https://youtu.be/dQw4w9WgXcQ")
        assert info is not None
        assert info.name == "YouTube"

    def test_detect_bilibili(self):
        info = PlatformDetector.detect("https://www.bilibili.com/video/BV1xx411c7mD")
        assert info is not None
        assert info.name == "Bilibili (哔哩哔哩)"

    def test_detect_vimeo(self):
        info = PlatformDetector.detect("https://vimeo.com/123456")
        assert info is not None
        assert info.name == "Vimeo"

    def test_detect_tiktok(self):
        info = PlatformDetector.detect("https://www.tiktok.com/@user/video/123")
        assert info is not None
        assert info.name == "TikTok"

    def test_detect_twitch(self):
        info = PlatformDetector.detect("https://www.twitch.tv/videos/123")
        assert info is not None
        assert info.name == "Twitch"

    def test_detect_twitter(self):
        info = PlatformDetector.detect("https://twitter.com/user/status/123")
        assert info is not None
        assert info.name == "X (Twitter)"

    def test_detect_unknown(self):
        info = PlatformDetector.detect("https://example.com/video")
        assert info is None

    def test_detect_invalid_url(self):
        info = PlatformDetector.detect("not a url")
        assert info is None

    def test_get_platform_key(self):
        key = PlatformDetector.get_platform_key("https://www.youtube.com/watch?v=123")
        assert key == "youtube"

    def test_is_supported(self):
        assert PlatformDetector.is_supported("https://www.youtube.com/watch?v=123")
        assert not PlatformDetector.is_supported("https://example.com")

    def test_get_all_platforms(self):
        platforms = PlatformDetector.get_all_platforms()
        assert len(platforms) > 20

    def test_get_platforms_by_region(self):
        china = PlatformDetector.get_platforms_by_region("china")
        assert len(china) > 5
        for p in china:
            assert p.region == "china"

    def test_get_regions(self):
        regions = PlatformDetector.get_regions()
        assert "global" in regions
        assert "china" in regions

    def test_search_platforms(self):
        results = PlatformDetector.search_platforms("youtube")
        assert len(results) >= 1
        assert results[0].name == "YouTube"

    def test_search_chinese(self):
        results = PlatformDetector.search_platforms("bilibili")
        assert len(results) >= 1
