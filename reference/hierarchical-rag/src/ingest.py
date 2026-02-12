"""Ingestion entry point for Hierarchical RAG Workshop.

This module handles:
1. Environment validation
2. Database connection testing
3. Schema creation
4. Document generation (if needed)
5. Document ingestion
"""

import os
import asyncio
import shutil
import logging
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

from .settings import load_settings
from .db.connection import get_pool, close_pool, test_connection, enable_pgvector
from .db.schema import create_schema, check_pgvector_extension
from .ingestion.pipeline import run_ingestion
from .generate_docs import generate_documents

console = Console()
logger = logging.getLogger(__name__)


async def check_env_file() -> bool:
    """Check if .env file exists and prompt user if needed.

    Returns:
        True if .env is configured, False otherwise.
    """
    env_path = Path(".env")
    env_example_path = Path(".env.example")

    if not env_path.exists():
        if env_example_path.exists():
            console.print(Panel(
                "[yellow][WARNING]  No .env file found.[/yellow]\n\n"
                "Created .env from .env.example.\n\n"
                "[bold]Please update the following values in .env:[/bold]\n"
                "  - DATABASE_URL (your PostgreSQL connection string)\n"
                "  - OPENROUTER_API_KEY (your OpenRouter API key)\n\n"
                "[dim]The same OpenRouter key works for both LLM and embeddings.[/dim]",
                title="Environment Setup",
                border_style="yellow"
            ))

            # Copy .env.example to .env
            shutil.copy(env_example_path, env_path)

            console.print()
            input("Press Enter when you've updated .env...")
            console.print()
        else:
            console.print("[red]Error: Neither .env nor .env.example found.[/red]")
            return False

    return True


async def validate_database() -> bool:
    """Validate database connection and pgvector extension.

    Returns:
        True if database is ready, False otherwise.
    """
    console.print("[bold blue]Validating database connection...[/bold blue]")

    try:
        # Test basic connection (without pgvector)
        if not await test_connection():
            console.print(
                "[red]Database connection failed.[/red]\n"
                "Please check your DATABASE_URL in .env\n"
                "  - Is PostgreSQL running?\n"
                "  - Is the database created?\n"
                "  - Are credentials correct?"
            )
            return False

        console.print("  [green][OK][/green] Database connection successful")

        # Enable pgvector extension
        console.print("  Enabling pgvector extension...")
        if not await enable_pgvector():
            console.print(
                "[red]Failed to enable pgvector.[/red]\n"
                "Please check if pgvector is available on your PostgreSQL instance.\n"
                "For Neon, pgvector should be pre-installed."
            )
            return False

        console.print("  [green][OK][/green] pgvector extension enabled")
        return True

    except Exception as e:
        console.print(f"[red]Database validation failed: {e}[/red]")
        return False


async def check_documents() -> bool:
    """Check if documents exist, generate if needed.

    Returns:
        True if documents are ready, False otherwise.
    """
    docs_path = Path("docs")

    # Check if docs directory has content
    if docs_path.exists():
        md_files = list(docs_path.glob("**/*.md"))
        if md_files:
            console.print(f"  [green][OK][/green] Found {len(md_files)} documents in docs/")
            return True

    console.print("[yellow]No documents found in docs/[/yellow]")

    if Confirm.ask("Generate mock documents?", default=True):
        console.print()
        await generate_documents()
        return True
    else:
        console.print("[yellow]Skipping document generation.[/yellow]")
        return False


async def run_setup():
    """Run the complete setup process.

    This function:
    1. Checks/creates .env file
    2. Validates database connection
    3. Creates database schema
    4. Generates mock documents (if needed)
    5. Runs document ingestion
    """
    console.print(Panel(
        "[bold blue]Hierarchical RAG Workshop Setup[/bold blue]\n\n"
        "This will:\n"
        "  1. Validate environment configuration\n"
        "  2. Set up the database schema\n"
        "  3. Generate mock documents (if needed)\n"
        "  4. Ingest documents into the knowledge base",
        style="blue"
    ))
    console.print()

    # Step 1: Check environment
    console.print("[bold]Step 1: Environment Setup[/bold]")
    if not await check_env_file():
        return

    try:
        settings = load_settings()
        console.print("  [green][OK][/green] Environment loaded successfully")
    except Exception as e:
        console.print(f"[red]Failed to load settings: {e}[/red]")
        return

    # Step 2: Validate database
    console.print("\n[bold]Step 2: Database Validation[/bold]")
    if not await validate_database():
        return

    # Step 3: Create schema
    console.print("\n[bold]Step 3: Database Schema[/bold]")
    try:
        pool = await get_pool()
        await create_schema(pool)
        console.print("  [green][OK][/green] Schema created/verified")
    except Exception as e:
        console.print(f"[red]Failed to create schema: {e}[/red]")
        return

    # Step 4: Check/generate documents
    console.print("\n[bold]Step 4: Document Generation[/bold]")
    if not await check_documents():
        console.print("[yellow]No documents to ingest.[/yellow]")
        return

    # Step 5: Run ingestion
    console.print("\n[bold]Step 5: Document Ingestion[/bold]")
    try:
        results = await run_ingestion()

        # Print summary
        total_docs = len(results)
        total_chunks = sum(r.chunks_created for r in results)
        total_errors = sum(len(r.errors) for r in results)

        console.print(Panel(
            f"[bold green]Setup Complete![/bold green]\n\n"
            f"Documents ingested: {total_docs}\n"
            f"Total chunks created: {total_chunks}\n"
            f"Errors: {total_errors}\n\n"
            "[dim]Run the CLI with: uv run python -m src.cli[/dim]",
            style="green"
        ))

    except Exception as e:
        console.print(f"[red]Ingestion failed: {e}[/red]")
        import traceback
        traceback.print_exc()

    finally:
        await close_pool()


async def main():
    """Entry point for ingestion."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    await run_setup()


if __name__ == "__main__":
    asyncio.run(main())
