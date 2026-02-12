"""Filesystem watcher for live Obsidian vault sync using watchdog."""

import asyncio
import logging
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

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
        if not event.is_directory and self._is_markdown(event.src_path):
            logger.info("File created: %s", event.src_path)
            asyncio.run_coroutine_threadsafe(
                self.indexer.index_single_note(Path(event.src_path)), self.loop
            )

    def on_modified(self, event: FileSystemEvent) -> None:
        if not event.is_directory and self._is_markdown(event.src_path):
            logger.info("File modified: %s", event.src_path)
            asyncio.run_coroutine_threadsafe(
                self.indexer.index_single_note(Path(event.src_path)), self.loop
            )

    def on_deleted(self, event: FileSystemEvent) -> None:
        if not event.is_directory and self._is_markdown(event.src_path):
            logger.info("File deleted: %s", event.src_path)
            asyncio.run_coroutine_threadsafe(
                self.indexer.delete_note(Path(event.src_path)), self.loop
            )

    def on_moved(self, event: FileSystemEvent) -> None:
        # Delete old path, index new path
        if hasattr(event, "dest_path"):
            src_md = self._is_markdown(event.src_path)
            dest_md = self._is_markdown(event.dest_path)  # type: ignore[attr-defined]

            if src_md:
                logger.info("File moved from: %s", event.src_path)
                asyncio.run_coroutine_threadsafe(
                    self.indexer.delete_note(Path(event.src_path)), self.loop
                )
            if dest_md:
                logger.info("File moved to: %s", event.dest_path)  # type: ignore[attr-defined]
                asyncio.run_coroutine_threadsafe(
                    self.indexer.index_single_note(Path(event.dest_path)),  # type: ignore[attr-defined]
                    self.loop,
                )


async def start_watcher(indexer: VaultIndexer, vault_path: Path) -> None:
    """Start watching the vault for filesystem changes.

    Runs until cancelled or KeyboardInterrupt.
    """
    loop = asyncio.get_running_loop()
    handler = VaultEventHandler(loop, indexer)

    observer = Observer()
    observer.schedule(handler, str(vault_path), recursive=True)
    observer.start()
    logger.info("Watcher started on %s", vault_path)

    try:
        while True:
            await asyncio.sleep(1)
    except (asyncio.CancelledError, KeyboardInterrupt):
        logger.info("Stopping watcher")
    finally:
        observer.stop()
        observer.join()
