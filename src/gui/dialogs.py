"""Dialog windows for GrabVid GUI."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Callable, List
from pathlib import Path


class SettingsDialog(tk.Toplevel):
    """Application settings dialog."""

    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self.title("⚙️  GrabVid Settings")
        self.geometry("650x550")
        self.configure(bg="#0D0D12")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._result = None
        self._build_ui()
        self._center()

    def _center(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"+{x}+{y}")

    def _build_ui(self):
        style = {"bg": "#0D0D12", "fg": "#FFFFFF", "font": ("Segoe UI", 11)}
        lbl_style = {"bg": "#0D0D12", "fg": "#A0A0B8", "font": ("Segoe UI", 10)}

        main = tk.Frame(self, bg="#0D0D12", padx=24, pady=16)
        main.pack(fill="both", expand=True)

        # Title
        tk.Label(main, text="⚙️  Settings", bg="#0D0D12", fg="#FFFFFF",
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 16))

        # Notebook
        notebook = ttk.Notebook(main)
        notebook.pack(fill="both", expand=True)

        # ── General Tab ──
        general = tk.Frame(notebook, bg="#141420", padx=16, pady=12)
        notebook.add(general, text="  General  ")

        tk.Label(general, text="Download Directory", **lbl_style).pack(anchor="w", pady=(8, 4))
        dir_frame = tk.Frame(general, bg="#141420")
        dir_frame.pack(fill="x")
        self._dir_var = tk.StringVar(value=self.config.get("download", "output_dir", ""))
        tk.Entry(dir_frame, textvariable=self._dir_var, bg="#16162A", fg="#FFFFFF",
                 font=("Segoe UI", 10), relief="flat", bd=0).pack(side="left", fill="x", expand=True, padx=(0, 8))
        tk.Button(dir_frame, text="Browse", bg="#2A2A42", fg="#FFFFFF", relief="flat",
                  font=("Segoe UI", 9), command=self._browse_dir).pack(side="right")

        tk.Label(general, text="Concurrent Downloads", **lbl_style).pack(anchor="w", pady=(16, 4))
        self._concurrent_var = tk.IntVar(value=self.config.get("download", "concurrent_downloads", 3))
        tk.Spinbox(general, from_=1, to=10, textvariable=self._concurrent_var,
                   bg="#16162A", fg="#FFFFFF", font=("Segoe UI", 10), relief="flat",
                   width=5, bd=0).pack(anchor="w")

        tk.Label(general, text="Max Retries", **lbl_style).pack(anchor="w", pady=(12, 4))
        self._retries_var = tk.IntVar(value=self.config.get("download", "max_retries", 3))
        tk.Spinbox(general, from_=0, to=10, textvariable=self._retries_var,
                   bg="#16162A", fg="#FFFFFF", font=("Segoe UI", 10), relief="flat",
                   width=5, bd=0).pack(anchor="w")

        # ── Quality Tab ──
        quality = tk.Frame(notebook, bg="#141420", padx=16, pady=12)
        notebook.add(quality, text="  Quality  ")

        tk.Label(quality, text="Default Resolution", **lbl_style).pack(anchor="w", pady=(8, 4))
        self._res_var = tk.StringVar(value=self.config.get("download", "max_resolution", "best"))
        res_frame = tk.Frame(quality, bg="#141420")
        res_frame.pack(anchor="w")
        for res in ["best", "4K", "1080p", "720p", "480p", "360p", "worst"]:
            tk.Radiobutton(res_frame, text=res, variable=self._res_var, value=res,
                           bg="#141420", fg="#FFFFFF", selectcolor="#16162A",
                           activebackground="#141420", activeforeground="#FFFFFF",
                           font=("Segoe UI", 10)).pack(side="left", padx=(0, 12))

        tk.Label(quality, text="Video Format", **lbl_style).pack(anchor="w", pady=(16, 4))
        self._vfmt_var = tk.StringVar(value=self.config.get("download", "video_format", "mp4"))
        fmt_frame = tk.Frame(quality, bg="#141420")
        fmt_frame.pack(anchor="w")
        for fmt in ["mp4", "mkv", "webm", "avi"]:
            tk.Radiobutton(fmt_frame, text=fmt.upper(), variable=self._vfmt_var, value=fmt,
                           bg="#141420", fg="#FFFFFF", selectcolor="#16162A",
                           activebackground="#141420", activeforeground="#FFFFFF",
                           font=("Segoe UI", 10)).pack(side="left", padx=(0, 12))

        tk.Label(quality, text="Audio Format", **lbl_style).pack(anchor="w", pady=(16, 4))
        self._afmt_var = tk.StringVar(value=self.config.get("download", "audio_format", "mp3"))
        afmt_frame = tk.Frame(quality, bg="#141420")
        afmt_frame.pack(anchor="w")
        for fmt in ["mp3", "aac", "flac", "ogg", "wav", "m4a"]:
            tk.Radiobutton(afmt_frame, text=fmt.upper(), variable=self._afmt_var, value=fmt,
                           bg="#141420", fg="#FFFFFF", selectcolor="#16162A",
                           activebackground="#141420", activeforeground="#FFFFFF",
                           font=("Segoe UI", 10)).pack(side="left", padx=(0, 12))

        # ── Metadata Tab ──
        metadata = tk.Frame(notebook, bg="#141420", padx=16, pady=12)
        notebook.add(metadata, text="  Metadata  ")

        self._subtitles_var = tk.BooleanVar(value=self.config.get("download", "embed_subtitles", True))
        self._thumbnail_var = tk.BooleanVar(value=self.config.get("download", "embed_thumbnail", True))
        self._meta_var = tk.BooleanVar(value=self.config.get("download", "embed_metadata", True))

        tk.Label(metadata, text="Embed Options", **lbl_style).pack(anchor="w", pady=(8, 4))
        for text, var in [("Subtitles", self._subtitles_var), ("Thumbnail", self._thumbnail_var), ("Metadata", self._meta_var)]:
            tk.Checkbutton(metadata, text=f" Embed {text}", variable=var,
                           bg="#141420", fg="#FFFFFF", selectcolor="#16162A",
                           activebackground="#141420", activeforeground="#FFFFFF",
                           font=("Segoe UI", 10)).pack(anchor="w", pady=4)

        # ── Advanced Tab ──
        advanced = tk.Frame(notebook, bg="#141420", padx=16, pady=12)
        notebook.add(advanced, text="  Advanced  ")

        tk.Label(advanced, text="Rate Limit", **lbl_style).pack(anchor="w", pady=(8, 4))
        self._rate_var = tk.StringVar(value=self.config.get("download", "rate_limit", ""))
        tk.Entry(advanced, textvariable=self._rate_var, bg="#16162A", fg="#FFFFFF",
                 font=("Segoe UI", 10), relief="flat", bd=0, width=20).pack(anchor="w")
        tk.Label(advanced, text="e.g., 5M, 1000K (leave empty for unlimited)",
                 bg="#141420", fg="#606078", font=("Segoe UI", 9)).pack(anchor="w")

        tk.Label(advanced, text="Proxy", **lbl_style).pack(anchor="w", pady=(16, 4))
        self._proxy_var = tk.StringVar(value=self.config.get("download", "proxy", ""))
        tk.Entry(advanced, textvariable=self._proxy_var, bg="#16162A", fg="#FFFFFF",
                 font=("Segoe UI", 10), relief="flat", bd=0, width=40).pack(anchor="w")

        # ── Buttons ──
        btn_frame = tk.Frame(main, bg="#0D0D12")
        btn_frame.pack(fill="x", pady=(16, 0))

        tk.Button(btn_frame, text="Reset to Defaults", bg="#2A2A42", fg="#A0A0B8",
                  font=("Segoe UI", 10), relief="flat", padx=16, pady=6,
                  command=self._reset).pack(side="left")

        tk.Button(btn_frame, text="Cancel", bg="#2A2A42", fg="#FFFFFF",
                  font=("Segoe UI", 10), relief="flat", padx=16, pady=6,
                  command=self.destroy).pack(side="right", padx=(8, 0))

        tk.Button(btn_frame, text="Save", bg="#6C5CE7", fg="#FFFFFF",
                  font=("Segoe UI", 10, "bold"), relief="flat", padx=16, pady=6,
                  command=self._save).pack(side="right")

    def _browse_dir(self):
        d = filedialog.askdirectory(title="Select Download Directory")
        if d:
            self._dir_var.set(d)

    def _save(self):
        self.config.set("download", "output_dir", self._dir_var.get())
        self.config.set("download", "concurrent_downloads", self._concurrent_var.get())
        self.config.set("download", "max_retries", self._retries_var.get())
        self.config.set("download", "max_resolution", self._res_var.get())
        self.config.set("download", "video_format", self._vfmt_var.get())
        self.config.set("download", "audio_format", self._afmt_var.get())
        self.config.set("download", "embed_subtitles", self._subtitles_var.get())
        self.config.set("download", "embed_thumbnail", self._thumbnail_var.get())
        self.config.set("download", "embed_metadata", self._meta_var.get())
        self.config.set("download", "rate_limit", self._rate_var.get())
        self.config.set("download", "proxy", self._proxy_var.get())
        self.config.save()
        self._result = True
        self.destroy()

    def _reset(self):
        self.config.reset()
        self.destroy()


class BatchDialog(tk.Toplevel):
    """Batch download dialog."""

    def __init__(self, parent, config, on_submit: Callable):
        super().__init__(parent)
        self.config = config
        self._on_submit = on_submit
        self.title("📋  Batch Download")
        self.geometry("600x500")
        self.configure(bg="#0D0D12")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        self._build_ui()
        self._center()

    def _center(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"+{x}+{y}")

    def _build_ui(self):
        main = tk.Frame(self, bg="#0D0D12", padx=24, pady=16)
        main.pack(fill="both", expand=True)

        tk.Label(main, text="📋  Batch Download", bg="#0D0D12", fg="#FFFFFF",
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 8))
        tk.Label(main, text="Enter URLs (one per line) or load from file",
                 bg="#0D0D12", fg="#A0A0B8", font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 12))

        # Text area
        text_frame = tk.Frame(main, bg="#2A2A42", padx=1, pady=1)
        text_frame.pack(fill="both", expand=True)
        self._text = tk.Text(text_frame, bg="#16162A", fg="#FFFFFF", insertbackground="#FFFFFF",
                             font=("SF Mono", 10), relief="flat", bd=0, padx=12, pady=12,
                             wrap="word", undo=True)
        scrollbar = tk.Scrollbar(text_frame, command=self._text.yview, bg="#16162A",
                                 troughcolor="#16162A", highlightthickness=0)
        self._text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self._text.pack(fill="both", expand=True)

        # Options
        opts = tk.Frame(main, bg="#0D0D12")
        opts.pack(fill="x", pady=(12, 0))

        tk.Button(opts, text="📂 Load from File", bg="#2A2A42", fg="#FFFFFF",
                  font=("Segoe UI", 10), relief="flat", padx=12, pady=4,
                  command=self._load_file).pack(side="left")

        tk.Button(opts, text="📋 Paste from Clipboard", bg="#2A2A42", fg="#FFFFFF",
                  font=("Segoe UI", 10), relief="flat", padx=12, pady=4,
                  command=self._paste_clipboard).pack(side="left", padx=8)

        tk.Label(opts, textvariable=tk.StringVar(), bg="#0D0D12", fg="#A0A0B8",
                 font=("Segoe UI", 9)).pack(side="right")

        # Buttons
        btn_frame = tk.Frame(main, bg="#0D0D12")
        btn_frame.pack(fill="x", pady=(16, 0))

        tk.Button(btn_frame, text="Cancel", bg="#2A2A42", fg="#FFFFFF",
                  font=("Segoe UI", 10), relief="flat", padx=20, pady=6,
                  command=self.destroy).pack(side="right", padx=(8, 0))

        tk.Button(btn_frame, text="▶  Start Batch Download", bg="#6C5CE7", fg="#FFFFFF",
                  font=("Segoe UI", 10, "bold"), relief="flat", padx=20, pady=6,
                  command=self._submit).pack(side="right")

    def _load_file(self):
        f = filedialog.askopenfilename(
            title="Select URL file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if f:
            with open(f, "r", encoding="utf-8") as fh:
                self._text.delete("1.0", "end")
                self._text.insert("1.0", fh.read())

    def _paste_clipboard(self):
        try:
            text = self.clipboard_get()
            self._text.insert("end", text)
        except Exception:
            pass

    def _submit(self):
        urls_text = self._text.get("1.0", "end").strip()
        if urls_text:
            self._on_submit(urls_text)
            self.destroy()
