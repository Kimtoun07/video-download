"""
GrabVid CLI — Premium terminal interface for video downloading.

Usage:
    grabvid <url>                    Download a single video
    grabvid batch <file>             Batch download from file
    grabvid episodes <url>           Download playlist/episodes
    grabvid info <url>               Show video information
    grabvid formats <url>            List available formats
    grabvid gui                      Launch the GUI
    grabvid platforms                List supported platforms
"""

import os
import sys
import time
import threading
from pathlib import Path
from typing import Optional

import click

# Ensure src is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.core.config import Config
from src.core.engine import DownloadEngine, DownloadOptions, VideoInfo
from src.core.downloader import DownloadManager, DownloadTask, DownloadState
from src.core.platforms import PlatformDetector, PlatformInfo
from src.core.batch import BatchProcessor, BatchConfig
from src.core.episodes import EpisodeManager
from src.utils.network import format_size, format_speed, format_eta, is_url_valid
from src.utils.system import open_folder, get_ffmpeg_path
from src.cli.formatters import (
    logo, header, section, divider, progress_bar, status_icon,
    brand, success, warning, error, info, muted, bold, dim, c,
    format_download_info,
)


# ─── Global Context ────────────────────────────────────────────────────
class Context:
    def __init__(self):
        self.config = Config()
        self.engine = None
        self.manager = None

    def get_engine(self):
        if self.engine is None:
            try:
                self.engine = DownloadEngine()
            except ImportError as e:
                click.echo(error(f"✗ yt-dlp not installed. Run: pip install yt-dlp"))
                sys.exit(1)
        return self.engine

    def get_manager(self):
        if self.manager is None:
            self.manager = DownloadManager(
                max_concurrent=self.config.get("download", "concurrent_downloads", 3),
                engine=self.get_engine(),
            )
        return self.manager


pass_ctx = click.make_pass_decorator(Context, ensure=True)


# ─── Main Group ────────────────────────────────────────────────────────
@click.group(invoke_without_command=True)
@click.option("--version", "-V", is_flag=True, help="Show version")
@click.option("--quiet", "-q", is_flag=True, help="Suppress output")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.pass_context
def cli(ctx, version, quiet, debug):
    """
    🎬 GrabVid — Universal Video Downloader

    Download videos from 1000+ platforms worldwide.
    """
    ctx.ensure_object(Context)

    if version:
        click.echo(f"GrabVid v1.0.0")
        return

    if ctx.invoked_subcommand is None:
        click.echo(logo())
        click.echo(f"  {bold('Usage:')} grabvid <command> [options]")
        click.echo()
        click.echo(f"  {brand('grabvid <url>')}          Download a video")
        click.echo(f"  {brand('grabvid batch <file>')}   Batch download from file")
        click.echo(f"  {brand('grabvid episodes <url>')} Download playlist/episodes")
        click.echo(f"  {brand('grabvid info <url>')}     Show video information")
        click.echo(f"  {brand('grabvid formats <url>')}  List available formats")
        click.echo(f"  {brand('grabvid gui')}            Launch the GUI application")
        click.echo(f"  {brand('grabvid platforms')}      List supported platforms")
        click.echo()
        click.echo(f"  Run {bold('grabvid --help')} for full options.")
        click.echo()


