"""Filesystem watcher for live Obsidian vault sync using watchdog.

Supports two modes:
- Native (default): Uses OS filesystem events (inotify on Linux). Fast, zero-delay.
- Polling (fallback): Checks for file changes every N seconds. Works on Docker
  bind-mounted Windows/macOS volumes where inotify events don't propagate.

Set WATCHER_POLLING=true to force polling mode, or the watcher auto-detects
by writing a test file and checking if an event fires within 3 seconds.
"""

import asyncio
import logging
import threading
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver

from src.indexer import VaultIndexer

logger = logging.getLogger(__name__)


class VaultEventHandler(FileSystemEventHandler):
    """Bridge watchdog sync callbacks to async VaultIndexer operations."""

    def __init__(self, loop: asyncio.AbstractEventLoop, indexer: VaultIndexer) -> None:
        super().__init__()
        self.loop = loop
        self.indexer = indexer

    def _is_markdown(self, path: str) -> bool:
        """Check if path is a non-hidden markdown file."""
        p = Path(path)
        if not p.suffix == ".md":
            return False
        # Skip hidden directories / files
        return not any(part.startswith(".") for part in p.parts)

    def on_created(self, event: FileSystemEvent) -> None:
        src = str(event.src_path)
        if not event.is_directory and self._is_markdown(src):
            logger.info("File created: %s", src)
            asyncio.run_coroutine_threadsafe(self.indexer.index_single_note(Path(src)), self.loop)

    def on_modified(self, event: FileSystemEvent) -> None:
        src = str(event.src_path)
        if not event.is_directory and self._is_markdown(src):
            logger.info("File modified: %s", src)
            asyncio.run_coroutine_threadsafe(self.indexer.index_single_note(Path(src)), self.loop)

    def on_deleted(self, event: FileSystemEvent) -> None:
        src = str(event.src_path)
        if not event.is_directory and self._is_markdown(src):
            logger.info("File deleted: %s", src)
            asyncio.run_coroutine_threadsafe(self.indexer.delete_note(Path(src)), self.loop)

    def on_moved(self, event: FileSystemEvent) -> None:
        # Delete old path, index new path
        if hasattr(event, "dest_path"):
            src = str(event.src_path)
            dest = str(event.dest_path)  # type: ignore[attr-defined]
            src_md = self._is_markdown(src)
            dest_md = self._is_markdown(dest)

            if src_md:
                logger.info("File moved from: %s", src)
                asyncio.run_coroutine_threadsafe(self.indexer.delete_note(Path(src)), self.loop)
            if dest_md:
                logger.info("File moved to: %s", dest)
                asyncio.run_coroutine_threadsafe(
                    self.indexer.index_single_note(Path(dest)), self.loop
                )


def _detect_inotify_works(vault_path: Path, timeout: float = 3.0) -> bool:
    """Write a temp file and check if the native observer fires an event.

    Returns True if inotify works (native mode is safe), False if events
    don't propagate (need polling fallback).
    """
    event_fired = threading.Event()

    class _ProbeHandler(FileSystemEventHandler):
        def on_created(self, event: FileSystemEvent) -> None:
            event_fired.set()

        def on_modified(self, event: FileSystemEvent) -> None:
            event_fired.set()

    observer = Observer()
    handler = _ProbeHandler()
    observer.schedule(handler, str(vault_path), recursive=False)
    observer.start()

    # Write a temporary probe file
    probe = vault_path / ".athena-inotify-probe"
    try:
        probe.write_text("probe", encoding="utf-8")
        detected = event_fired.wait(timeout=timeout)
    except OSError:
        # Read-only filesystem (e.g. Docker :ro mount) — inotify won't help
        logger.debug("Cannot write probe file (read-only filesystem)")
        detected = False
    finally:
        try:
            probe.unlink(missing_ok=True)
        except OSError:
            pass
        observer.stop()
        observer.join()

    return detected


async def start_watcher(
    indexer: VaultIndexer,
    vault_path: Path,
    force_polling: bool = False,
    poll_interval: int = 30,
) -> None:
    """Start watching the vault for filesystem changes.

    Args:
        indexer: VaultIndexer instance for ES operations.
        vault_path: Path to the Obsidian vault root.
        force_polling: If True, skip auto-detection and use polling.
        poll_interval: Seconds between polls in polling mode.
    """
    loop = asyncio.get_running_loop()
    handler = VaultEventHandler(loop, indexer)

    use_polling = force_polling
    if not use_polling:
        logger.info("Testing filesystem event support...")
        works = await loop.run_in_executor(None, _detect_inotify_works, vault_path)
        if not works:
            logger.warning(
                "Native filesystem events not detected (Docker bind-mount?). "
                "Falling back to polling every %ds.",
                poll_interval,
            )
            use_polling = True
        else:
            logger.info("Native filesystem events working — using inotify mode")

    if use_polling:
        observer = PollingObserver(timeout=poll_interval)
        mode_label = f"polling (every {poll_interval}s)"
    else:
        observer = Observer()
        mode_label = "native (inotify)"

    observer.schedule(handler, str(vault_path), recursive=True)
    observer.start()
    logger.info("Watcher started on %s [%s]", vault_path, mode_label)

    # Run an initial bulk index to catch notes created before the watcher started
    logger.info("Running initial bulk index to sync existing notes...")
    result = await indexer.index_vault()
    logger.info(
        "Initial sync complete — %d indexed, %d skipped, %d errors",
        result.indexed,
        result.skipped,
        result.failed,
    )

    try:
        while True:
            await asyncio.sleep(1)
    except (asyncio.CancelledError, KeyboardInterrupt):
        logger.info("Stopping watcher")
    finally:
        observer.stop()
        observer.join()
