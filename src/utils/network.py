"""Network utilities for GrabVid."""

import socket
import urllib.request
from typing import Optional


def check_connection(host: str = "8.8.8.8", port: int = 53, timeout: float = 3.0) -> bool:
    """Check if an internet connection is available."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except (socket.error, OSError):
        return False


def get_public_ip() -> Optional[str]:
    """Get the public IP address."""
    try:
        return urllib.request.urlopen("https://api.ipify.org", timeout=5).read().decode()
    except Exception:
        return None


def is_url_valid(url: str) -> bool:
    """Basic URL validation."""
    from urllib.parse import urlparse
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except Exception:
        return False


def format_size(size_bytes: int) -> str:
    """Format bytes to human-readable size."""
    if size_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    while size >= 1024 and i < len(units) - 1:
        size /= 1024
        i += 1
    return f"{size:.2f} {units[i]}"


def format_speed(speed_bytes: float) -> str:
    """Format speed in bytes/sec to human-readable."""
    if not speed_bytes:
        return "-- B/s"
    return f"{format_size(int(speed_bytes))}/s"


def format_eta(eta_seconds: float) -> str:
    """Format ETA to human-readable."""
    if not eta_seconds:
        return "--:--"
    eta = int(eta_seconds)
    if eta > 3600:
        return f"{eta // 3600}h {(eta % 3600) // 60}m"
    return f"{eta // 60}:{eta % 60:02d}"
