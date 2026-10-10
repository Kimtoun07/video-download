"""
GrabVid GUI — Premium Desktop Application
Modern, cross-platform GUI for video downloading.
"""

import os
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Optional, Dict, List

from ..core.config import Config
from ..core.engine import DownloadEngine, DownloadOptions, VideoInfo
from ..core.downloader import DownloadManager, DownloadTask, DownloadState
from ..core.platforms import PlatformDetector
from ..core.batch import BatchProcessor, BatchConfig
from ..core.episodes import EpisodeManager
from ..utils.network import format_size, format_speed, format_eta
from ..utils.system import open_folder, open_file
from .themes import get_theme, DARK_THEME
from .dialogs import SettingsDialog, BatchDialog
from .widgets import ModernEntry, ProgressBar, ModernButton


class GrabVidGUI:
    """Main GrabVid GUI Application."""

    def __init__(self):
        self.config = Config()
        self.theme = get_theme(self.config.get("general", "theme", "dark"))

        try:
            self.engine = DownloadEngine()
        except ImportError:
            self.engine = None

        self.manager = DownloadManager(
            max_concurrent=self.config.get("download", "concurrent_downloads", 3),
            engine=self.engine,
        ) if self.engine else None

        self._task_widgets: Dict[str, dict] = {}
        self._downloading = False

        self._build_window()
        self._build_ui()
        self._setup_callbacks()

    def _build_window(self):
        """Create and configure the main window."""
        self.root = tk.Tk()
        self.root.title("🎬 GrabVid — Universal Video Downloader")
        self.root.geometry(f"{self.config.get('gui', 'window_width', 1100)}x{self.config.get('gui', 'window_height', 720)}")
        self.root.minsize(900, 600)
        self.root.configure(bg=self.theme["bg_primary"])

        # Window icon (cross-platform)
        try:
            icon_path = Path(__file__).parent.parent.parent / "assets" / "icon.png"
            if icon_path.exists():
                icon = tk.PhotoImage(file=str(icon_path))
                self.root.iconphoto(True, icon)
        except Exception:
            pass

        # Dark title bar on Windows
        if sys.platform == "win32":
            try:
                import ctypes
                DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    ctypes.windll.user32.GetParent(self.root.winfo_id()),
                    DWMWA_USE_IMMERSIVE_DARK_MODE,
                    ctypes.byref(ctypes.c_int(1)),
                    ctypes.sizeof(ctypes.c_int),
                )
            except Exception:
                pass

    def _build_ui(self):
        """Build the entire UI."""
        t = self.theme

        # ════════════════════════════════════════════
        #  SIDEBAR
        # ════════════════════════════════════════════
        sidebar = tk.Frame(self.root, bg=t["bg_sidebar"], width=240)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Logo
        logo_frame = tk.Frame(sidebar, bg=t["bg_sidebar"], pady=20)
        logo_frame.pack(fill="x", padx=16)
        tk.Label(logo_frame, text="🎬", font=("Segoe UI", 28), bg=t["bg_sidebar"], fg=t["fg_primary"]).pack(anchor="w")
        tk.Label(logo_frame, text="GrabVid", font=("Segoe UI", 18, "bold"), bg=t["bg_sidebar"], fg=t["fg_primary"]).pack(anchor="w")
        tk.Label(logo_frame, text="Universal Video Downloader", font=("Segoe UI", 9), bg=t["bg_sidebar"], fg=t["fg_muted"]).pack(anchor="w")

        # Separator
        tk.Frame(sidebar, bg=t["border"], height=1).pack(fill="x", padx=16, pady=12)

        # Navigation
        nav_items = [
            ("🏠", "Home", "home"),
            ("📥", "Downloads", "downloads"),
            ("📋", "Batch", "batch"),
            ("📺", "Episodes", "episodes"),
            ("🌐", "Platforms", "platforms"),
        ]

        self._nav_buttons = {}
        self._current_page = "home"

        for icon, text, page in nav_items:
            frame = tk.Frame(sidebar, bg=t["bg_sidebar"])
            frame.pack(fill="x", padx=8, pady=2)

            btn = tk.Label(
                frame, text=f"  {icon}  {text}",
                bg=t["bg_sidebar"], fg=t["fg_secondary"],
                font=("Segoe UI", 11), anchor="w", padx=16, pady=10, cursor="hand2",
            )
            btn.pack(fill="x")
            btn.bind("<Button-1>", lambda e, p=page: self._switch_page(p))
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=t["bg_hover"]))
            btn.bind("<Leave>", lambda e, b=btn, p=page: b.configure(
                bg=t["accent_muted"] if p == self._current_page else t["bg_sidebar"]
            ))
            self._nav_buttons[page] = btn

        # Separator
        tk.Frame(sidebar, bg=t["border"], height=1).pack(fill="x", padx=16, pady=12)

        # Bottom sidebar
        tk.Label(sidebar, text="⚙️  Settings", bg=t["bg_sidebar"], fg=t["fg_secondary"],
                 font=("Segoe UI", 11), anchor="w", padx=24, pady=10, cursor="hand2"
                 ).pack(fill="x", padx=8).bind("<Button-1>", lambda e: self._open_settings())

        tk.Label(sidebar, text=f"v1.0.0", bg=t["bg_sidebar"], fg=t["fg_muted"],
                 font=("Segoe UI", 9), anchor="w", padx=24).pack(side="bottom", pady=16)

        # ════════════════════════════════════════════
        #  MAIN CONTENT AREA
        # ════════════════════════════════════════════
        self._content = tk.Frame(self.root, bg=t["bg_primary"])
        self._content.pack(side="left", fill="both", expand=True)

        # Pages container
        self._pages = {}
        self._build_home_page()
        self._build_downloads_page()
        self._build_batch_page()
        self._build_episodes_page()
        self._build_platforms_page()

        # Show home page
        self._switch_page("home")

    # ════════════════════════════════════════════════
    #  HOME PAGE
    # ════════════════════════════════════════════════
    def _build_home_page(self):
        t = self.theme
        page = tk.Frame(self._content, bg=t["bg_primary"])
        self._pages["home"] = page

        # Header
        header = tk.Frame(page, bg=t["bg_primary"], pady=20)
        header.pack(fill="x", padx=32)

        tk.Label(header, text="Welcome to GrabVid", bg=t["bg_primary"],
                 fg=t["fg_primary"], font=("Segoe UI", 22, "bold")).pack(anchor="w")
        tk.Label(header, text="Download videos from 1000+ platforms worldwide",
                 bg=t["bg_primary"], fg=t["fg_secondary"], font=("Segoe UI", 11)).pack(anchor="w", pady=(4, 0))

        # URL Input Card
        card = tk.Frame(page, bg=t["bg_card"], padx=24, pady=20)
        card.pack(fill="x", padx=32, pady=(0, 16))
        # Border effect
        border = tk.Frame(page, bg=t["border"], height=1)
        border.pack(fill="x", padx=32)

        tk.Label(card, text="Paste video URL", bg=t["bg_card"], fg=t["fg_secondary"],
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 8))

        input_row = tk.Frame(card, bg=t["bg_card"])
        input_row.pack(fill="x")

        self._url_entry = tk.Entry(
            input_row, bg=t["bg_input"], fg=t["fg_primary"],
            insertbackground=t["fg_primary"], font=("Segoe UI", 12),
            relief="flat", bd=0, highlightthickness=1,
            highlightbackground=t["border"], highlightcolor=t["accent"],
        )
        self._url_entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(12, 12))
        self._url_entry.insert(0, "")
        self._url_entry.bind("<FocusIn>", lambda e: self._on_url_focus(True))
        self._url_entry.bind("<FocusOut>", lambda e: self._on_url_focus(False))

        # Paste button
        paste_btn = tk.Label(input_row, text="📋 Paste", bg=t["bg_hover"], fg=t["fg_secondary"],
                             font=("Segoe UI", 10), padx=12, pady=6, cursor="hand2")
        paste_btn.pack(side="left", padx=(0, 8))
        paste_btn.bind("<Button-1>", lambda e: self._paste_url())

        # Download button
        dl_btn = tk.Label(input_row, text="  ▶  Download  ", bg=t["accent"], fg="#FFFFFF",
                          font=("Segoe UI", 11, "bold"), padx=16, pady=6, cursor="hand2")
        dl_btn.pack(side="right")
        dl_btn.bind("<Button-1>", lambda e: self._start_download())

        # Quick options
        opts = tk.Frame(card, bg=t["bg_card"])
        opts.pack(fill="x", pady=(16, 0))

        self._audio_only_var = tk.BooleanVar(value=False)
        tk.Checkbutton(opts, text=" 🎵 Audio Only", variable=self._audio_only_var,
                       bg=t["bg_card"], fg=t["fg_secondary"], selectcolor=t["bg_input"],
                       activebackground=t["bg_card"], activeforeground=t["fg_primary"],
                       font=("Segoe UI", 10)).pack(side="left", padx=(0, 16))

        self._resolution_var = tk.StringVar(value="best")
        res_menu = ttk.Combobox(opts, textvariable=self._resolution_var, state="readonly",
                                values=["best", "4K", "1080p", "720p", "480p", "360p"],
                                width=8, font=("Segoe UI", 10))
        res_menu.pack(side="left", padx=(0, 8))
        tk.Label(opts, text="Quality", bg=t["bg_card"], fg=t["fg_muted"],
                 font=("Segoe UI", 9)).pack(side="left")

        # Output dir
        out_frame = tk.Frame(card, bg=t["bg_card"])
        out_frame.pack(fill="x", pady=(12, 0))
        tk.Label(out_frame, text="📁", bg=t["bg_card"], fg=t["fg_muted"],
                 font=("Segoe UI", 10)).pack(side="left")
        self._output_label = tk.Label(out_frame, text=str(self.config.output_dir),
                                      bg=t["bg_card"], fg=t["fg_muted"],
                                      font=("Segoe UI", 9), anchor="w")
        self._output_label.pack(side="left", padx=(8, 8), fill="x", expand=True)
        tk.Label(out_frame, text="Change", bg=t["bg_card"], fg=t["accent"],
                 font=("Segoe UI", 9, "underline"), cursor="hand2").pack(side="right")
        out_frame.winfo_children()[-1].bind("<Button-1>", lambda e: self._change_output_dir())

        # Video Info Card (initially hidden)
        self._info_card = tk.Frame(page, bg=t["bg_card"], padx=24, pady=20)
        self._info_label = tk.Label(self._info_card, text="", bg=t["bg_card"],
                                     fg=t["fg_primary"], font=("Segoe UI", 11),
                                     justify="left", anchor="w")
        self._info_label.pack(fill="x")

        # Stats cards
        stats = tk.Frame(page, bg=t["bg_primary"])
        stats.pack(fill="x", padx=32, pady=16)

        for i, (icon, title, value) in enumerate([
            ("🌐", "Platforms", "1000+"),
            ("🌍", "Regions", "Global"),
            ("📺", "Formats", "All"),
            ("⚡", "Speed", "Max"),
        ]):
            stat_card = tk.Frame(stats, bg=t["bg_card"], padx=20, pady=16)
            stat_card.pack(side="left", fill="x", expand=True, padx=(0 if i == 0 else 8, 0))
            tk.Label(stat_card, text=icon, font=("Segoe UI", 24), bg=t["bg_card"]).pack()
            tk.Label(stat_card, text=value, font=("Segoe UI", 16, "bold"),
                     bg=t["bg_card"], fg=t["fg_primary"]).pack()
            tk.Label(stat_card, text=title, font=("Segoe UI", 9),
                     bg=t["bg_card"], fg=t["fg_muted"]).pack()

    # ════════════════════════════════════════════════
    #  DOWNLOADS PAGE
    # ════════════════════════════════════════════════
    def _build_downloads_page(self):
        t = self.theme
        page = tk.Frame(self._content, bg=t["bg_primary"])
        self._pages["downloads"] = page

        # Header
        header = tk.Frame(page, bg=t["bg_primary"], pady=20)
        header.pack(fill="x", padx=32)

        tk.Label(header, text="Downloads", bg=t["bg_primary"],
                 fg=t["fg_primary"], font=("Segoe UI", 22, "bold")).pack(side="left")

        # Action buttons
        btn_frame = tk.Frame(header, bg=t["bg_primary"])
        btn_frame.pack(side="right")

        tk.Label(btn_frame, text="🗑 Clear Completed", bg=t["bg_hover"], fg=t["fg_secondary"],
                 font=("Segoe UI", 10), padx=12, pady=6, cursor="hand2"
                 ).pack(side="left", padx=4).bind("<Button-1>", lambda e: self._clear_completed())

        tk.Label(btn_frame, text="📂 Open Folder", bg=t["bg_hover"], fg=t["fg_secondary"],
                 font=("Segoe UI", 10), padx=12, pady=6, cursor="hand2"
                 ).pack(side="left", padx=4).bind("<Button-1>", lambda e: self._open_download_folder())

        # Downloads list
        self._downloads_frame = tk.Frame(page, bg=t["bg_primary"])
        self._downloads_frame.pack(fill="both", expand=True, padx=32, pady=(0, 16))

        # Scrollable canvas
        canvas = tk.Canvas(self._downloads_frame, bg=t["bg_primary"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self._downloads_frame, orient="vertical", command=canvas.yview)
        self._downloads_inner = tk.Frame(canvas, bg=t["bg_primary"])

        self._downloads_inner.bind("<Configure>",
                                    lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self._downloads_inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Empty state
        self._empty_label = tk.Label(
            self._downloads_inner, text="No downloads yet\n\nPaste a URL and click Download to get started",
            bg=t["bg_primary"], fg=t["fg_muted"], font=("Segoe UI", 12), justify="center",
        )
        self._empty_label.pack(pady=60)

    # ════════════════════════════════════════════════
    #  BATCH PAGE
    # ════════════════════════════════════════════════
    def _build_batch_page(self):
        t = self.theme
        page = tk.Frame(self._content, bg=t["bg_primary"])
        self._pages["batch"] = page

        header = tk.Frame(page, bg=t["bg_primary"], pady=20)
        header.pack(fill="x", padx=32)
        tk.Label(header, text="Batch Download", bg=t["bg_primary"],
                 fg=t["fg_primary"], font=("Segoe UI", 22, "bold")).pack(side="left")
        tk.Label(header, text="Download multiple videos at once",
                 bg=t["bg_primary"], fg=t["fg_secondary"], font=("Segoe UI", 11)).pack(anchor="w")

        # URL text area
        text_frame = tk.Frame(page, bg=t["bg_primary"])
        text_frame.pack(fill="both", expand=True, padx=32, pady=(0, 16))

        self._batch_text = tk.Text(
            text_frame, bg=t["bg_input"], fg=t["fg_primary"],
            insertbackground=t["fg_primary"], font=("SF Mono", 10),
            relief="flat", bd=0, padx=16, pady=16, wrap="word",
            highlightthickness=1, highlightbackground=t["border"], highlightcolor=t["accent"],
        )
        self._batch_text.pack(fill="both", expand=True)

        # Insert placeholder
        self._batch_text.insert("1.0", "Paste multiple URLs here, one per line...\n\nhttps://youtube.com/watch?v=...\nhttps://vimeo.com/...\nhttps://bilibili.com/...")
        self._batch_text.configure(fg=t["fg_muted"])
        self._batch_text.bind("<FocusIn>", lambda e: self._batch_focus_in())

        # Buttons
        btn_frame = tk.Frame(page, bg=t["bg_primary"])
        btn_frame.pack(fill="x", padx=32, pady=(0, 16))

        tk.Label(btn_frame, text="📂 Load File", bg=t["bg_hover"], fg=t["fg_secondary"],
                 font=("Segoe UI", 10), padx=12, pady=6, cursor="hand2"
                 ).pack(side="left", padx=(0, 8)).bind("<Button-1>", lambda e: self._load_batch_file())

        tk.Label(btn_frame, text="📋 Paste", bg=t["bg_hover"], fg=t["fg_secondary"],
                 font=("Segoe UI", 10), padx=12, pady=6, cursor="hand2"
                 ).pack(side="left").bind("<Button-1>", lambda e: self._paste_batch())

        tk.Label(btn_frame, text="  ▶  Start Batch Download  ", bg=t["accent"], fg="#FFFFFF",
                 font=("Segoe UI", 11, "bold"), padx=16, pady=6, cursor="hand2"
                 ).pack(side="right").bind("<Button-1>", lambda e: self._start_batch())

    # ════════════════════════════════════════════════
    #  EPISODES PAGE
    # ════════════════════════════════════════════════
    def _build_episodes_page(self):
        t = self.theme
        page = tk.Frame(self._content, bg=t["bg_primary"])
        self._pages["episodes"] = page

        header = tk.Frame(page, bg=t["bg_primary"], pady=20)
        header.pack(fill="x", padx=32)
        tk.Label(header, text="Episodes & Playlists", bg=t["bg_primary"],
                 fg=t["fg_primary"], font=("Segoe UI", 22, "bold")).pack(side="left")

        # Input
        card = tk.Frame(page, bg=t["bg_card"], padx=24, pady=20)
        card.pack(fill="x", padx=32, pady=(0, 16))

        tk.Label(card, text="Playlist or Channel URL", bg=t["bg_card"], fg=t["fg_secondary"],
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 8))

        input_row = tk.Frame(card, bg=t["bg_card"])
        input_row.pack(fill="x")

        self._ep_url_entry = tk.Entry(
            input_row, bg=t["bg_input"], fg=t["fg_primary"],
            insertbackground=t["fg_primary"], font=("Segoe UI", 12),
            relief="flat", bd=0, highlightthickness=1,
            highlightbackground=t["border"], highlightcolor=t["accent"],
        )
        self._ep_url_entry.pack(side="left", fill="x", expand=True, ipady=10, padx=12)

        tk.Label(input_row, text="  🔍 Detect  ", bg=t["accent"], fg="#FFFFFF",
                 font=("Segoe UI", 11, "bold"), padx=16, pady=6, cursor="hand2"
                 ).pack(side="right").bind("<Button-1>", lambda e: self._detect_episodes())

        # Episodes list
        self._episodes_frame = tk.Frame(page, bg=t["bg_primary"])
        self._episodes_frame.pack(fill="both", expand=True, padx=32, pady=(0, 16))

        self._episodes_text = tk.Text(
            self._episodes_frame, bg=t["bg_input"], fg=t["fg_primary"],
            font=("SF Mono", 10), relief="flat", bd=0, padx=16, pady=16,
            highlightthickness=1, highlightbackground=t["border"],
        )
        self._episodes_text.pack(fill="both", expand=True)

    # ════════════════════════════════════════════════
    #  PLATFORMS PAGE
    # ════════════════════════════════════════════════
    def _build_platforms_page(self):
        t = self.theme
        page = tk.Frame(self._content, bg=t["bg_primary"])
        self._pages["platforms"] = page

        header = tk.Frame(page, bg=t["bg_primary"], pady=20)
        header.pack(fill="x", padx=32)
        tk.Label(header, text="Supported Platforms", bg=t["bg_primary"],
                 fg=t["fg_primary"], font=("Segoe UI", 22, "bold")).pack(side="left")

        # Search
        search_frame = tk.Frame(page, bg=t["bg_primary"])
        search_frame.pack(fill="x", padx=32, pady=(0, 12))
        self._platform_search = tk.Entry(
            search_frame, bg=t["bg_input"], fg=t["fg_primary"],
            insertbackground=t["fg_primary"], font=("Segoe UI", 11),
            relief="flat", bd=0, highlightthickness=1,
            highlightbackground=t["border"], highlightcolor=t["accent"],
        )
        self._platform_search.pack(fill="x", ipady=8, padx=12)
        self._platform_search.bind("<KeyRelease>", lambda e: self._filter_platforms())

        # Platforms grid
        canvas = tk.Canvas(page, bg=t["bg_primary"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(page, orient="vertical", command=canvas.yview)
        self._platforms_inner = tk.Frame(canvas, bg=t["bg_primary"])

        self._platforms_inner.bind("<Configure>",
                                    lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self._platforms_inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=32)
        scrollbar.pack(side="right", fill="y")

        self._populate_platforms()

    def _populate_platforms(self, filter_text=""):
        t = self.theme
        for widget in self._platforms_inner.winfo_children():
            widget.destroy()

        platforms = PlatformDetector.get_all_platforms()
        if filter_text:
            platforms = PlatformDetector.search_platforms(filter_text)

        # Group by region
        regions = {}
        for p in platforms:
            regions.setdefault(p.region, []).append(p)

        for region_name, region_platforms in sorted(regions.items()):
            # Region header
            tk.Label(self._platforms_inner, text=f"  {region_name.upper()}",
                     bg=t["bg_primary"], fg=t["accent"],
                     font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=16, pady=(16, 4))

            # Platform cards in a grid
            grid = tk.Frame(self._platforms_inner, bg=t["bg_primary"])
            grid.pack(fill="x", padx=16)

            for i, p in enumerate(region_platforms):
                card = tk.Frame(grid, bg=t["bg_card"], padx=12, pady=8)
                card.pack(side="left", fill="x", expand=True, padx=4, pady=4)

                login_badge = " 🔒" if p.requires_login else ""
                tk.Label(card, text=f"{p.icon} {p.name}{login_badge}",
                         bg=t["bg_card"], fg=t["fg_primary"],
                         font=("Segoe UI", 10, "bold"), anchor="w").pack(anchor="w")
                tk.Label(card, text=p.domain, bg=t["bg_card"], fg=t["fg_muted"],
                         font=("Segoe UI", 9), anchor="w").pack(anchor="w")

    def _filter_platforms(self):
        query = self._platform_search.get()
        self._populate_platforms(query)

    # ════════════════════════════════════════════════
    #  NAVIGATION & ACTIONS
    # ════════════════════════════════════════════════
    def _switch_page(self, page_name: str):
        t = self.theme
        for name, page in self._pages.items():
            page.pack_forget()

        self._pages[page_name].pack(fill="both", expand=True)
        self._current_page = page_name

        # Update nav button styles
        for name, btn in self._nav_buttons.items():
            if name == page_name:
                btn.configure(bg=t["accent_muted"], fg=t["accent"])
            else:
                btn.configure(bg=t["bg_sidebar"], fg=t["fg_secondary"])

    def _setup_callbacks(self):
        if self.manager:
            self.manager.on_progress = self._on_download_progress
            self.manager.on_state_change = self._on_state_change
            self.manager.on_complete = self._on_download_complete
            self.manager.on_error = self._on_download_error

    def _on_url_focus(self, focused):
        if focused:
            from ..utils.system import get_clipboard_text
            clip = get_clipboard_text()
            if clip and clip.startswith("http"):
                pass  # Could auto-paste

    def _paste_url(self):
        try:
            text = self.root.clipboard_get()
            if text:
                self._url_entry.delete(0, "end")
                self._url_entry.insert(0, text.strip())
        except Exception:
            pass

    def _start_download(self):
        url = self._url_entry.get().strip()
        if not url:
            messagebox.showwarning("GrabVid", "Please enter a URL.")
            return
        if not url.startswith("http"):
            messagebox.showwarning("GrabVid", "Please enter a valid URL starting with http(s)://")
            return

        if not self.engine:
            messagebox.showerror("GrabVid", "yt-dlp is not installed.\nInstall it with: pip install yt-dlp")
            return

        options = DownloadOptions(
            url=url,
            output_dir=str(self.config.output_dir),
            resolution=self._resolution_var.get(),
            audio_only=self._audio_only_var.get(),
            audio_format=self.config.get("download", "audio_format", "mp3"),
            video_format=self.config.get("download", "video_format", "mp4"),
            write_subtitles=self.config.get("download", "embed_subtitles", True),
            embed_thumbnail=self.config.get("download", "embed_thumbnail", True),
            embed_metadata=self.config.get("download", "embed_metadata", True),
        )

        Path(options.output_dir).mkdir(parents=True, exist_ok=True)

        # Detect platform
        platform_info = PlatformDetector.detect(url)

        task = self.manager.add_task(url, options, auto_start=True)
        task.title = "Extracting info..."
        task.platform = platform_info.name if platform_info else "Unknown"

        # Add to downloads view
        self._add_task_widget(task)
        self._switch_page("downloads")

        # Update info in background
        threading.Thread(target=self._update_task_info, args=(task,), daemon=True).start()

    def _update_task_info(self, task):
        try:
            info = self.engine.extract_info(task.url)
            if info:
                task.title = info.title
                task.platform = info.platform
                task.thumbnail = info.thumbnail
                self.root.after(0, self._refresh_task_widget, task)
        except Exception:
            pass

    def _add_task_widget(self, task: DownloadTask):
        t = self.theme

        if self._empty_label.winfo_exists():
            self._empty_label.pack_forget()

        card = tk.Frame(self._downloads_inner, bg=t["bg_card"], padx=16, pady=12)
        card.pack(fill="x", pady=4)

        # Top row
        top = tk.Frame(card, bg=t["bg_card"])
        top.pack(fill="x")

        title_label = tk.Label(top, text=task.title or task.url[:60],
                                bg=t["bg_card"], fg=t["fg_primary"],
                                font=("Segoe UI", 11, "bold"), anchor="w")
        title_label.pack(side="left", fill="x", expand=True)

        platform_label = tk.Label(top, text=task.platform,
                                   bg=t["bg_card"], fg=t["fg_muted"],
                                   font=("Segoe UI", 9))
        platform_label.pack(side="right")

        # Progress row
        prog_frame = tk.Frame(card, bg=t["bg_card"])
        prog_frame.pack(fill="x", pady=(8, 0))

        progress_bar = ProgressBar(prog_frame, width=500, height=6,
                                    bg=t["progress_bg"], fill=t["progress_fill"])
        progress_bar.pack(side="left", fill="x", expand=True)

        pct_label = tk.Label(prog_frame, text="0.0%", bg=t["bg_card"],
                              fg=t["accent"], font=("Segoe UI", 10, "bold"))
        pct_label.pack(side="right", padx=(12, 0))

        # Info row
        info_frame = tk.Frame(card, bg=t["bg_card"])
        info_frame.pack(fill="x", pady=(4, 0))

        status_label = tk.Label(info_frame, text="⏳ Queued",
                                 bg=t["bg_card"], fg=t["fg_secondary"],
                                 font=("Segoe UI", 9))
        status_label.pack(side="left")

        speed_label = tk.Label(info_frame, text="",
                                bg=t["bg_card"], fg=t["fg_muted"],
                                font=("Segoe UI", 9))
        speed_label.pack(side="right")

        size_label = tk.Label(info_frame, text="",
                               bg=t["bg_card"], fg=t["fg_muted"],
                               font=("Segoe UI", 9))
        size_label.pack(side="right", padx=(0, 12))

        # Cancel button
        cancel_label = tk.Label(info_frame, text="✕ Cancel",
                                 bg=t["bg_card"], fg=t["error"],
                                 font=("Segoe UI", 9), cursor="hand2")
        cancel_label.pack(side="right", padx=(0, 12))
        cancel_label.bind("<Button-1>", lambda e, tid=task.id: self._cancel_task(tid))

        self._task_widgets[task.id] = {
            "card": card,
            "title": title_label,
            "platform": platform_label,
            "progress": progress_bar,
            "pct": pct_label,
            "status": status_label,
            "speed": speed_label,
            "size": size_label,
            "cancel": cancel_label,
        }

    def _refresh_task_widget(self, task: DownloadTask):
        widgets = self._task_widgets.get(task.id)
        if not widgets:
            return
        widgets["title"].configure(text=task.title or task.url[:60])
        widgets["platform"].configure(text=task.platform)

    def _on_download_progress(self, task: DownloadTask):
        def update():
            widgets = self._task_widgets.get(task.id)
            if not widgets:
                return

            p = task.progress
            widgets["progress"].set(p.progress)
            widgets["pct"].configure(text=f"{p.progress:.1f}%")
            widgets["speed"].configure(text=format_speed(p.speed))
            widgets["size"].configure(text=f"{format_size(p.downloaded)}/{format_size(p.total)}")
            widgets["status"].configure(text="⬇️ Downloading")

        self.root.after(0, update)

    def _on_state_change(self, task: DownloadTask):
        def update():
            widgets = self._task_widgets.get(task.id)
            if not widgets:
                return

            state_colors = {
                "queued": ("⏳ Queued", self.theme["fg_secondary"]),
                "downloading": ("⬇️ Downloading", self.theme["accent"]),
                "processing": ("⚙️ Processing", self.theme["warning"]),
                "completed": ("✓ Completed", self.theme["success"]),
                "failed": ("✗ Failed", self.theme["error"]),
                "cancelled": ("⊘ Cancelled", self.theme["warning"]),
            }

            text, color = state_colors.get(task.state.value, ("Unknown", self.theme["fg_muted"]))
            widgets["status"].configure(text=text, fg=color)

            if task.is_terminal:
                widgets["cancel"].configure(text="")
                widgets["progress"].set(100 if task.state == DownloadState.COMPLETED else 0)

        self.root.after(0, update)

    def _on_download_complete(self, task: DownloadTask):
        def update():
            widgets = self._task_widgets.get(task.id)
            if widgets:
                widgets["progress"].set(100)
                widgets["pct"].configure(text="100%", fg=self.theme["success"])
                widgets["status"].configure(text="✓ Completed", fg=self.theme["success"])
                widgets["cancel"].configure(text="📂 Open", fg=self.theme["accent"])
                if task.files:
                    widgets["cancel"].bind("<Button-1>",
                                           lambda e, f=task.files[0]: open_file(f))

        self.root.after(0, update)

    def _on_download_error(self, task: DownloadTask):
        def update():
            widgets = self._task_widgets.get(task.id)
            if widgets:
                widgets["status"].configure(text=f"✗ {task.error[:40]}", fg=self.theme["error"])

        self.root.after(0, update)

    def _cancel_task(self, task_id):
        if self.manager:
            self.manager.cancel_task(task_id)

    def _clear_completed(self):
        if self.manager:
            self.manager.clear_completed()
        for tid, widgets in list(self._task_widgets.items()):
            task = self.manager.get_task(tid) if self.manager else None
            if task and task.is_terminal:
                widgets["card"].destroy()
                del self._task_widgets[tid]

        if not self._task_widgets:
            self._empty_label.pack(pady=60)

    def _open_download_folder(self):
        open_folder(str(self.config.output_dir))

    def _change_output_dir(self):
        d = filedialog.askdirectory(title="Select Download Directory")
        if d:
            self.config.output_dir = d
            self.config.save()
            self._output_label.configure(text=d)

    def _load_batch_file(self):
        f = filedialog.askopenfilename(
            title="Select URL file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if f:
            with open(f, "r", encoding="utf-8") as fh:
                self._batch_text.delete("1.0", "end")
                self._batch_text.insert("1.0", fh.read())
                self._batch_text.configure(fg=self.theme["fg_primary"])

    def _paste_batch(self):
        try:
            text = self.root.clipboard_get()
            if text:
                self._batch_text.insert("end", "\n" + text)
                self._batch_text.configure(fg=self.theme["fg_primary"])
        except Exception:
            pass

    def _batch_focus_in(self):
        if self._batch_text.cget("fg") == self.theme["fg_muted"]:
            self._batch_text.delete("1.0", "end")
            self._batch_text.configure(fg=self.theme["fg_primary"])

    def _start_batch(self):
        text = self._batch_text.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("GrabVid", "Please enter URLs.")
            return

        urls = BatchProcessor.extract_urls(text)
        if not urls:
            messagebox.showwarning("GrabVid", "No valid URLs found.")
            return

        if not self.engine:
            messagebox.showerror("GrabVid", "yt-dlp is not installed.")
            return

        self._switch_page("downloads")

        for url in urls:
            options = DownloadOptions(
                url=url,
                output_dir=str(self.config.output_dir),
                resolution=self.config.get("download", "max_resolution", "best"),
            )
            task = self.manager.add_task(url, options, auto_start=True)
            platform_info = PlatformDetector.detect(url)
            task.platform = platform_info.name if platform_info else "Unknown"
            task.title = url[:60]
            self._add_task_widget(task)
            threading.Thread(target=self._update_task_info, args=(task,), daemon=True).start()

    def _detect_episodes(self):
        url = self._ep_url_entry.get().strip()
        if not url:
            messagebox.showwarning("GrabVid", "Please enter a URL.")
            return

        if not self.engine:
            messagebox.showerror("GrabVid", "yt-dlp is not installed.")
            return

        self._episodes_text.delete("1.0", "end")
        self._episodes_text.insert("1.0", "🔍 Detecting episodes...\n")

        def detect():
            try:
                ep_manager = EpisodeManager(engine=self.engine, manager=self.manager)
                preview = ep_manager.preview_episodes(url)
                self.root.after(0, lambda: self._episodes_text.delete("1.0", "end"))
                self.root.after(0, lambda: self._episodes_text.insert("1.0", preview))
            except Exception as e:
                self.root.after(0, lambda: self._episodes_text.insert("end", f"\n✗ Error: {e}"))

        threading.Thread(target=detect, daemon=True).start()

    def _open_settings(self):
        SettingsDialog(self.root, self.config)

    def run(self):
        """Start the GUI event loop."""
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _on_close(self):
        # Save window state
        self.config.set("gui", "window_width", self.root.winfo_width())
        self.config.set("gui", "window_height", self.root.winfo_height())
        self.config.save()

        if self.manager:
            self.manager.shutdown()

        self.root.destroy()