# ─── Download Command (default) ────────────────────────────────────────
@cli.command("download")
@click.argument("url", required=False)
@click.option("--output", "-o", type=click.Path(), help="Output directory")
@click.option("--format", "-f", "fmt", default="best", help="Video format (best, worst, 1080p, 720p, etc.)")
@click.option("--resolution", "-r", help="Max resolution (e.g., 1080, 720)")
@click.option("--audio-only", "-a", is_flag=True, help="Download audio only")
@click.option("--audio-format", type=click.Choice(["mp3", "aac", "flac", "ogg", "wav", "m4a"]), default="mp3")
@click.option("--subtitles/--no-subtitles", default=True, help="Download subtitles")
@click.option("--thumbnail/--no-thumbnail", default=True, help="Embed thumbnail")
@click.option("--metadata/--no-metadata", default=True, help="Embed metadata")
@click.option("--rate-limit", help="Download rate limit (e.g., 5M, 1000K)")
@click.option("--proxy", help="HTTP/SOCKS proxy URL")
@click.option("--cookies", type=click.Path(exists=True), help="Cookies file")
@click.option("--retries", type=int, default=3, help="Max retries")
@click.option("--playlist-items", help="Playlist items (e.g., 1-5, 1,3,5)")
@click.option("--template", help="Output filename template")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
@pass_ctx
def download_cmd(ctx, url, output, fmt, resolution, audio_only, audio_format,
                 subtitles, thumbnail, metadata, rate_limit, proxy, cookies,
                 retries, playlist_items, template, yes):
    """Download a video or audio file."""
    if not url:
        click.echo(error("✗ Please provide a URL."))
        click.echo(f"  Usage: {brand('grabvid download <url>')}")
        return

    if not is_url_valid(url):
        click.echo(error(f"✗ Invalid URL: {url}"))
        return

    # Detect platform
    platform_info = PlatformDetector.detect(url)

    # Show info header
    click.echo(logo())

    if platform_info:
        click.echo(f"  {platform_info.icon} Platform: {bold(platform_info.name)}")
        if platform_info.notes:
            click.echo(f"  {muted('⚠ ' + platform_info.notes)}")
    else:
        click.echo(f"  🌐 Platform: {bold('Auto-detect')}")

    click.echo(f"  🔗 URL: {dim(url)}")
    click.echo()

    # Extract info
    engine = ctx.get_engine()

    with click.progressbar(length=100, label=f"  {info('Extracting info')}",
                           show_eta=False, show_percent=False) as bar:
        bar.update(30)
        try:
            video_info = engine.extract_info(url)
        except Exception as e:
            click.echo(error(f"\n✗ Failed to extract info: {e}"))
            return
        bar.update(70)

    if not video_info:
        click.echo(error("✗ Could not extract video information."))
        return

    # Display video info
    click.echo(section("Video Information"))
    click.echo(f"  {bold('Title:')}    {video_info.title}")
    click.echo(f"  {bold('Duration:')} {video_info.duration_str}")
    click.echo(f"  {bold('Uploader:')} {video_info.uploader}")
    if video_info.is_playlist:
        click.echo(f"  {bold('Type:')}     Playlist ({video_info.playlist_count} items)")
    click.echo(f"  {bold('Quality:')}  {video_info.best_resolution}")
    click.echo()

    if not yes and not click.confirm(f"  {brand('▶')} Download this video?", default=True):
        click.echo(muted("  Cancelled."))
        return

    # Build options
    options = DownloadOptions(
        url=url,
        output_dir=output or str(ctx.config.output_dir),
        format_id=fmt,
        resolution=resolution or ctx.config.get("download", "max_resolution", "best"),
        audio_only=audio_only,
        audio_format=audio_format,
        write_subtitles=subtitles,
        embed_thumbnail=thumbnail,
        embed_metadata=metadata,
        rate_limit=rate_limit or "",
        proxy=proxy or "",
        cookies_file=cookies or "",
        max_retries=retries,
        playlist_items=playlist_items or "",
        template=template or ctx.config.get("naming", "template"),
    )

    # Ensure output directory exists
    Path(options.output_dir).mkdir(parents=True, exist_ok=True)

    # Download
    click.echo(section("Downloading"))

    progress_data = {"last_print": 0}

    def on_progress(data):
        now = time.time()
        if now - progress_data["last_print"] < 0.3:
            return
        progress_data["last_print"] = now

        pct = data.get("progress", 0)
        speed = format_speed(data.get("speed", 0))
        eta = format_eta(data.get("eta", 0))
        dl = format_size(data.get("downloaded", 0))
        total = format_size(data.get("total", 0))
        fname = data.get("filename", "")[:40]

        bar = progress_bar(pct, width=30)
        line = f"\r  {bar}  {dl}/{total}  {speed}  ETA {eta}  {dim(fname)}"
        sys.stdout.write(line)
        sys.stdout.flush()

    result = engine.download(options, progress_callback=on_progress)

    click.echo()  # Newline after progress

    if result["success"]:
        click.echo(f"\n  {success('✓ Download complete!')}")
        if result.get("files"):
            for f in result["files"]:
                click.echo(f"  📁 {dim(f)}")
        click.echo(f"\n  {muted('Output:')} {options.output_dir}")
    else:
        click.echo(f"\n  {error('✗ Download failed:')} {result.get('error', 'Unknown error')}")
        sys.exit(1)


