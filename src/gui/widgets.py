"""
Custom widgets for GrabVid GUI.
Premium styled widgets with modern aesthetics.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable


class RoundedFrame(tk.Canvas):
    """A frame with rounded corners."""

    def __init__(self, parent, radius=12, bg="#1A1A2E", **kwargs):
        self.radius = radius
        self.bg_color = bg
        super().__init__(parent, highlightthickness=0, bg=parent.cget("bg") if hasattr(parent, "cget") else bg, **kwargs)
        self._frame = tk.Frame(self, bg=bg)
        self.bind("<Configure>", self._redraw)

    @property
    def inner(self):
        return self._frame

    def _redraw(self, event=None):
        self.delete("bg")
        w, h, r = self.winfo_width(), self.winfo_height(), self.radius
        # Draw rounded rectangle
        points = [
            r, 0, w-r, 0,
            w, 0, w, r,
            w, h-r, w, h,
            w-r, h, r, h,
            0, h, 0, h-r,
            0, r, 0, 0,
        ]
        self.create_polygon(points, fill=self.bg_color, smooth=True, tags="bg")
        self.create_window((w//2, h//2), window=self._frame, tags="bg")


class ModernButton(tk.Canvas):
    """A modern styled button with hover effects."""

    def __init__(
        self,
        parent,
        text="",
        command=None,
        bg="#6C5CE7",
        fg="#FFFFFF",
        hover_bg="#7D6FF0",
        width=120,
        height=38,
        radius=8,
        font=("Segoe UI", 10, "bold"),
        icon="",
        **kwargs
    ):
        self._text = text
        self._command = command
        self._bg = bg
        self._fg = fg
        self._hover_bg = hover_bg
        self._width = width
        self._height = height
        self._radius = radius
        self._font = font
        self._icon = icon
        self._is_hover = False

        super().__init__(
            parent,
            width=width,
            height=height,
            highlightthickness=0,
            bg=parent.cget("bg") if hasattr(parent, "cget") else "#0D0D12",
            **kwargs,
        )

        self._draw()
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _draw(self, bg=None):
        self.delete("all")
        bg = bg or self._bg
        w, h, r = self._width, self._height, self._radius

        # Rounded rectangle
        self.create_rounded_rect(4, 4, w-4, h-4, r, fill=bg, outline="")

        # Text
        label = f"{self._icon} {self._text}" if self._icon else self._text
        self.create_text(w//2, h//2, text=label, fill=self._fg, font=self._font)

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1+r, y1, x2-r, y1,
            x2, y1, x2, y1+r,
            x2, y2-r, x2, y2,
            x2-r, y2, x1+r, y2,
            x1, y2, x1, y2-r,
            x1, y1+r, x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _on_enter(self, event):
        self._is_hover = True
        self._draw(self._hover_bg)

    def _on_leave(self, event):
        self._is_hover = False
        self._draw(self._bg)

    def _on_click(self, event):
        self._draw(self._bg)

    def _on_release(self, event):
        if self._is_hover and self._command:
            self._draw(self._hover_bg)
            self._command()

    def configure(self, **kwargs):
        if "text" in kwargs:
            self._text = kwargs.pop("text")
        if "command" in kwargs:
            self._command = kwargs.pop("command")
        if "bg" in kwargs:
            self._bg = kwargs.pop("bg")
        if "state" in kwargs:
            state = kwargs.pop("state")
            if state == "disabled":
                self._bg = "#404058"
        self._draw()


class ModernEntry(tk.Frame):
    """A modern styled text entry."""

    def __init__(
        self,
        parent,
        placeholder="",
        bg="#16162A",
        fg="#FFFFFF",
        border_color="#2A2A42",
        focus_color="#6C5CE7",
        width=40,
        font=("Segoe UI", 11),
        **kwargs
    ):
        self._bg = bg
        self._border_color = border_color
        self._focus_color = focus_color

        super().__init__(parent, bg=bg, **kwargs)

        self._entry = tk.Entry(
            self,
            bg=bg,
            fg=fg,
            insertbackground=fg,
            font=font,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=border_color,
            highlightcolor=focus_color,
            width=width,
        )

        self._placeholder = placeholder
        self._has_placeholder = True
        self._fg = fg
        self._placeholder_color = "#606078"

        if placeholder:
            self._entry.insert(0, placeholder)
            self._entry.config(fg=self._placeholder_color)

        self._entry.pack(fill="both", expand=True, padx=8, pady=8)
        self._entry.bind("<FocusIn>", self._on_focus_in)
        self._entry.bind("<FocusOut>", self._on_focus_out)

    def _on_focus_in(self, event):
        if self._has_placeholder:
            self._entry.delete(0, "end")
            self._entry.config(fg=self._fg)
            self._has_placeholder = False

    def _on_focus_out(self, event):
        if not self._entry.get():
            if self._placeholder:
                self._entry.insert(0, self._placeholder)
                self._entry.config(fg=self._placeholder_color)
                self._has_placeholder = True

    def get(self):
        text = self._entry.get()
        if self._has_placeholder:
            return ""
        return text

    def insert(self, index, text):
        if self._has_placeholder:
            self._entry.delete(0, "end")
            self._has_placeholder = False
            self._entry.config(fg=self._fg)
        self._entry.insert(index, text)

    def delete(self, first, last=None):
        self._entry.delete(first, last or "end")


class ProgressBar(tk.Canvas):
    """A modern progress bar with animation."""

    def __init__(
        self,
        parent,
        width=300,
        height=8,
        bg="#1C1C2E",
        fill="#6C5CE7",
        radius=4,
        **kwargs
    ):
        self._width = width
        self._height = height
        self._bg = bg
        self._fill = fill
        self._radius = radius
        self._progress = 0

        super().__init__(
            parent,
            width=width,
            height=height,
            highlightthickness=0,
            bg=parent.cget("bg") if hasattr(parent, "cget") else "#0D0D12",
            **kwargs,
        )
        self._draw()

    def _draw(self):
        self.delete("all")
        w, h, r = self._width, self._height, self._radius

        # Background
        self._rounded_rect(0, 0, w, h, r, fill=self._bg)

        # Fill
        fill_w = max(0, int(w * self._progress / 100))
        if fill_w > 0:
            self._rounded_rect(0, 0, fill_w, h, r, fill=self._fill)

    def _rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1+r, y1, x2-r, y1,
            x2, y1, x2, y1+r,
            x2, y2-r, x2, y2,
            x2-r, y2, x1+r, y2,
            x1, y2, x1, y2-r,
            x1, y1+r, x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def set(self, value: float):
        self._progress = max(0, min(100, value))
        self._draw()

    def get(self) -> float:
        return self._progress


class StatusBadge(tk.Canvas):
    """A status indicator badge."""

    def __init__(self, parent, text="", color="#6C5CE7", **kwargs):
        self._text = text
        self._color = color
        super().__init__(parent, height=24, highlightthickness=0,
                        bg=parent.cget("bg") if hasattr(parent, "cget") else "#0D0D12", **kwargs)
        self.bind("<Configure>", self._draw)

    def _draw(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        # Pill shape
        self.create_rounded_rect(0, 0, w, h, h//2, fill=self._color + "30", outline=self._color)
        self.create_text(w//2, h//2, text=self._text, fill=self._color, font=("Segoe UI", 9, "bold"))

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1+r, y1, x2-r, y1,
            x2, y1, x2, y1+r,
            x2, y2-r, x2, y2,
            x2-r, y2, x1+r, y2,
            x1, y2, x1, y2-r,
            x1, y1+r, x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def set_text(self, text):
        self._text = text
        self._draw()

    def set_color(self, color):
        self._color = color
        self._draw()
