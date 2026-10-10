"""Tests for configuration."""

import json
import tempfile
import os
import pytest
from src.core.config import Config


class TestConfig:
    """Tests for Config."""

    def test_default_config(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name

        try:
            config = Config(config_path=path)
            assert config.get("download", "max_retries") == 3
            assert config.get("download", "video_format") == "mp4"
            assert config.get("general", "theme") == "dark"
        finally:
            os.unlink(path)

    def test_set_and_get(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name

        try:
            config = Config(config_path=path)
            config.set("download", "max_retries", 5)
            assert config.get("download", "max_retries") == 5
        finally:
            os.unlink(path)

    def test_save_and_load(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name

        try:
            config = Config(config_path=path)
            config.set("download", "max_retries", 7)
            config.save()

            config2 = Config(config_path=path)
            assert config2.get("download", "max_retries") == 7
        finally:
            os.unlink(path)

    def test_reset(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name

        try:
            config = Config(config_path=path)
            config.set("download", "max_retries", 99)
            config.reset()
            assert config.get("download", "max_retries") == 3
        finally:
            os.unlink(path)

    def test_output_dir(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name

        try:
            config = Config(config_path=path)
            assert config.output_dir is not None
            config.output_dir = "/tmp/test"
            assert str(config.output_dir) == "/tmp/test"
        finally:
            os.unlink(path)
