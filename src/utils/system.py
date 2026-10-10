"""System utilities for GrabVid."""

import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple


def get_system_info() -> dict:
    """Get system information."""
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "os_release": platform.release(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "hostname": platform.node(),
    }


def get_ffmpeg_path() -> Optional[str]:
    """Find ffmpeg binary path."""
    # Check common locations
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return ffmpeg

    # Check platform-specific locations
    system = platform.system()
    if system == "Windows":
        paths = [
            r"C:\ffmpeg\bin\ffmpeg.exe",
            os.path.expanduser(r"~\ffmpeg\bin\ffmpeg.exe"),
        ]
    elif system == "Darwin":
        paths = [
            "/usr/local/bin/ffmpeg",
            "/opt/homebrew/bin/ffmpeg",
        ]
    else:
        paths = [
            "/usr/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            "/snap/bin/ffmpeg",
        ]

    for p in paths:
        if os.path.isfile(p):
            return p
    return None


def get_ffmpeg_version() -> Optional[str]:
    """Get ffmpeg version string."""
    ffmpeg = get_ffmpeg_path()
    if not ffmpeg:
        return None
    try:
        result = subprocess.run(
            [ffmpeg, "-version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        first_line = result.stdout.split("\n")[0]
        return first_line.split("version")[-1].strip().split()[0] if "version" in first_line else None
    except Exception:
        return None


def open_file(filepath: str):
    """Open a file with the default application."""
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.Popen(["open", filepath])
        elif system == "Windows":
            os.startfile(filepath)
        else:
            subprocess.Popen(["xdg-open", filepath])
    except Exception:
        pass


def open_folder(folderpath: str):
    """Open a folder in the file manager."""
    path = Path(folderpath)
    path.mkdir(parents=True, exist_ok=True)
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.Popen(["open", str(path)])
        elif system == "Windows":
            subprocess.Popen(["explorer", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
    except Exception:
        pass


def get_disk_space(path: str = ".") -> Tuple[int, int, int]:
    """Get disk space info: (total, used, free) in bytes."""
    try:
        usage = shutil.disk_usage(path)
        return usage.total, usage.used, usage.free
    except Exception:
        return 0, 0, 0


def get_clipboard_text() -> str:
    """Get text from system clipboard."""
    try:
        import pyperclip
        return pyperclip.paste()
    except ImportError:
        pass

    system = platform.system()
    try:
        if system == "Darwin":
            result = subprocess.run(["pbpaste"], capture_output=True, text=True)
            return result.stdout
        elif system == "Linux":
            for cmd in [["xclip", "-selection", "clipboard", "-o"], ["xsel", "--clipboard", "--output"]]:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        return result.stdout
                except FileNotFoundError:
                    continue
        elif system == "Windows":
            result = subprocess.run(
                ["powershell", "-command", "Get-Clipboard"],
                capture_output=True, text=True,
            )
            return result.stdout.strip()
    except Exception:
        pass
    return ""


def set_clipboard_text(text: str):
    """Set text to system clipboard."""
    try:
        import pyperclip
        pyperclip.copy(text)
        return
    except ImportError:
        pass

    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.run(["pbcopy"], input=text.encode(), check=True)
        elif system == "Linux":
            subprocess.run(
                ["xclip", "-selection", "clipboard"],
                input=text.encode(), check=True,
            )
        elif system == "Windows":
            subprocess.run(
                ["powershell", "-command", f"Set-Clipboard -Value '{text}'"],
                check=True,
            )
    except Exception:
        pass
