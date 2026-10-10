"""
Configuration management for GrabVid.
Handles user preferences, download defaults, and persistent settings.
"""

import json
import os
import platform
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Application configuration manager with persistent storage."""

    DEFAULT_CONFIG = {
        "general": {
            "language": "en",
            "theme": "dark",
            "first_run": True,
            "check_updates": True,
            "notifications": True,
        },
        "download": {
            "output_dir": "",  # Will be set dynamically
            "format_preference": "best",
            "video_format": "mp4",
            "audio_format": "mp3",
            "max_resolution": "best",
            "concurrent_downloads": 3,
            "max_retries": 3,
            "retry_delay": 5,
            "rate_limit": "",  # e.g., "5M" for 5MB/s
            "proxy": "",
            "cookies_file": "",
            "embed_subtitles": True,
            "embed_thumbnail": True,
            "embed_metadata": True,
            "write_description": False,
            "auto_resume": True,
        },
        "naming": {
            "template": "%(title)s.%(ext)s",
            "playlist_template": "%(playlist_title)s/%(playlist_index)03d - %(title)s.%(ext)s",
            "sanitize_filenames": True,
            "restrict_to_ascii": False,
            "max_filename_length": 200,
        },
        "batch": {
            "default_delay": 1.0,
            "max_concurrent": 5,
            "auto_detect_episodes": True,
            "sequential_naming": True,
        },
        "advanced": {
            "debug_mode": False,
            "log_level": "INFO",
            "ffmpeg_path": "",
            "custom_headers": {},
            "user_agent": "",
            "geo_bypass": True,
            "geo_bypass_country": "",
            "no_check_certificate": False,
        },
        "gui": {
            "window_width": 1100,
            "window_height": 720,
            "window_x": -1,
            "window_y": -1,
            "maximized": False,
            "sidebar_collapsed": False,
            "show_thumbnails": True,
            "compact_mode": False,
            "accent_color": "#6C5CE7",
        },
    }

    def __init__(self, config_path: Optional[str] = None):
        if config_path:
            self._config_path = Path(config_path)
        else:
            self._config_path = self._get_default_config_path()

        self._config: Dict[str, Any] = {}
        self._load()

    @staticmethod
    def _get_default_config_path() -> Path:
        """Get the default configuration file path based on the OS."""
        system = platform.system()
        if system == "Windows":
            base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        elif system == "Darwin":
            base = Path.home() / "Library" / "Application Support"
        else:
            base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
        return base / "grabvid" / "config.json"

    @staticmethod
    def get_default_download_dir() -> Path:
        """Get the default download directory."""
        home = Path.home()
        downloads = home / "Downloads" / "GrabVid"
        return downloads

    def _load(self):
        """Load configuration from file, creating defaults if needed."""
        self._config = self._deep_copy(self.DEFAULT_CONFIG)

        # Set dynamic defaults
        if not self._config["download"]["output_dir"]:
            self._config["download"]["output_dir"] = str(self.get_default_download_dir())

        if self._config_path.exists():
            try:
                with open(self._config_path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                self._deep_merge(self._config, saved)
            except (json.JSONDecodeError, IOError):
                pass

    def _deep_copy(self, d: Dict) -> Dict:
        """Deep copy a dictionary."""
        result = {}
        for k, v in d.items():
            if isinstance(v, dict):
                result[k] = self._deep_copy(v)
            else:
                result[k] = v
        return result

    def _deep_merge(self, base: Dict, override: Dict):
        """Deep merge override into base."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def save(self):
        """Save configuration to file."""
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._config_path, "w", encoding="utf-8") as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        try:
            return self._config[section][key]
        except KeyError:
            return default

    def set(self, section: str, key: str, value: Any):
        """Set a configuration value."""
        if section not in self._config:
            self._config[section] = {}
        self._config[section][key] = value

    def get_section(self, section: str) -> Dict[str, Any]:
        """Get an entire configuration section."""
        return self._config.get(section, {})

    def reset(self, section: Optional[str] = None):
        """Reset configuration to defaults."""
        if section:
            self._config[section] = self._deep_copy(self.DEFAULT_CONFIG.get(section, {}))
        else:
            self._config = self._deep_copy(self.DEFAULT_CONFIG)
        self.save()

    @property
    def output_dir(self) -> Path:
        return Path(self.get("download", "output_dir"))

    @output_dir.setter
    def output_dir(self, value: str):
        self.set("download", "output_dir", value)

    @property
    def config_path(self) -> Path:
        return self._config_path

    def to_dict(self) -> Dict[str, Any]:
        return self._deep_copy(self._config)