# ─── Info Command ──────────────────────────────────────────────────────
@cli.command("info")
@click.argument("url")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@pass_ctx
def info_cmd(ctx, url, as_json):
    """Show detailed information about a video."""
    engine = ctx.get_engine()

    try:
        video_info = engine.extract_info(url)
    except Exception as e:
        click.echo(error(f"✗ Failed: {e}"))
        return

    if not video_info:
        click.echo(error("✗ No information available."))
        return

    if as_json:
        import json
        data = {
            "id": video_info.id,
            "title": video_info.title,
            "duration": video_info.duration,
            "uploader": video_info.uploader,
            "upload_date": video_info.upload_date,
            "view_count": video_info.view_count,
            "like_count": video_info.like_count,
            "platform": video_info.platform,
            "url": video_info.webpage_url,
            "is_playlist": video_info.is_playlist,
            "playlist_count": video_info.playlist_count,
            "formats_count": len(video_info.formats),
            "subtitles": video_info.subtitles,
        }
        click.echo(json.dumps(data, indent=2, ensure_ascii=False))
        return

    click.echo(header("Video Information"))
    click.echo(f"  {bold('Title:')}      {video_info.title}")
    click.echo(f"  {bold('Platform:')}   {video_info.platform}")
    click.echo(f"  {bold('Duration:')}   {video_info.duration_str}")
    click.echo(f"  {bold('Uploader:')}   {video_info.uploader}")
    click.echo(f"  {bold('Views:')}      {video_info.view_count:,}")
    click.echo(f"  {bold('Likes:')}      {video_info.like_count:,}")
    click.echo(f"  {bold('Upload Date:')} {video_info.upload_date}")
    click.echo(f"  {bold('Formats:')}    {len(video_info.formats)} available")

    if video_info.subtitles:
        click.echo(f"  {bold('Subtitles:')}  {', '.join(video_info.subtitles[:10])}")

    if video_info.is_playlist:
        click.echo(f"\n  {bold('Playlist:')}   {video_info.playlist_title}")
        click.echo(f"  {bold('Items:')}      {video_info.playlist_count}")
        click.echo(divider())
        for i, entry in enumerate(video_info.entries[:20]):
            dur = f"{int(entry.duration // 60)}:{int(entry.duration % 60):02d}" if entry.duration else "??:??"
            click.echo(f"  {dim(f'{i+1:3d}.')} {entry.title} {dim(f'[{dur}]')}")
        if len(video_info.entries) > 20:
            click.echo(f"  {muted(f'... and {len(video_info.entries) - 20} more')}")

    click.echo()


# ─── Formats Command ───────────────────────────────────────────────────
@cli.command("formats")
@click.argument("url")
@pass_ctx
def formats_cmd(ctx, url):
    """List available formats for a video."""
    engine = ctx.get_engine()

    try:
        formats = engine.get_available_formats(url)
    except Exception as e:
        click.echo(error(f"✗ Failed: {e}"))
        return

    click.echo(header("Available Formats"))
    click.echo(f"  {'ID':<10} {'Ext':<6} {'Resolution':<12} {'FPS':<6} {'VCodec':<12} {'ACodec':<10} {'Size':<10} {'Note'}")
    click.echo(divider())

    for f in formats:
        size = format_size(f["filesize"]) if f.get("filesize") else "—"
        fps = str(f.get("fps") or "—")
        res = f.get("resolution") or "—"
        click.echo(
            f"  {f['format_id']:<10} {f.get('ext', '—'):<6} {res:<12} {fps:<6} "
            f"{f.get('vcodec', '—'):<12} {f.get('acodec', '—'):<10} {size:<10} "
            f"{dim(f.get('format_note', ''))}"
        )
    click.echo()


