# 🎬 GrabVid — Universal Video Downloader

<div align="center">

**Download videos from 1000+ platforms worldwide.**

*Premium CLI & GUI • All OS • All Regions • All Formats*

[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Platforms](https://img.shields.io/badge/Platforms-1000+-purple?style=for-the-badge)](#supported-platforms)
[![OS](https://img.shields.io/badge/OS-Linux%20%7C%20macOS%20%7C%20Windows-orange?style=for-the-badge)](#installation)

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🌍 **1000+ Platforms** | YouTube, Bilibili, TikTok, Vimeo, Twitch, and 995+ more |
| 🇨🇳 **Chinese Platforms** | Bilibili, Douyin, Youku, iQiyi, Tencent Video, Weibo, Kuaishou |
| 🖥️ **Cross-Platform** | Native support for Linux, macOS, and Windows |
| 🎨 **Premium GUI** | Modern dark/light theme GUI with beautiful animations |
| ⌨️ **Powerful CLI** | Full-featured terminal interface with colors and progress bars |
| 📥 **Batch Download** | Download multiple videos from a file or text |
| 📺 **Episodes/Playlists** | Smart playlist detection and episode management |
| 🎵 **Audio Extraction** | Extract audio in MP3, FLAC, AAC, OGG, WAV, M4A |
| 📝 **Subtitles** | Auto-download and embed subtitles |
| 🏷️ **Metadata** | Embed thumbnails, metadata, and descriptions |
| ⚡ **Concurrent** | Download multiple videos simultaneously |
| 🔄 **Auto-Retry** | Automatic retry with exponential backoff |
| 🌐 **Proxy Support** | HTTP/SOCKS proxy support |
| 🍪 **Cookies** | Support for authentication via cookies |

---

## 🚀 Quick Start

### One-Line Install

**Linux / macOS:**
```bash
git clone https://github.com/Kimtoun07/video-download.git && cd video-download && bash install.sh
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/Kimtoun07/video-download.git; cd video-download; pip install -e .
```

### Download Your First Video

```bash
# CLI
grabvid https://www.youtube.com/watch?v=dQw4w9WgXcQ

# GUI
grabvid gui
```

---

## 📦 Installation

### Method 1: Clone & Install (Recommended)

```bash
# Clone the repository
git clone https://github.com/Kimtoun07/video-download.git
cd video-download

# Install (CLI only)
pip install -e .

# Or with GUI support
pip install -e ".[gui]"

# Or everything
pip install -e ".[all]"
```

### Method 2: Using Install Scripts

```bash
# Linux / macOS
bash install.sh           # CLI only
bash install.sh --gui     # With GUI
bash install.sh --all     # Everything

# Windows
install.bat               # CLI only
install.bat --gui         # With GUI
install.bat --all         # Everything
```

### Method 3: Make

```bash
make install        # Core only
make install-gui    # With GUI
make install-all    # Everything
```

### Prerequisites

- **Python 3.8+**
- **ffmpeg** (for video processing and format conversion)

Install ffmpeg:
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows (via chocolatey)
choco install ffmpeg

# Fedora
sudo dnf install ffmpeg

# Arch
sudo pacman -S ffmpeg
```

---

## ⌨️ CLI Usage

### Basic Download

```bash
# Download best quality
grabvid download https://www.youtube.com/watch?v=dQw4w9WgXcQ

# Audio only (MP3)
grabvid download https://www.youtube.com/watch?v=dQw4w9WgXcQ --audio-only

# Specific resolution
grabvid download https://www.youtube.com/watch?v=dQw4w9WgXcQ --resolution 1080p

# Custom output directory
grabvid download https://www.youtube.com/watch?v=dQw4w9WgXcQ -o ~/Videos

# With subtitles
grabvid download https://www.youtube.com/watch?v=dQw4w9WgXcQ --subtitles

# Skip confirmation
grabvid download https://www.youtube.com/watch?v=dQw4w9WgXcQ -y
```

### View Video Info

```bash
# Show video details
grabvid info https://www.youtube.com/watch?v=dQw4w9WgXcQ

# JSON output
grabvid info https://www.youtube.com/watch?v=dQw4w9WgXcQ --json
```

### List Available Formats

```bash
grabvid formats https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

### Batch Download

```bash
# From a file (one URL per line)
grabvid batch urls.txt

# From text
grabvid batch "https://youtube.com/watch?v=abc https://vimeo.com/123"

# With options
grabvid batch urls.txt -o ~/Downloads --concurrent 5 --delay 2
```

### Episodes & Playlists

```bash
# Auto-detect and download all episodes
grabvid episodes https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf

# Specific range
grabvid episodes https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf --range 1-10

# List only (no download)
grabvid episodes https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf --list
```

### Supported Platforms

```bash
# List all platforms
grabvid platforms

# Filter by region
grabvid platforms --region china

# Search
grabvid platforms --search youtube
```

### Configuration

```bash
# Show config
grabvid config --show

# Set value
grabvid config --set download.max_retries 5
grabvid config --set download.output_dir /home/user/Videos

# Show config file path
grabvid config --path

# Reset to defaults
grabvid config --reset
```

### CLI Options Reference

| Option | Short | Description |
|--------|-------|-------------|
| `--output` | `-o` | Output directory |
| `--format` | `-f` | Video format (best, worst, etc.) |
| `--resolution` | `-r` | Max resolution (1080, 720, 480, etc.) |
| `--audio-only` | `-a` | Download audio only |
| `--audio-format` | | Audio format (mp3, aac, flac, ogg, wav, m4a) |
| `--subtitles` | | Download subtitles |
| `--no-subtitles` | | Skip subtitles |
| `--thumbnail` | | Embed thumbnail |
| `--metadata` | | Embed metadata |
| `--rate-limit` | | Download speed limit (e.g., 5M, 1000K) |
| `--proxy` | | HTTP/SOCKS proxy |
| `--cookies` | | Cookies file path |
| `--retries` | | Max retry attempts |
| `--playlist-items` | | Playlist items (1-5, 1,3,5) |
| `--yes` | `-y` | Skip confirmation prompt |
| `--quiet` | `-q` | Suppress output |
| `--debug` | | Enable debug mode |

---

## 🖥️ GUI

Launch the GUI with:

```bash
grabvid gui
```

Or directly:
```bash
python -m src.gui
```

### GUI Features

- **🏠 Home** — Paste URL and download with one click
- **📥 Downloads** — Real-time progress tracking for all downloads
- **📋 Batch** — Multi-URL batch downloading
- **📺 Episodes** — Playlist and series detection
- **🌐 Platforms** — Browse all supported platforms
- **⚙️ Settings** — Configure all options visually
- **🎨 Themes** — Beautiful dark theme (light theme available)

---

## 🌍 Supported Platforms

### Global Platforms
| Platform | Domain | Features |
|----------|--------|----------|
| 📺 YouTube | youtube.com | 8K, Playlists, Subtitles |
| 🎬 Vimeo | vimeo.com | 4K, Password protected |
| 🎥 Dailymotion | dailymotion.com | HD |
| 🎮 Twitch | twitch.tv | VODs, Clips |
| 🐦 X (Twitter) | x.com | Videos, GIFs |
| 👤 Facebook | facebook.com | Videos, Reels |
| 📸 Instagram | instagram.com | Reels, Stories [login] |
| 🎵 TikTok | tiktok.com | Videos, No watermark |
| 🤖 Reddit | reddit.com | Videos, GIFs |
| 🎧 SoundCloud | soundcloud.com | Audio, Playlists |
| 📌 Pinterest | pinterest.com | Videos |
| 💼 LinkedIn | linkedin.com | Videos |
| ❤️ Patreon | patreon.com | Videos [login] |
| 📢 Rumble | rumble.com | HD |
| 🆓 Odysee | odysee.com | HD |

### Chinese Platforms 🇨🇳
| Platform | Domain | Features |
|----------|--------|----------|
| 📺 Bilibili (哔哩哔哩) | bilibili.com | 4K, Danmaku, Playlists |
| 🎵 Douyin (抖音) | douyin.com | Short videos |
| 🎬 Youku (优酷) | youku.com | HD, Playlists |
| 🎭 iQiyi (爱奇艺) | iqiyi.com | HD, Playlists |
| 🐧 Tencent Video (腾讯视频) | v.qq.com | HD, Playlists |
| 🥭 Mango TV (芒果TV) | mgtv.com | HD, Playlists |
| 📹 Kuaishou (快手) | kuaishou.com | Short videos |
| 🌐 Weibo (微博) | weibo.com | Videos |
| 🍉 Xigua Video (西瓜视频) | ixigua.com | HD |
| 🅰️ AcFun (A站) | acfun.cn | HD |

### Korean 🇰🇷 / Japanese 🇯🇵 / Other
| Platform | Region | Domain |
|----------|--------|--------|
| 🇰🇷 Naver TV | Korea | tv.naver.com |
| 🇯🇵 Niconico | Japan | nicovideo.jp |
| 🇷🇺 VK | Russia | vk.com |
| 🇷🇺 Rutube | Russia | rutube.ru |
| 🇪🇺 Arte | Europe | arte.tv |
| ⭐ Hotstar | India | hotstar.com |

> **Note:** GrabVid supports 1000+ platforms via yt-dlp. The table above shows featured platforms.
> Run `grabvid platforms` for the complete list.

---

## 🏗️ Project Structure

```
video-download/
├── README.md              # This file
├── LICENSE                # MIT License
├── pyproject.toml         # Python packaging
├── setup.py               # Backward compat installer
├── requirements.txt       # Dependencies
├── Makefile               # Build automation
├── install.sh             # Linux/macOS installer
├── install.bat            # Windows installer
├── .gitignore
│
├── src/                   # Source code
│   ├── __init__.py        # Package init
│   ├── __main__.py        # Entry point
│   │
│   ├── core/              # Core engine
│   │   ├── config.py      # Configuration management
│   │   ├── engine.py      # yt-dlp wrapper engine
│   │   ├── downloader.py  # Download manager & queue
│   │   ├── platforms.py   # Platform detection (1000+)
│   │   ├── batch.py       # Batch processing
│   │   └── episodes.py    # Episode/playlist manager
│   │
│   ├── cli/               # CLI interface
│   │   ├── main.py        # CLI commands (Click)
│   │   └── formatters.py  # Terminal styling (ANSI)
│   │
│   ├── gui/               # GUI application
│   │   ├── app.py         # Main window
│   │   ├── widgets.py     # Custom widgets
│   │   ├── themes.py      # Dark/light themes
│   │   └── dialogs.py     # Settings, batch dialogs
│   │
│   └── utils/             # Utilities
│       ├── logger.py      # Logging
│       ├── network.py     # Network utils
│       └── system.py      # System utilities
│
├── assets/                # Icons and resources
│
└── tests/                 # Test suite
    ├── test_engine.py
    ├── test_platforms.py
    ├── test_downloader.py
    ├── test_batch.py
    └── test_config.py
```

---

## 🛠️ Development

```bash
# Clone
git clone https://github.com/Kimtoun07/video-download.git
cd video-download

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
make test

# Lint
make lint

# Format
make format

# Launch GUI
make run-gui
```

---

## ⚙️ Configuration

GrabVid stores configuration at:
- **Linux:** `~/.config/grabvid/config.json`
- **macOS:** `~/Library/Application Support/grabvid/config.json`
- **Windows:** `%APPDATA%/grabvid/config.json`

### Key Settings

```json
{
  "download": {
    "output_dir": "~/Downloads/GrabVid",
    "max_resolution": "best",
    "video_format": "mp4",
    "audio_format": "mp3",
    "concurrent_downloads": 3,
    "max_retries": 3,
    "embed_subtitles": true,
    "embed_thumbnail": true,
    "embed_metadata": true
  },
  "naming": {
    "template": "%(title)s.%(ext)s",
    "playlist_template": "%(playlist_title)s/%(playlist_index)03d - %(title)s.%(ext)s"
  }
}
```

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Submit a pull request

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** — The most powerful video downloader engine
- **[Click](https://click.palletsprojects.com/)** — Beautiful CLI framework
- **[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)** — Modern GUI toolkit

---

<div align="center">

**Made with ❤️ for the global community**

*Download anything, from anywhere, on any platform.*

</div>
