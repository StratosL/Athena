"""Phase 2b: Create Elasticsearch indices and index the sample vault."""

import shutil
import subprocess
from pathlib import Path

import httpx
from rich.console import Console

from .config import SetupConfig

console = Console()

INDEXER_DIR = str(Path(__file__).parent.parent / "indexer")


def _check_uv() -> bool:
    """Check that uv is installed."""
    if shutil.which("uv"):
        return True
    console.print("  [red]\u2717[/] uv not found. Install from https://docs.astral.sh/uv/")
    return False


def _run_cmd(args: list[str], label: str) -> bool:
    """Run a subprocess command with output capture."""
    try:
        result = subprocess.run(
            args,
            cwd=INDEXER_DIR,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            console.print(f"  [green]\u2192[/] {label}")
            return True
        console.print(f"  [red]\u2717[/] {label}")
        if result.stderr:
            for line in result.stderr.strip().splitlines()[:5]:
                console.print(f"    {line}")
        return False
    except subprocess.TimeoutExpired:
        console.print(f"  [red]\u2717[/] {label} (timed out after 120s)")
        return False
    except Exception as e:
        console.print(f"  [red]\u2717[/] {label}: {e}")
        return False


def _verify_index(cfg: SetupConfig) -> int:
    """Check note count in the athena-notes index. Returns count or -1."""
    try:
        r = httpx.get(
            f"{cfg.elastic_url}/{cfg.notes_index}/_count",
            headers={"Authorization": f"ApiKey {cfg.elastic_api_key}"},
            timeout=10,
        )
        if r.status_code == 200:
            return r.json().get("count", 0)
    except Exception:
        pass
    return -1


def run(cfg: SetupConfig) -> bool:
    """Create ES indices and index the vault. Returns True on success."""
    console.print("\n  [bold][2b] Elasticsearch indices...[/]")

    if not _check_uv():
        return False

    # Install indexer dependencies
    if not _run_cmd(["uv", "sync"], "Installed indexer dependencies"):
        return False

    # Create indices
    if not _run_cmd(["uv", "run", "athena-index", "setup-indices"], "Indices created"):
        return False

    # Index the vault
    if not _run_cmd(["uv", "run", "athena-index", "index"], "Vault indexed"):
        return False

    # Verify
    count = _verify_index(cfg)
    if count > 0:
        console.print(f"  [green]\u2192[/] {cfg.notes_index}: {count} notes indexed")
        console.print(f"  [green]\u2192[/] {cfg.conversations_index} created")
        return True
    elif count == 0:
        console.print(f"  [yellow]\u26a0[/] {cfg.notes_index} exists but has 0 documents")
        return True
    else:
        console.print(f"  [red]\u2717[/] Could not verify {cfg.notes_index} index")
        return False
