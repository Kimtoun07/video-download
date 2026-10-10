"""CLI terminal formatters for GrabVid."""

import os
import sys
from typing import Optional

# ANSI color codes
COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "italic": "\033[3m",
    "underline": "\033[4m",
    "blink": "\033[5m",
    "strikethrough": "\033[9m",
    # Foreground
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    # Bright
    "bright_red": "\033[91m",
    "bright_green": "\033[92m",
    "bright_yellow": "\033[93m",
    "bright_blue": "\033[94m",
    "bright_magenta": "\033[95m",
    "bright_cyan": "\033[96m",
    "bright_white": "\033[97m",
    # Background
    "bg_black": "\033[40m",
    "bg_red": "\033[41m",
    "bg_green": "\033[42m",
    "bg_yellow": "\033[43m",
    "bg_blue": "\033[44m",
    "bg_magenta": "\033[45m",
    "bg_cyan": "\033[46m",
}

# GrabVid brand colors
BRAND = {
    "primary": "bright_magenta",
    "secondary": "bright_cyan",
    "success": "bright_green",
    "warning": "bright_yellow",
    "error": "bright_red",
    "info": "bright_blue",
    "muted": "dim",
}


def supports_color() -> bool:
    """Check if the terminal supports ANSI colors."""
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    if not hasattr(sys.stdout, "isatty"):
        return False
    if not sys.stdout.isatty():
        return False
    return True


_USE_COLOR = supports_color()


def c(color_name: str, text: str) -> str:
    """Apply color to text."""
    if not _USE_COLOR or color_name not in COLORS:
        return text
    return f"{COLORS[color_name]}{text}{COLORS['reset']}"


def brand(text: str) -> str:
    return c(BRAND["primary"], text)


def success(text: str) -> str:
    return c(BRAND["success"], text)


def warning(text: str) -> str:
    return c(BRAND["warning"], text)


def error(text: str) -> str:
    return c(BRAND["error"], text)


def info(text: str) -> str:
    return c(BRAND["info"], text)


def muted(text: str) -> str:
    return c(BRAND["muted"], text)


def bold(text: str) -> str:
    return c("bold", text)


def dim(text: str) -> str:
    return c("dim", text)


def get_terminal_width() -> int:
    """Get terminal width."""
    try:
        return os.get_terminal_size().columns
    except (AttributeError, ValueError, OSError):
        return 80


def header(title: str, char: str = "═") -> str:
    """Create a styled header."""
    width = min(get_terminal_width(), 80)
    line = char * width
    return f"\n{c(BRAND['primary'], line)}\n  {c(BRAND['primary'], '▸')} {bold(brand(title))}\n{c(BRAND['primary'], line)}"


def section(title: str) -> str:
    """Create a section header."""
    return f"\n  {c(BRAND['secondary'], '◆')} {bold(title)}"


def divider(char: str = "─") -> str:
    """Create a divider line."""
    width = min(get_terminal_width(), 80)
    return c("dim", char * width)


def progress_bar(
    progress: float,
    width: int = 40,
    filled_char: str = "█",
    empty_char: str = "░",
    show_percent: bool = True,
) -> str:
    """Create a styled progress bar."""
    filled = int(width * progress / 100)
    empty = width - filled
    bar = c(BRAND["primary"], filled_char * filled) + c("dim", empty_char * empty)

    if show_percent:
        pct = f"{progress:.1f}%"
        if progress >= 100:
            pct = success(pct)
        elif progress > 50:
            pct = c(BRAND["primary"], pct)
        else:
            pct = info(pct)
        return f"{bar} {pct}"
    return bar


def table_row(columns: list, widths: list, padding: int = 2) -> str:
    """Create a formatted table row."""
    parts = []
    for i, (col, w) in enumerate(zip(columns, widths)):
        text = str(col)
        visible_len = len(text.replace(COLORS.get("reset", ""), ""))
        for cname, ccode in COLORS.items():
            text_len = len(text)
            text = text  # Keep colors
        parts.append(f"{'':<{padding}}{text:<{w + len(text) - len(_strip_ansi(text))}}")
    return "".join(parts)


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text."""
    import re
    return re.sub(r'\033\[[0-9;]*m', '', text)


def spinner_frames():
    """Get spinner animation frames."""
    return ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


def logo() -> str:
    """Return the GrabVid ASCII logo."""
    return f"""
{c(BRAND['primary'], '   ╔══════════════════════════════════════╗')}
{c(BRAND['primary'], '   ║')}  {c(BRAND['primary'], bold('🎬 GrabVid'))} {muted('v1.0.0')}                  {c(BRAND['primary'], '║')}
{c(BRAND['primary'], '   ║')}  {c(BRAND['secondary'], 'Universal Video Downloader')}      {c(BRAND['primary'], '║')}
{c(BRAND['primary'], '   ║')}  {muted('1000+ Platforms • All Regions')}     {c(BRAND['primary'], '║')}
{c(BRAND['primary'], '   ╚══════════════════════════════════════╝')}
"""


def status_icon(state: str) -> str:
    """Get a status icon for a download state."""
    icons = {
        "pending": muted("○"),
        "queued": info("◌"),
        "downloading": c(BRAND["primary"], "◉"),
        "processing": warning("⚙"),
        "completed": success("✓"),
        "failed": error("✗"),
        "cancelled": warning("⊘"),
        "paused": warning("⏸"),
    }
    return icons.get(state, muted("?"))


def format_download_info(info: dict) -> str:
    """Format video info for display."""
    lines = []
    if info.get("title"):
        lines.append(f"  {bold('Title:')}    {info['title']}")
    if info.get("platform"):
        lines.append(f"  {bold('Platform:')} {info['platform']}")
    if info.get("duration"):
        lines.append(f"  {bold('Duration:')} {info['duration']}")
    if info.get("uploader"):
        lines.append(f"  {bold('Uploader:')} {info['uploader']}")
    if info.get("resolution"):
        lines.append(f"  {bold('Quality:')}  {info['resolution']}")
    return "\n".join(lines)
