"""
Download engine for GrabVid.
Core wrapper around yt-dlp with enhanced features.
"""

import os
import re
import json
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class VideoInfo:
    """Metadata about a video."""
    id: str = ""
    title: str = ""
    description: str = ""
    duration: float = 0.0
    thumbnail: str = ""
    uploader: str = ""
    upload_date: str = ""
    view_count: int = 0
    like_count: int = 0
    url: str = ""
    webpage_url: str = ""
    platform: str = ""
    formats: List[Dict[str, Any]] = field(default_factory=list)
    subtitles: List[str] = field(default_factory=list)
    is_playlist: bool = False
    playlist_count: int = 0
    playlist_title: str = ""
    entries: List["VideoInfo"] = field(default_factory=list)
    raw_info: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration_str(self) -> str:
        if not self.duration:
            return "Unknown"
        hours = int(self.duration // 3600)
        minutes = int((self.duration % 3600) // 60)
        seconds = int(self.duration % 60)
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"

    @property
    def best_resolution(self) -> str:
        best = "Unknown"
        for fmt in self.formats:
            h = fmt.get("height")
            if h and (best == "Unknown" or h > int(re.search(r"\d+", best).group() if re.search(r"\d+", best) else "0")):
                best = f"{h}p"
        return best


@dataclass
class DownloadOptions:
    """Options for a download operation."""
    url: str = ""
    output_dir: str = ""
    format_id: str = "best"
    video_format: str = "mp4"
    audio_format: str = "mp3"
    resolution: str = "best"
    write_subtitles: bool = True
    embed_thumbnail: bool = True
    embed_metadata: bool = True
    write_description: bool = False
    rate_limit: str = ""
    proxy: str = ""
    cookies_file: str = ""
    playlist_start: int = 1
    playlist_end: Optional[int] = None
    playlist_items: str = ""
    max_retries: int = 3
    custom_headers: Dict[str, str] = field(default_factory=dict)
    template: str = "%(title)s.%(ext)s"
    audio_only: bool = False
    merge_format: str = "bestvideo+bestaudio/best"
    geo_bypass: bool = True
    geo_bypass_country: str = ""
    no_check_certificate: bool = False
    extra_args: Dict[str, Any] = field(default_factory=dict)


class DownloadEngine:
    """
    Core download engine wrapping yt-dlp with enhanced functionality.
    Thread-safe and supports callbacks for progress tracking.
    """

    def __init__(self):
        if yt_dlp is None:
            raise ImportError(
                "yt-dlp is not installed. Install it with: pip install yt-dlp"
            )
        self._lock = threading.Lock()
        self._cancel_event = threading.Event()

    def extract_info(
        self,
        url: str,
        download: bool = False,
        options: Optional[DownloadOptions] = None,
        progress_callback: Optional[Callable] = None,
    ) -> Optional[VideoInfo]:
        """Extract video information and optionally download."""
        opts = options or DownloadOptions(url=url)
        ydl_opts = self._build_ydl_opts(opts, download, progress_callback)

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=download)
                if info:
                    return self._parse_info(info, url)
        except Exception as e:
            logger.error(f"Error extracting info from {url}: {e}")
            raise
        return None

    def download(
        self,
        options: DownloadOptions,
        progress_callback: Optional[Callable] = None,
        status_callback: Optional[Callable] = None,
        complete_callback: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        Download a video with full progress tracking.
        Returns a dict with download results.
        """
        self._cancel_event.clear()
        ydl_opts = self._build_ydl_opts(options, True, progress_callback)

        results = {
            "success": False,
            "url": options.url,
            "files": [],
            "error": None,
            "info": None,
        }

        def cancel_hook(info_dict):
            if self._cancel_event.is_set():
                raise Exception("Download cancelled by user")

        ydl_opts["postprocessor_hooks"] = [cancel_hook]

        try:
            with self._lock:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(options.url, download=True)
                    if info:
                        results["info"] = self._parse_info(info, options.url)
                        results["success"] = True
                        # Collect downloaded files
                        if "requested_downloads" in info:
                            for d in info["requested_downloads"]:
                                filepath = d.get("filepath") or d.get("filename")
                                if filepath:
                                    results["files"].append(filepath)
                        elif info.get("_filename"):
                            results["files"].append(info["_filename"])

            if complete_callback:
                complete_callback(results)

        except Exception as e:
            error_msg = str(e)
            if "cancelled" in error_msg.lower():
                results["error"] = "Download cancelled"
            else:
                results["error"] = error_msg
            logger.error(f"Download failed for {options.url}: {e}")

            if status_callback:
                status_callback("error", results["error"])

        return results

    def cancel(self):
        """Cancel the current download."""
        self._cancel_event.set()

    def get_available_formats(self, url: str) -> List[Dict[str, Any]]:
        """Get all available formats for a video."""
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info and "formats" in info:
                    return self._format_list(info["formats"])
        except Exception as e:
            logger.error(f"Error getting formats for {url}: {e}")
            raise
        return []

    def list_playlist_entries(self, url: str) -> List[VideoInfo]:
        """List all entries in a playlist."""
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
            "dump_single_json": True,
        }
        entries = []
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info and "entries" in info:
                    for entry in info["entries"]:
                        if entry:
                            vi = VideoInfo(
                                id=entry.get("id", ""),
                                title=entry.get("title", "Unknown"),
                                url=entry.get("url", entry.get("webpage_url", "")),
                                webpage_url=entry.get("webpage_url", ""),
                                duration=entry.get("duration", 0),
                                uploader=entry.get("uploader", ""),
                                thumbnail=entry.get("thumbnail", ""),
                            )
                            entries.append(vi)
        except Exception as e:
            logger.error(f"Error listing playlist {url}: {e}")
            raise
        return entries

    def _build_ydl_opts(
        self,
        options: DownloadOptions,
        download: bool,
        progress_callback: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """Build yt-dlp options dictionary from DownloadOptions."""
        output_template = os.path.join(
            options.output_dir or ".",
            options.template,
        )

        ydl_opts: Dict[str, Any] = {
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
            "noprogress": True,
            "ignoreerrors": False,
            "retries": options.max_retries,
            "fragment_retries": options.max_retries,
            "socket_timeout": 30,
            "geo_bypass": options.geo_bypass,
            "nocheckcertificate": options.no_check_certificate,
            "writethumbnail": options.embed_thumbnail,
            "writeinfojson": options.write_description,
        }

        # Format selection
        if options.audio_only:
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": options.audio_format,
                "preferredquality": "320",
            }]
        else:
            if options.resolution == "best":
                ydl_opts["format"] = options.merge_format
            elif options.resolution == "worst":
                ydl_opts["format"] = "worstvideo+worstaudio/worst"
            else:
                # Specific resolution (e.g., "1080", "720")
                res = options.resolution.replace("p", "")
                ydl_opts["format"] = (
                    f"bestvideo[height<={res}]+bestaudio/best[height<={res}]/best"
                )

        # Merge output format
        if not options.audio_only:
            ydl_opts.setdefault("postprocessors", [])
            ydl_opts["postprocessors"].append({
                "key": "FFmpegVideoConvertor",
                "preferedformat": options.video_format,
            })

        # Metadata embedding
        if options.embed_metadata:
            ydl_opts.setdefault("postprocessors", []).append({
                "key": "FFmpegMetadata",
            })

        # Thumbnail embedding
        if options.embed_thumbnail:
            ydl_opts.setdefault("postprocessors", []).append({
                "key": "EmbedThumbnail",
            })

        # Subtitles
        if options.write_subtitles:
            ydl_opts["writesubtitles"] = True
            ydl_opts["writeautomaticsub"] = True
            ydl_opts["subtitleslangs"] = ["all"]
            if options.embed_metadata:
                ydl_opts.setdefault("postprocessors", []).append({
                    "key": "FFmpegEmbedSubtitle",
                })

        # Rate limiting
        if options.rate_limit:
            ydl_opts["ratelimit"] = self._parse_rate_limit(options.rate_limit)

        # Proxy
        if options.proxy:
            ydl_opts["proxy"] = options.proxy

        # Cookies
        if options.cookies_file:
            ydl_opts["cookiefile"] = options.cookies_file

        # Playlist options
        if options.playlist_items:
            ydl_opts["playlist_items"] = options.playlist_items
        else:
            if options.playlist_start > 1:
                ydl_opts["playliststart"] = options.playlist_start
            if options.playlist_end:
                ydl_opts["playlistend"] = options.playlist_end

        # Geo bypass country
        if options.geo_bypass_country:
            ydl_opts["geo_bypass_country"] = options.geo_bypass_country

        # Custom headers
        if options.custom_headers:
            ydl_opts["http_headers"] = options.custom_headers

        # Progress hook
        if progress_callback:
            def hook(d):
                if d["status"] == "downloading":
                    total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
                    downloaded = d.get("downloaded_bytes", 0)
                    speed = d.get("speed", 0)
                    eta = d.get("eta", 0)
                    filename = d.get("filename", "")
                    progress = (downloaded / total * 100) if total else 0
                    progress_callback({
                        "status": "downloading",
                        "progress": round(progress, 2),
                        "downloaded": downloaded,
                        "total": total,
                        "speed": speed or 0,
                        "eta": eta or 0,
                        "filename": os.path.basename(filename),
                    })
                elif d["status"] == "finished":
                    progress_callback({
                        "status": "finished",
                        "progress": 100,
                        "filename": os.path.basename(d.get("filename", "")),
                    })
                elif d["status"] == "error":
                    progress_callback({
                        "status": "error",
                        "error": str(d.get("error", "Unknown error")),
                    })

            ydl_opts["progress_hooks"] = [hook]

        # Extra args
        for k, v in options.extra_args.items():
            ydl_opts[k] = v

        return ydl_opts

    def _parse_info(self, info: Dict[str, Any], url: str) -> VideoInfo:
        """Parse yt-dlp info dict into VideoInfo."""
        vi = VideoInfo(
            id=info.get("id", ""),
            title=info.get("title", "Unknown"),
            description=info.get("description", ""),
            duration=info.get("duration", 0) or 0,
            thumbnail=info.get("thumbnail", ""),
            uploader=info.get("uploader", info.get("channel", "")),
            upload_date=info.get("upload_date", ""),
            view_count=info.get("view_count", 0) or 0,
            like_count=info.get("like_count", 0) or 0,
            url=info.get("url", url),
            webpage_url=info.get("webpage_url", url),
            platform=info.get("extractor", ""),
            formats=info.get("formats", []),
            subtitles=list(info.get("subtitles", {}).keys()),
            is_playlist=info.get("_type") == "playlist" or "entries" in info,
            raw_info=info,
        )

        if vi.is_playlist:
            entries_data = info.get("entries", [])
            vi.playlist_count = len(entries_data) if entries_data else info.get("n_entries", 0)
            vi.playlist_title = info.get("title", "")
            for entry in (entries_data or []):
                if entry:
                    vi.entries.append(VideoInfo(
                        id=entry.get("id", ""),
                        title=entry.get("title", "Unknown"),
                        duration=entry.get("duration", 0),
                        url=entry.get("url", entry.get("webpage_url", "")),
                        webpage_url=entry.get("webpage_url", ""),
                        uploader=entry.get("uploader", ""),
                        thumbnail=entry.get("thumbnail", ""),
                    ))

        return vi

    def _format_list(self, formats: List[Dict]) -> List[Dict[str, Any]]:
        """Clean and sort format list."""
        cleaned = []
        for f in formats:
            cleaned.append({
                "format_id": f.get("format_id", ""),
                "ext": f.get("ext", ""),
                "resolution": f.get("resolution", ""),
                "width": f.get("width"),
                "height": f.get("height"),
                "fps": f.get("fps"),
                "vcodec": f.get("vcodec", "none"),
                "acodec": f.get("acodec", "none"),
                "filesize": f.get("filesize") or f.get("filesize_approx"),
                "tbr": f.get("tbr"),
                "format_note": f.get("format_note", ""),
            })
        return sorted(cleaned, key=lambda x: x.get("height") or 0, reverse=True)

    @staticmethod
    def _parse_rate_limit(rate: str) -> Optional[int]:
        """Parse rate limit string to bytes per second."""
        if not rate:
            return None
        rate = rate.strip().upper()
        multipliers = {"K": 1024, "M": 1024**2, "G": 1024**3}
        for suffix, mult in multipliers.items():
            if rate.endswith(suffix):
                try:
                    return int(float(rate[:-1]) * mult)
                except ValueError:
                    return None
        try:
            return int(rate)
        except ValueError:
            return None