# ─── Batch Command ─────────────────────────────────────────────────────
@cli.command("batch")
@click.argument("source")
@click.option("--output", "-o", type=click.Path(), help="Output directory")
@click.option("--delay", type=float, default=1.0, help="Delay between downloads (seconds)")
@click.option("--concurrent", type=int, default=3, help="Max concurrent downloads")
@click.option("--stop-on-error", is_flag=True, help="Stop batch on first error")
@click.option("--format", "-f", "fmt", default="best", help="Video format")
@pass_ctx
def batch_cmd(ctx, source, output, delay, concurrent, stop_on_error, fmt):
    """Batch download from a file or text containing URLs."""
    click.echo(logo())

    # Determine if source is a file or text
    if os.path.isfile(source):
        urls = BatchProcessor.load_urls_from_file(source)
        click.echo(f"  📄 Loaded {len(urls)} URLs from: {dim(source)}")
    else:
        urls = BatchProcessor.extract_urls(source)
        if not urls:
            # Treat as a single URL
            urls = [source]
        click.echo(f"  📋 Found {len(urls)} URLs")

    if not urls:
        click.echo(error("✗ No valid URLs found."))
        return

    for i, url in enumerate(urls):
        click.echo(f"  {dim(f'{i+1}.')} {url[:70]}")

    click.echo()

    engine = ctx.get_engine()
    manager = DownloadManager(max_concurrent=concurrent, engine=engine)
    batch = BatchProcessor(manager)

    config = BatchConfig(
        urls=urls,
        delay_between=delay,
        max_concurrent=concurrent,
        stop_on_error=stop_on_error,
        output_dir=output or str(ctx.config.output_dir),
    )

    options = DownloadOptions(
        format_id=fmt,
        output_dir=config.output_dir,
    )
    config.options = options

    Path(config.output_dir).mkdir(parents=True, exist_ok=True)

    completed_count = [0]

    def on_batch_progress(data):
        if data.get("type") == "task_added":
            click.echo(f"  {status_icon('queued')} Queued [{data['index']}/{data['total']}] {dim(data['url'][:50])}")
        elif data.get("type") == "progress":
            completed = data.get("completed", 0)
            if completed > completed_count[0]:
                completed_count[0] = completed
                click.echo(f"  {status_icon('completed')} Completed [{completed}/{data['total']}]")

    def on_batch_complete(result):
        click.echo(divider())
        click.echo(section("Batch Complete"))
        click.echo(f"  {success('✓ Completed:')} {result.completed}/{result.total}")
        if result.failed:
            click.echo(f"  {error('✗ Failed:')}    {result.failed}")
        if result.cancelled:
            click.echo(f"  {warning('⊘ Cancelled:')} {result.cancelled}")
        click.echo(f"  {bold('Success Rate:')} {result.success_rate:.1f}%")
        click.echo(f"  {bold('Duration:')}     {result.duration:.1f}s")
        click.echo()

        if result.errors:
            click.echo(section("Errors"))
            for err in result.errors[:10]:
                click.echo(f"  {error('✗')} {err['url'][:50]}")
                click.echo(f"    {dim(err['error'][:80])}")
            click.echo()

    click.echo()
    result = batch.process(config, progress_callback=on_batch_progress, complete_callback=on_batch_complete)

    manager.shutdown()


# ─── Episodes Command ──────────────────────────────────────────────────
@cli.command("episodes")
@click.argument("url")
@click.option("--output", "-o", type=click.Path(), help="Output directory")
@click.option("--range", "-r", "ep_range", help="Episode range (e.g., 1-10)")
@click.option("--list", "-l", "list_only", is_flag=True, help="List episodes only")
@click.option("--format", "-f", "fmt", default="best", help="Video format")
@pass_ctx
def episodes_cmd(ctx, url, output, ep_range, list_only, fmt):
    """Download playlist or episodic content."""
    click.echo(logo())
    click.echo(f"  🔍 Detecting episodes from: {dim(url)}")
    click.echo()

    engine = ctx.get_engine()
    manager = DownloadManager(
        max_concurrent=ctx.config.get("download", "concurrent_downloads", 3),
        engine=engine,
    )
    ep_manager = EpisodeManager(engine=engine, manager=manager)

    try:
        series = ep_manager.detect_series(url)
    except Exception as e:
        click.echo(error(f"✗ Failed: {e}"))
        return

    if not series:
        click.echo(error("✗ No episodes detected."))
        return

    # Display series info
    click.echo(header("Series Information"))
    click.echo(f"  {bold('Title:')}     {series.title}")
    click.echo(f"  {bold('Platform:')}  {series.platform}")
    click.echo(f"  {bold('Episodes:')}  {series.total_episodes}")
    click.echo(f"  {bold('Duration:')}  {series.duration_str}")
    click.echo(divider())

    # List episodes
    for ep in series.episodes:
        dur = f"{int(ep.duration // 60)}:{int(ep.duration % 60):02d}" if ep.duration else "??:??"
        prefix = f"S{ep.season:02d}" if ep.season else "  "
        click.echo(f"  {prefix}E{ep.episode:02d} │ {dim(dur)} │ {ep.title}")

    click.echo()

    if list_only:
        return

    # Parse range
    ep_range_tuple = None
    if ep_range:
        parts = ep_range.split("-")
        if len(parts) == 2:
            ep_range_tuple = (int(parts[0]), int(parts[1]))

    # Download
    click.echo(section("Downloading Episodes"))

    options = DownloadOptions(
        format_id=fmt,
        output_dir=output or str(ctx.config.output_dir),
    )

    tasks = ep_manager.download_series(series, options, ep_range_tuple)
    click.echo(f"  📥 Queued {len(tasks)} episodes")
    click.echo()

    # Wait for completion
    while True:
        all_done = True
        for task in tasks:
            t = manager.get_task(task.id)
            if t and not t.is_terminal:
                all_done = False
                pct = t.progress.progress if t.progress else 0
                state_icon = status_icon(t.state.value)
                fname = t.progress.filename[:35] if t.progress and t.progress.filename else ""
                sys.stdout.write(f"\r  {state_icon} {pct:5.1f}% {dim(fname)}    ")
                sys.stdout.flush()

        if all_done:
            break
        time.sleep(0.5)

    click.echo(f"\n\n  {success('✓ All episodes downloaded!')}")
    click.echo(f"  📁 {options.output_dir}")
    click.echo()

    manager.shutdown()


