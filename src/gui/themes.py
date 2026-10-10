"""
GrabVid GUI Theme System.
Modern dark/light themes with accent color support.
"""

# ═══════════════════════════════════════════════════════════
#  DARK THEME (Default — Premium look)
# ═══════════════════════════════════════════════════════════
DARK_THEME = {
    "name": "dark",
    "bg_primary": "#0D0D12",
    "bg_secondary": "#141420",
    "bg_tertiary": "#1C1C2E",
    "bg_card": "#1A1A2E",
    "bg_hover": "#252540",
    "bg_active": "#2D2D4A",
    "bg_input": "#16162A",
    "bg_sidebar": "#0F0F1A",
    "fg_primary": "#FFFFFF",
    "fg_secondary": "#A0A0B8",
    "fg_muted": "#606078",
    "fg_disabled": "#404058",
    "accent": "#6C5CE7",
    "accent_hover": "#7D6FF0",
    "accent_active": "#5A4BD6",
    "accent_muted": "#6C5CE720",
    "success": "#00D68F",
    "success_muted": "#00D68F20",
    "warning": "#FFB800",
    "warning_muted": "#FFB80020",
    "error": "#FF3D71",
    "error_muted": "#FF3D7120",
    "info": "#0095FF",
    "info_muted": "#0095FF20",
    "border": "#2A2A42",
    "border_light": "#1E1E36",
    "shadow": "#00000040",
    "scrollbar": "#2A2A42",
    "scrollbar_hover": "#3A3A52",
    "progress_bg": "#1C1C2E",
    "progress_fill": "#6C5CE7",
    "font_family": "SF Pro Display",
    "font_fallback": "Segoe UI",
    "font_mono": "SF Mono",
    "radius_sm": 6,
    "radius_md": 10,
    "radius_lg": 16,
    "radius_xl": 24,
}

# ═══════════════════════════════════════════════════════════
#  LIGHT THEME
# ═══════════════════════════════════════════════════════════
LIGHT_THEME = {
    "name": "light",
    "bg_primary": "#F8F9FC",
    "bg_secondary": "#FFFFFF",
    "bg_tertiary": "#F0F1F5",
    "bg_card": "#FFFFFF",
    "bg_hover": "#EDEEF5",
    "bg_active": "#E5E6F0",
    "bg_input": "#FFFFFF",
    "bg_sidebar": "#F0F1F5",
    "fg_primary": "#1A1A2E",
    "fg_secondary": "#606078",
    "fg_muted": "#A0A0B8",
    "fg_disabled": "#C0C0D0",
    "accent": "#6C5CE7",
    "accent_hover": "#5A4BD6",
    "accent_active": "#4A3BC6",
    "accent_muted": "#6C5CE715",
    "success": "#00B377",
    "success_muted": "#00B37715",
    "warning": "#E6A600",
    "warning_muted": "#E6A60015",
    "error": "#E6364F",
    "error_muted": "#E6364F15",
    "info": "#0085E6",
    "info_muted": "#0085E615",
    "border": "#E0E1EA",
    "border_light": "#EAEBF2",
    "shadow": "#00000010",
    "scrollbar": "#D0D1E0",
    "scrollbar_hover": "#B0B1C0",
    "progress_bg": "#E0E1EA",
    "progress_fill": "#6C5CE7",
    "font_family": "SF Pro Display",
    "font_fallback": "Segoe UI",
    "font_mono": "SF Mono",
    "radius_sm": 6,
    "radius_md": 10,
    "radius_lg": 16,
    "radius_xl": 24,
}

# ═══════════════════════════════════════════════════════════
#  ACCENT COLORS
# ═══════════════════════════════════════════════════════════
ACCENT_COLORS = {
    "purple": {"primary": "#6C5CE7", "hover": "#7D6FF0", "active": "#5A4BD6"},
    "blue": {"primary": "#0984E3", "hover": "#2E9BEE", "active": "#0770C0"},
    "teal": {"primary": "#00B894", "hover": "#1AC9A5", "active": "#009A7B"},
    "pink": {"primary": "#E84393", "hover": "#ED5AA3", "active": "#D12F7F"},
    "orange": {"primary": "#E17055", "hover": "#E88570", "active": "#D05B40"},
    "red": {"primary": "#FF3D71", "hover": "#FF5A87", "active": "#E62D5E"},
    "green": {"primary": "#00D68F", "hover": "#1AE0A0", "active": "#00B877"},
}


def get_theme(name: str = "dark") -> dict:
    """Get theme by name."""
    if name == "light":
        return LIGHT_THEME
    return DARK_THEME


def apply_accent(theme: dict, accent_name: str) -> dict:
    """Apply an accent color to a theme."""
    theme = theme.copy()
    accent = ACCENT_COLORS.get(accent_name, ACCENT_COLORS["purple"])
    theme["accent"] = accent["primary"]
    theme["accent_hover"] = accent["hover"]
    theme["accent_active"] = accent["active"]
    return theme
