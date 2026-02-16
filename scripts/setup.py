"""Main setup orchestrator. Runs all phases or individual phases via CLI flags."""

import argparse
import sys

from rich.console import Console

from .config import SetupConfig
from . import validate_env, setup_supabase, setup_elasticsearch, setup_agent_builder, verify

console = Console()

PHASES = {
    "validate": "Phase 1: Validate environment",
    "supabase": "Phase 2a: Supabase database",
    "elasticsearch": "Phase 2b: Elasticsearch indices",
    "agent-builder": "Phase 2c: Agent Builder (Kibana)",
    "verify": "Phase 3: Verification",
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Athena setup automation — configure all services from .env"
    )
    parser.add_argument(
        "--phase",
        choices=list(PHASES.keys()),
        default=None,
        help="Run a single phase instead of all phases",
    )
    args = parser.parse_args()

    console.print("[bold cyan]Athena Setup[/]")
    console.print("=" * 50)

    cfg = SetupConfig()

    if args.phase:
        _run_phase(args.phase, cfg)
    else:
        _run_all(cfg)


def _run_phase(phase: str, cfg: SetupConfig) -> None:
    """Run a single phase."""
    console.print(f"Running: {PHASES[phase]}")
    ok = _execute_phase(phase, cfg)
    if not ok:
        console.print(f"\n[red]Phase '{phase}' failed.[/]")
        sys.exit(1)
    console.print(f"\n[green]Phase '{phase}' complete.[/]")


def _run_all(cfg: SetupConfig) -> None:
    """Run all phases in sequence."""
    # Phase 1: Validate
    if not validate_env.run(cfg):
        sys.exit(1)

    # Phase 2: Setup services
    console.print("\n[bold]Phase 2/3: Setting up services...[/]")

    if not setup_supabase.run(cfg):
        console.print("\n[red]Supabase setup failed.[/]")
        sys.exit(1)

    if not setup_elasticsearch.run(cfg):
        console.print("\n[red]Elasticsearch setup failed.[/]")
        sys.exit(1)

    if not setup_agent_builder.run(cfg):
        console.print("\n[red]Agent Builder setup failed.[/]")
        sys.exit(1)

    # Phase 3: Verify
    if not verify.run(cfg):
        console.print("\n[yellow]Some checks failed. Review the table above.[/]")
    else:
        console.print("\n[bold green]Setup complete![/]")

    console.print("\nNext steps:")
    console.print("  docker compose --profile tunnel up --build")
    console.print("  Open Kibana \u2192 Agent Builder \u2192 Chat with Athena")


def _execute_phase(phase: str, cfg: SetupConfig) -> bool:
    """Execute a single named phase."""
    if phase == "validate":
        return validate_env.run(cfg)
    elif phase == "supabase":
        return setup_supabase.run(cfg)
    elif phase == "elasticsearch":
        return setup_elasticsearch.run(cfg)
    elif phase == "agent-builder":
        return setup_agent_builder.run(cfg)
    elif phase == "verify":
        return verify.run(cfg)
    return False


if __name__ == "__main__":
    main()