# ─── Platforms Command ─────────────────────────────────────────────────
@cli.command("platforms")
@click.option("--region", "-r", help="Filter by region")
@click.option("--search", "-s", help="Search platforms")
def platforms_cmd(region, search):
    """List all supported platforms."""
    click.echo(header("Supported Platforms"))
    click.echo(f"  {muted('GrabVid supports 1000+ platforms via yt-dlp.')}")
    click.echo(f"  {muted('Featured platforms listed below:')}\n")

    if search:
        platforms = PlatformDetector.search_platforms(search)
        msg = f'Search results for "{search}":'
        click.echo(f"  {info(msg)}\n")
    elif region:
        platforms = PlatformDetector.get_platforms_by_region(region)
        click.echo(f"  {info(f'Region: {region}')}\n")
    else:
        platforms = PlatformDetector.get_all_platforms()
        # Group by region
        regions = {}
        for p in platforms:
            regions.setdefault(p.region, []).append(p)

        for region_name, region_platforms in sorted(regions.items()):
            click.echo(section(region_name.upper()))
            for p in region_platforms:
                login = warning(" [login]") if p.requires_login else ""
                click.echo(f"  {p.icon} {bold(p.name):<30} {dim(p.domain)}{login}")
                if p.notes:
                    click.echo(f"    {dim(p.notes)}")
            click.echo()
        return

    for p in platforms:
        login = warning(" [login]") if p.requires_login else ""
        click.echo(f"  {p.icon} {bold(p.name):<30} {dim(p.domain)}{login}")
    click.echo()


# ─── GUI Command ───────────────────────────────────────────────────────
@cli.command("gui")
@pass_ctx
def gui_cmd(ctx):
    """Launch the GrabVid GUI application."""
    click.echo(f"  {brand('▶')} Launching GrabVid GUI...")
    try:
        from src.gui.app import GrabVidGUI
        app = GrabVidGUI()
        app.run()
    except ImportError as e:
        click.echo(error(f"✗ GUI dependencies not installed: {e}"))
        click.echo(f"  Install with: {brand('pip install customtkinter')}")
    except Exception as e:
        click.echo(error(f"✗ GUI error: {e}"))


# ─── Config Command ────────────────────────────────────────────────────
@cli.command("config")
@click.option("--show", is_flag=True, help="Show current config")
@click.option("--set", "set_val", nargs=2, type=str, help="Set config value (section.key value)")
@click.option("--reset", is_flag=True, help="Reset to defaults")
@click.option("--path", is_flag=True, help="Show config file path")
@pass_ctx
def config_cmd(ctx, show, set_val, reset, path):
    """Manage GrabVid configuration."""
    if path:
        click.echo(f"  Config: {ctx.config.config_path}")
        return

    if reset:
        ctx.config.reset()
        click.echo(success("  ✓ Configuration reset to defaults."))
        return

    if set_val:
        key, value = set_val
        parts = key.split(".")
        if len(parts) == 2:
            sec_name, key = parts
            # Try to parse as number or bool
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    if value.lower() in ("true", "yes"):
                        value = True
                    elif value.lower() in ("false", "no"):
                        value = False
            ctx.config.set(sec_name, key, value)
            ctx.config.save()
            click.echo(success(f"  ✓ Set {sec_name}.{key} = {value}"))
        else:
            click.echo(error("  ✗ Use format: section.key"))
        return

    if show:
        import json
        click.echo(header("Configuration"))
        config_dict = ctx.config.to_dict()
        for section_name, values in config_dict.items():
            click.echo(section(f"  {section_name}"))
            for k, v in values.items():
                click.echo(f"    {dim(k + ':'):25s} {v}")
        click.echo()
        return

    click.echo(f"  Config file: {ctx.config.config_path}")
    click.echo(f"  Download dir: {ctx.config.output_dir}")


# ─── Entry Point ───────────────────────────────────────────────────────
def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
