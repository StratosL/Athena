"""CLI entry points for the Athena indexer: setup-indices, index, watch."""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.config import get_settings
from src.indexer import VaultIndexer

console = Console()
logger = logging.getLogger(__name__)


def _configure_logging(level: str) -> None:
    """Set up logging and suppress noisy Elasticsearch transport logs."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.getLogger("elastic_transport").setLevel(logging.WARNING)


async def cmd_setup_indices(indexer: VaultIndexer) -> None:
    """Create Elasticsearch indices if they don't exist."""
    results = await indexer.setup_indices()

    table = Table(title="Index Setup")
    table.add_column("Index", style="cyan")
    table.add_column("Status", style="green")

    for name, created in results.items():
        status = "Created" if created else "Already exists"
        table.add_row(name, status)

    console.print(table)


async def cmd_index(indexer: VaultIndexer) -> None:
    """Parse and index the vault into Elasticsearch."""
    vault_path = Path(indexer.settings.vault_path)
    if not vault_path.is_dir():
        console.print(f"[red]Vault path does not exist: {vault_path}[/red]")
        sys.exit(1)

    console.print(f"Indexing vault: [cyan]{vault_path}[/cyan]")
    result = await indexer.index_vault()

    # Summary panel
    summary = (
        f"Total files: {result.total_files}\n"
        f"Indexed: {result.indexed}\n"
        f"Skipped (unchanged): {result.skipped}\n"
        f"Errors: {result.failed}"
    )
    style = "green" if result.failed == 0 else "yellow"
    console.print(Panel(summary, title="Index Results", border_style=style))

    # Error details
    if result.errors:
        err_table = Table(title="Errors", border_style="red")
        err_table.add_column("#", style="dim")
        err_table.add_column("Error")
        for i, err in enumerate(result.errors, 1):
            err_table.add_row(str(i), err)
        console.print(err_table)


async def cmd_watch(indexer: VaultIndexer) -> None:
    """Watch the vault for changes and sync to Elasticsearch in real time."""
    from src.watcher import start_watcher

    vault_path = Path(indexer.settings.vault_path)
    if not vault_path.is_dir():
        console.print(f"[red]Vault path does not exist: {vault_path}[/red]")
        sys.exit(1)

    console.print(f"Watching vault: [cyan]{vault_path}[/cyan]")
    console.print("[dim]Press Ctrl+C to stop[/dim]")
    await start_watcher(indexer, vault_path)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="athena-index",
        description="Athena Indexer — sync Obsidian vault to Elasticsearch",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("setup-indices", help="Create Elasticsearch indices")
    subparsers.add_parser("index", help="Bulk-index vault notes into Elasticsearch")
    subparsers.add_parser("watch", help="Watch vault for changes and sync in real time")

    args = parser.parse_args()

    settings = get_settings()
    _configure_logging(settings.log_level)

    async def _run() -> None:
        indexer = VaultIndexer(settings)
        try:
            if args.command == "setup-indices":
                await cmd_setup_indices(indexer)
            elif args.command == "index":
                await cmd_index(indexer)
            elif args.command == "watch":
                await cmd_watch(indexer)
        finally:
            await indexer.close()

    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        console.print("\n[dim]Stopped.[/dim]")


if __name__ == "__main__":
    main()
