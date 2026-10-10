"""
Episode and playlist management for GrabVid.
Smart detection and organization of episodic content.
"""

import re
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .engine import DownloadEngine, VideoInfo, DownloadOptions
from .downloader import DownloadManager, DownloadTask
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Episode:
    """Represents a single episode in a series."""
    index: int = 0
    title: str = ""
    url: str = ""
    duration: float = 0
    season: int = 0
    episode: int = 0
    video_info: Optional[VideoInfo] = None
    task: Optional[DownloadTask] = None


@dataclass
class Series:
    """Represents a series or playlist of episodes."""
    title: str = ""
    url: str = ""
    platform: str = ""
    total_episodes: int = 0
    episodes: List[Episode] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    @property
    def duration_str(self) -> str:
        total = sum(ep.duration for ep in self.episodes)
        hours = int(total // 3600)
        minutes = int((total % 3600) // 60)
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"


class EpisodeManager:
    """
    Manages episode detection, series organization, and playlist downloads.
    Supports smart episode numbering and season detection.
    """

    # Patterns for episode detection
    EPISODE_PATTERNS = [
        re.compile(r'[Ee](?:pisode)?\s*(\d+)', re.IGNORECASE),
        re.compile(r'[Ee][Pp]\s*(\d+)', re.IGNORECASE),
        re.compile(r'[Ee][Pp][Ii]?[Ss]?[Oo]?[Dd]?[Ee]?\s*(\d+)', re.IGNORECASE),
        re.compile(r'#\s*(\d+)', re.IGNORECASE),
        re.compile(r'第\s*(\d+)\s*[集话期話]', re.IGNORECASE),  # Chinese
        re.compile(r'(\d+)\s*[集话期話]', re.IGNORECASE),  # Chinese simplified
        re.compile(r'[Ss](\d+)\s*[Ee](\d+)', re.IGNORECASE),  # S01E01
    ]

    SEASON_PATTERN = re.compile(r'[Ss](?:eason)?\s*(\d+)', re.IGNORECASE)

    def __init__(self, engine: Optional[DownloadEngine] = None, manager: Optional[DownloadManager] = None):
        self._engine = engine or DownloadEngine()
        self._manager = manager

    def detect_series(self, url: str) -> Optional[Series]:
        """Detect and build a Series from a URL (playlist, channel, etc.)."""
        try:
            info = self._engine.extract_info(url)
            if not info:
                return None

            series = Series(
                title=info.title or info.playlist_title,
                url=url,
                platform=info.platform,
            )

            if info.is_playlist and info.entries:
                series.total_episodes = len(info.entries)
                for i, entry in enumerate(info.entries):
                    ep = Episode(
                        index=i + 1,
                        title=entry.title,
                        url=entry.url or entry.webpage_url,
                        duration=entry.duration or 0,
                        video_info=entry,
                    )
                    # Try to extract episode/season numbers
                    season, episode = self._extract_episode_info(entry.title)
                    if season:
                        ep.season = season
                    if episode:
                        ep.episode = episode
                    else:
                        ep.episode = i + 1

                    series.episodes.append(ep)
            else:
                # Single video - try to find related episodes
                ep = Episode(
                    index=1,
                    title=info.title,
                    url=url,
                    duration=info.duration,
                    video_info=info,
                    episode=1,
                )
                series.episodes.append(ep)
                series.total_episodes = 1

            return series

        except Exception as e:
            logger.error(f"Error detecting series from {url}: {e}")
            raise

    def download_series(
        self,
        series: Series,
        options: Optional[DownloadOptions] = None,
        episode_range: Optional[Tuple[int, int]] = None,
        progress_callback=None,
    ) -> List[DownloadTask]:
        """Download episodes from a series."""
        if not self._manager:
            raise ValueError("DownloadManager required for series download")

        episodes = series.episodes
        if episode_range:
            start, end = episode_range
            episodes = [ep for ep in episodes if start <= ep.index <= end]

        tasks = []
        base_opts = options or DownloadOptions()

        for ep in episodes:
            ep_opts = DownloadOptions(
                url=ep.url,
                output_dir=base_opts.output_dir or os.path.join(
                    base_opts.output_dir or ".",
                    self._sanitize(series.title),
                ),
                template=self._build_episode_template(series, ep, base_opts),
                format_id=base_opts.format_id,
                video_format=base_opts.video_format,
                resolution=base_opts.resolution,
                write_subtitles=base_opts.write_subtitles,
                embed_thumbnail=base_opts.embed_thumbnail,
                embed_metadata=base_opts.embed_metadata,
                max_retries=base_opts.max_retries,
            )

            task = self._manager.add_task(ep.url, ep_opts, auto_start=True)
            task.title = ep.title
            task.metadata["series"] = series.title
            task.metadata["episode"] = ep.index
            task.metadata["season"] = ep.season
            ep.task = task
            tasks.append(task)

            if progress_callback:
                progress_callback({
                    "type": "episode_queued",
                    "episode": ep.index,
                    "total": len(episodes),
                    "title": ep.title,
                })

        return tasks

    def download_episodes_range(
        self,
        url: str,
        start: int,
        end: int,
        options: Optional[DownloadOptions] = None,
    ) -> List[DownloadTask]:
        """Download a specific range of episodes."""
        series = self.detect_series(url)
        if not series:
            raise ValueError(f"Could not detect series from {url}")
        return self.download_series(series, options, (start, end))

    def get_episode_list(self, url: str) -> List[Episode]:
        """Get list of episodes without downloading."""
        series = self.detect_series(url)
        return series.episodes if series else []

    def _extract_episode_info(self, title: str) -> Tuple[Optional[int], Optional[int]]:
        """Extract season and episode numbers from a title."""
        season = None
        episode = None

        # Try S01E01 pattern
        m = self.EPISODE_PATTERNS[-1].search(title)
        if m:
            season = int(m.group(1))
            episode = int(m.group(2))
            return season, episode

        # Try season pattern
        m = self.SEASON_PATTERN.search(title)
        if m:
            season = int(m.group(1))

        # Try episode patterns
        for pattern in self.EPISODE_PATTERNS[:-1]:
            m = pattern.search(title)
            if m:
                episode = int(m.group(1))
                break

        return season, episode

    def _build_episode_template(self, series: Series, ep: Episode, base_opts: DownloadOptions) -> str:
        """Build a file naming template for an episode."""
        if ep.season > 0 and ep.episode > 0:
            return f"S{ep.season:02d}E{ep.episode:02d} - %(title)s.%(ext)s"
        elif ep.episode > 0:
            return f"{ep.episode:03d} - %(title)s.%(ext)s"
        else:
            return f"{ep.index:03d} - %(title)s.%(ext)s"

    @staticmethod
    def _sanitize(name: str) -> str:
        """Sanitize a string for use as a filename."""
        name = re.sub(r'[<>:"/\\|?*]', '_', name)
        name = name.strip('. ')
        return name[:200] if name else "untitled"

    def preview_episodes(self, url: str) -> str:
        """Generate a preview text of episodes in a series."""
        series = self.detect_series(url)
        if not series:
            return "No episodes found."

        lines = [
            f"📺 Series: {series.title}",
            f"🎬 Platform: {series.platform}",
            f"📋 Episodes: {series.total_episodes}",
            f"⏱️  Total Duration: {series.duration_str}",
            "",
            "─" * 50,
        ]

        for ep in series.episodes:
            dur = f"{int(ep.duration // 60)}:{int(ep.duration % 60):02d}" if ep.duration else "??:??"
            prefix = f"S{ep.season:02d}" if ep.season else "  "
            lines.append(f"  {prefix}E{ep.episode:02d} │ {dur} │ {ep.title}")

        return "\n".join(lines)
