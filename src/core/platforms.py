"""
Platform detection and configuration for GrabVid.
Supports 1000+ video platforms worldwide including Chinese platforms.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from urllib.parse import urlparse


@dataclass
class PlatformInfo:
    """Information about a supported video platform."""
    name: str
    domain: str
    aliases: List[str] = field(default_factory=list)
    region: str = "global"
    requires_login: bool = False
    supports_playlist: bool = True
    supports_subtitles: bool = True
    max_resolution: str = "4K"
    icon: str = "🌐"
    notes: str = ""


class PlatformDetector:
    """
    Detects and provides information about video platforms.
    Supports global and region-specific platforms.
    """

    PLATFORMS: Dict[str, PlatformInfo] = {
        # ═══════════════════════════════════════════
        #  GLOBAL PLATFORMS
        # ═══════════════════════════════════════════
        "youtube": PlatformInfo(
            name="YouTube",
            domain="youtube.com",
            aliases=["youtu.be", "youtube.com", "m.youtube.com", "music.youtube.com"],
            region="global",
            supports_playlist=True,
            supports_subtitles=True,
            max_resolution="8K",
            icon="📺",
        ),
        "vimeo": PlatformInfo(
            name="Vimeo",
            domain="vimeo.com",
            aliases=["vimeo.com", "player.vimeo.com"],
            region="global",
            icon="🎬",
        ),
        "dailymotion": PlatformInfo(
            name="Dailymotion",
            domain="dailymotion.com",
            aliases=["dailymotion.com", "dai.ly"],
            region="global",
            icon="🎥",
        ),
        "twitch": PlatformInfo(
            name="Twitch",
            domain="twitch.tv",
            aliases=["twitch.tv", "clips.twitch.tv"],
            region="global",
            supports_playlist=True,
            icon="🎮",
        ),
        "twitter": PlatformInfo(
            name="X (Twitter)",
            domain="x.com",
            aliases=["twitter.com", "x.com", "mobile.twitter.com"],
            region="global",
            icon="🐦",
        ),
        "facebook": PlatformInfo(
            name="Facebook",
            domain="facebook.com",
            aliases=["facebook.com", "fb.watch", "m.facebook.com"],
            region="global",
            icon="👤",
        ),
        "instagram": PlatformInfo(
            name="Instagram",
            domain="instagram.com",
            aliases=["instagram.com", "www.instagram.com"],
            region="global",
            requires_login=True,
            icon="📸",
            notes="Login may be required for some content",
        ),
        "tiktok": PlatformInfo(
            name="TikTok",
            domain="tiktok.com",
            aliases=["tiktok.com", "vm.tiktok.com", "vt.tiktok.com"],
            region="global",
            icon="🎵",
        ),
        "reddit": PlatformInfo(
            name="Reddit",
            domain="reddit.com",
            aliases=["reddit.com", "v.redd.it", "old.reddit.com"],
            region="global",
            icon="🤖",
        ),
        "soundcloud": PlatformInfo(
            name="SoundCloud",
            domain="soundcloud.com",
            aliases=["soundcloud.com", "m.soundcloud.com"],
            region="global",
            supports_playlist=True,
            icon="🎧",
        ),
        "spotify": PlatformInfo(
            name="Spotify",
            domain="spotify.com",
            aliases=["open.spotify.com"],
            region="global",
            requires_login=True,
            icon="🎶",
            notes="Audio only",
        ),
        "tumblr": PlatformInfo(
            name="Tumblr",
            domain="tumblr.com",
            region="global",
            icon="📝",
        ),
        "pinterest": PlatformInfo(
            name="Pinterest",
            domain="pinterest.com",
            aliases=["pinterest.com", "pin.it"],
            region="global",
            icon="📌",
        ),
        "linkedin": PlatformInfo(
            name="LinkedIn",
            domain="linkedin.com",
            region="global",
            icon="💼",
        ),
        "snapchat": PlatformInfo(
            name="Snapchat",
            domain="snapchat.com",
            aliases=["snapchat.com", "story.snapchat.com"],
            region="global",
            icon="👻",
        ),

        # ═══════════════════════════════════════════
        #  STREAMING PLATFORMS
        # ═══════════════════════════════════════════
        "netflix": PlatformInfo(
            name="Netflix",
            domain="netflix.com",
            region="global",
            requires_login=True,
            icon="🎬",
            notes="DRM protected - limited support",
        ),
        "amazon_prime": PlatformInfo(
            name="Amazon Prime Video",
            domain="amazon.com",
            aliases=["amazon.com", "primevideo.com"],
            region="global",
            requires_login=True,
            icon="📦",
            notes="DRM protected - limited support",
        ),
        "disney_plus": PlatformInfo(
            name="Disney+",
            domain="disneyplus.com",
            region="global",
            requires_login=True,
            icon="🏰",
            notes="DRM protected - limited support",
        ),
        "hulu": PlatformInfo(
            name="Hulu",
            domain="hulu.com",
            region="global",
            requires_login=True,
            icon="📡",
            notes="DRM protected - limited support",
        ),
        "hbo_max": PlatformInfo(
            name="HBO Max",
            domain="max.com",
            aliases=["max.com", "hbomax.com"],
            region="global",
            requires_login=True,
            icon="🎭",
            notes="DRM protected - limited support",
        ),

        # ═══════════════════════════════════════════
        #  CHINESE PLATFORMS
        # ═══════════════════════════════════════════
        "bilibili": PlatformInfo(
            name="Bilibili (哔哩哔哩)",
            domain="bilibili.com",
            aliases=["bilibili.com", "b23.tv", "bili.com"],
            region="china",
            supports_playlist=True,
            supports_subtitles=True,
            max_resolution="4K",
            icon="📺",
            notes="Some content requires login",
        ),
        "youku": PlatformInfo(
            name="Youku (优酷)",
            domain="youku.com",
            aliases=["youku.com", "v.youku.com"],
            region="china",
            supports_playlist=True,
            icon="🎬",
        ),
        "iqiyi": PlatformInfo(
            name="iQiyi (爱奇艺)",
            domain="iqiyi.com",
            aliases=["iqiyi.com", "iq.com"],
            region="china",
            supports_playlist=True,
            icon="🎭",
        ),
        "tencent_video": PlatformInfo(
            name="Tencent Video (腾讯视频)",
            domain="v.qq.com",
            aliases=["v.qq.com", "qq.com"],
            region="china",
            supports_playlist=True,
            icon="🐧",
        ),
        "mango_tv": PlatformInfo(
            name="Mango TV (芒果TV)",
            domain="mgtv.com",
            aliases=["mgtv.com"],
            region="china",
            supports_playlist=True,
            icon="🥭",
        ),
        "douyin": PlatformInfo(
            name="Douyin (抖音)",
            domain="douyin.com",
            aliases=["douyin.com"],
            region="china",
            icon="🎵",
            notes="Chinese version of TikTok",
        ),
        "kuaishou": PlatformInfo(
            name="Kuaishou (快手)",
            domain="kuaishou.com",
            aliases=["kuaishou.com", "gifshow.com"],
            region="china",
            icon="📹",
        ),
        "weibo": PlatformInfo(
            name="Weibo (微博)",
            domain="weibo.com",
            aliases=["weibo.com", "m.weibo.cn"],
            region="china",
            icon="🌐",
        ),
        "xigua_video": PlatformInfo(
            name="Xigua Video (西瓜视频)",
            domain="ixigua.com",
            aliases=["ixigua.com"],
            region="china",
            supports_playlist=True,
            icon="🍉",
        ),
        "acfun": PlatformInfo(
            name="AcFun (A站)",
            domain="acfun.cn",
            aliases=["acfun.cn"],
            region="china",
            supports_playlist=True,
            icon="🅰️",
        ),
        "sohu_video": PlatformInfo(
            name="Sohu Video (搜狐视频)",
            domain="tv.sohu.com",
            aliases=["tv.sohu.com"],
            region="china",
            icon="📺",
        ),
        "letv": PlatformInfo(
            name="Le.com (乐视)",
            domain="le.com",
            aliases=["le.com", "letv.com"],
            region="china",
            icon="📼",
        ),
        "pptv": PlatformInfo(
            name="PPTV (聚力视频)",
            domain="pptv.com",
            region="china",
            icon="📺",
        ),

        # ═══════════════════════════════════════════
        #  KOREAN PLATFORMS
        # ═══════════════════════════════════════════
        "naver": PlatformInfo(
            name="Naver TV",
            domain="tv.naver.com",
            aliases=["tv.naver.com", "naver.com"],
            region="korea",
            icon="🇰🇷",
        ),
        "kakao": PlatformInfo(
            name="Kakao TV",
            domain="tv.kakao.com",
            region="korea",
            icon="💬",
        ),

        # ═══════════════════════════════════════════
        #  JAPANESE PLATFORMS
        # ═══════════════════════════════════════════
        "niconico": PlatformInfo(
            name="Niconico (ニコニコ)",
            domain="nicovideo.jp",
            aliases=["nicovideo.jp", "nico.ms"],
            region="japan",
            requires_login=True,
            supports_playlist=True,
            icon="🇯🇵",
        ),
        "abematv": PlatformInfo(
            name="AbemaTV",
            domain="abema.tv",
            region="japan",
            icon="📺",
        ),

        # ═══════════════════════════════════════════
        #  INDIAN PLATFORMS
        # ═══════════════════════════════════════════
        "hotstar": PlatformInfo(
            name="Disney+ Hotstar",
            domain="hotstar.com",
            region="india",
            requires_login=True,
            icon="⭐",
        ),
        "jiosaavn": PlatformInfo(
            name="JioSaavn",
            domain="jiosaavn.com",
            region="india",
            icon="🎵",
            notes="Audio only",
        ),

        # ═══════════════════════════════════════════
        #  EUROPEAN PLATFORMS
        # ═══════════════════════════════════════════
        "rutube": PlatformInfo(
            name="Rutube",
            domain="rutube.ru",
            region="russia",
            icon="🇷🇺",
        ),
        "vk": PlatformInfo(
            name="VK (ВКонтакте)",
            domain="vk.com",
            aliases=["vk.com", "vkontakte.ru"],
            region="russia",
            icon="🔵",
        ),
        "ok_ru": PlatformInfo(
            name="Odnoklassniki",
            domain="ok.ru",
            region="russia",
            icon="🟠",
        ),
        "arte": PlatformInfo(
            name="Arte",
            domain="arte.tv",
            region="europe",
            icon="🇪🇺",
        ),

        # ═══════════════════════════════════════════
        #  EDUCATIONAL & OTHER PLATFORMS
        # ═══════════════════════════════════════════
        "udemy": PlatformInfo(
            name="Udemy",
            domain="udemy.com",
            region="global",
            requires_login=True,
            supports_playlist=True,
            icon="🎓",
            notes="Login required for purchased courses",
        ),
        "coursera": PlatformInfo(
            name="Coursera",
            domain="coursera.org",
            region="global",
            requires_login=True,
            icon="📚",
        ),
        "ted": PlatformInfo(
            name="TED",
            domain="ted.com",
            region="global",
            supports_subtitles=True,
            icon="💡",
        ),
        "kickstarter": PlatformInfo(
            name="Kickstarter",
            domain="kickstarter.com",
            region="global",
            icon="🚀",
        ),
        "patreon": PlatformInfo(
            name="Patreon",
            domain="patreon.com",
            region="global",
            requires_login=True,
            icon="❤️",
        ),
        "odysee": PlatformInfo(
            name="Odysee",
            domain="odysee.com",
            region="global",
            icon="🆓",
        ),
        "rumble": PlatformInfo(
            name="Rumble",
            domain="rumble.com",
            region="global",
            icon="📢",
        ),
    }

    # URL patterns for fast detection
    URL_PATTERNS = {
        r"youtube\.com|youtu\.be": "youtube",
        r"vimeo\.com": "vimeo",
        r"dailymotion\.com|dai\.ly": "dailymotion",
        r"twitch\.tv": "twitch",
        r"twitter\.com|x\.com": "twitter",
        r"facebook\.com|fb\.watch": "facebook",
        r"instagram\.com": "instagram",
        r"tiktok\.com": "tiktok",
        r"reddit\.com|v\.redd\.it": "reddit",
        r"soundcloud\.com": "soundcloud",
        r"bilibili\.com|b23\.tv": "bilibili",
        r"youku\.com": "youku",
        r"iqiyi\.com|iq\.com": "iqiyi",
        r"v\.qq\.com": "tencent_video",
        r"mgtv\.com": "mango_tv",
        r"douyin\.com": "douyin",
        r"kuaishou\.com|gifshow\.com": "kuaishou",
        r"weibo\.com|weibo\.cn": "weibo",
        r"ixigua\.com": "xigua_video",
        r"acfun\.cn": "acfun",
        r"nicovideo\.jp|nico\.ms": "niconico",
        r"vk\.com": "vk",
        r"ok\.ru": "ok_ru",
        r"rutube\.ru": "rutube",
        r"hotstar\.com": "hotstar",
        r"netflix\.com": "netflix",
        r"amazon\.com.*prime|primevideo\.com": "amazon_prime",
        r"disneyplus\.com": "disney_plus",
        r"hulu\.com": "hulu",
        r"max\.com|hbomax\.com": "hbo_max",
        r"udemy\.com": "udemy",
        r"coursera\.org": "coursera",
        r"ted\.com": "ted",
        r"patreon\.com": "patreon",
        r"rumble\.com": "rumble",
        r"odysee\.com": "odysee",
        r"pinterest\.com|pin\.it": "pinterest",
        r"linkedin\.com": "linkedin",
        r"tumblr\.com": "tumblr",
    }

    @classmethod
    def detect(cls, url: str) -> Optional[PlatformInfo]:
        """Detect the platform from a URL."""
        try:
            parsed = urlparse(url)
            host = parsed.hostname or ""
        except Exception:
            host = ""

        for pattern, platform_key in cls.URL_PATTERNS.items():
            if re.search(pattern, host, re.IGNORECASE):
                return cls.PLATFORMS.get(platform_key)

        return None

    @classmethod
    def get_platform_key(cls, url: str) -> Optional[str]:
        """Get the platform key from a URL."""
        try:
            parsed = urlparse(url)
            host = parsed.hostname or ""
        except Exception:
            return None

        for pattern, platform_key in cls.URL_PATTERNS.items():
            if re.search(pattern, host, re.IGNORECASE):
                return platform_key
        return None

    @classmethod
    def get_all_platforms(cls) -> List[PlatformInfo]:
        """Get all supported platforms."""
        return list(cls.PLATFORMS.values())

    @classmethod
    def get_platforms_by_region(cls, region: str) -> List[PlatformInfo]:
        """Get platforms filtered by region."""
        return [p for p in cls.PLATFORMS.values() if p.region == region]

    @classmethod
    def get_regions(cls) -> List[str]:
        """Get all unique regions."""
        return sorted(set(p.region for p in cls.PLATFORMS.values()))

    @classmethod
    def is_supported(cls, url: str) -> bool:
        """Check if a URL is from a known platform."""
        return cls.detect(url) is not None

    @classmethod
    def search_platforms(cls, query: str) -> List[PlatformInfo]:
        """Search platforms by name or domain."""
        query_lower = query.lower()
        results = []
        for p in cls.PLATFORMS.values():
            if (query_lower in p.name.lower() or
                    query_lower in p.domain.lower() or
                    any(query_lower in a.lower() for a in p.aliases)):
                results.append(p)
        return results
