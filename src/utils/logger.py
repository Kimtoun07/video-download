"""Logging utilities for GrabVid."""

import logging
import sys
from pathlib import Path
from typing import Optional


_LOGGERS = {}


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """Get or create a logger with consistent formatting."""
    if name in _LOGGERS:
        return _LOGGERS[name]

    logger = logging.getLogger(name)

    if level is None:
        level = logging.INFO

    logger.setLevel(level)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(level)
        formatter = logging.Formatter(
            "%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s",
            datefmt="%H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    _LOGGERS[name] = logger
    return logger


def setup_file_logging(log_dir: Optional[str] = None):
    """Set up file-based logging."""
    if log_dir is None:
        log_dir = str(Path.home() / ".grabvid" / "logs")

    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(
        log_path / "grabvid.log",
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s",
    )
    file_handler.setFormatter(formatter)

    root = logging.getLogger("src")
    root.addHandler(file_handler)
