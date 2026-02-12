"""Interactive CLI with streaming and tool call visibility.

Reference: examples/cli.py - Adapted for hierarchical RAG.

This module provides:
- Real-time streaming of agent responses
- Tool call visibility during execution
- Message history management
- Setup and document generation modes
"""

import asyncio
import argparse
import logging
from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from dotenv import load_dotenv

from pydantic_ai import Agent
from pydantic_ai.messages import PartDeltaEvent, PartStartEvent, TextPartDelta

from .agents import get_rag_agent, AgentDependencies
from .settings import load_settings

# Load environment variables
load_dotenv(override=True)

console = Console()
logger = logging.getLogger(__name__)


async def stream_agent_interaction(
    user_input: str,
    message_history: List,
    deps: AgentDependencies
) -> tuple[str, List]:
    """Stream agent interaction with real-time tool call display.

    Reference: examples/cli.py:31-164

    Args:
        user_input: The user's input text.
        message_history: List of previous messages.
        deps: Agent dependencies.

    Returns:
        Tuple of (response_text, new_messages).
    """
    response_text = ""

    try:
        # Get the agent instance
        agent = get_rag_agent()

        # Stream the agent execution
        # Reference: examples/cli.py:66-70
        async with agent.iter(
            user_input,
            deps=deps,
            message_history=message_history
        ) as run:

            async for node in run:
                # Handle model request node - stream text
                # Reference: examples/cli.py:79-101
                if Agent.is_model_request_node(node):
                    console.print("[bold blue]Assistant:[/bold blue] ", end="")

                    async with node.stream(run.ctx) as request_stream:
                        async for event in request_stream:
                            # Handle text part start events
                            if isinstance(event, PartStartEvent) and event.part.part_kind == 'text':
                                if event.part.content:
                                    console.print(event.part.content, end="")
                                    response_text += event.part.content

                            # Handle text delta events for streaming
                            elif isinstance(event, PartDeltaEvent) and isinstance(event.delta, TextPartDelta):
                                if event.delta.content_delta:
                                    console.print(event.delta.content_delta, end="")
                                    response_text += event.delta.content_delta

                    console.print()  # New line after streaming

                # Handle tool calls
                # Reference: examples/cli.py:104-151
                elif Agent.is_call_tools_node(node):
                    async with node.stream(run.ctx) as tool_stream:
                        async for event in tool_stream:
                            event_type = type(event).__name__

                            if event_type == "FunctionToolCallEvent":
                                tool_name = "Unknown"
                                if hasattr(event, 'part') and hasattr(event.part, 'tool_name'):
                                    tool_name = event.part.tool_name

                                console.print(f"  [cyan][Tool] Calling:[/cyan] [bold]{tool_name}[/bold]")

                                # Show arguments for search tools
                                if hasattr(event.part, 'args') and isinstance(event.part.args, dict):
                                    args = event.part.args
                                    if 'query' in args:
                                        console.print(f"    [dim]Query:[/dim] {args['query']}")
                                    if 'category_ids' in args and args['category_ids']:
                                        console.print(f"    [dim]Categories:[/dim] {args['category_ids']}")
                                    if 'chunk_id' in args:
                                        console.print(f"    [dim]Chunk ID:[/dim] {args['chunk_id']}")
                                    if 'document_id' in args:
                                        console.print(f"    [dim]Document ID:[/dim] {args['document_id']}")

                            elif event_type == "FunctionToolResultEvent":
                                console.print(f"  [green][OK] Tool completed[/green]")

        # Get new messages for history
        new_messages = run.result.new_messages()
        return (response_text.strip(), new_messages)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        return ("", [])


def display_welcome():
    """Display welcome message with configuration info.

    Reference: examples/cli.py:167-180
    """
    try:
        settings = load_settings()
        model_info = f"[dim]LLM: {settings.llm_model} (via OpenRouter)[/dim]"
    except Exception:
        model_info = "[dim]LLM: Not configured[/dim]"

    welcome = Panel(
        "[bold blue]Hierarchical RAG Workshop[/bold blue]\n\n"
        "[green]Enterprise IT Knowledge Base with Categorical + Structural Hierarchy[/green]\n"
        f"{model_info}\n\n"
        "[dim]Commands: 'exit' to quit, 'info' for config, 'clear' to reset[/dim]",
        style="blue",
        padding=(1, 2)
    )
    console.print(welcome)
    console.print()


async def run_interactive_chat():
    """Main conversation loop.

    Reference: examples/cli.py:183-256
    """
    display_welcome()

    # Initialize dependencies
    deps = AgentDependencies()
    await deps.initialize()

    console.print("[bold green][OK][/bold green] Knowledge base connected\n")

    message_history = []

    try:
        while True:
            try:
                user_input = Prompt.ask("[bold green]You").strip()

                # Handle special commands
                if user_input.lower() in ['exit', 'quit', 'q']:
                    console.print("\n[yellow] Goodbye![/yellow]")
                    break

                if user_input.lower() == 'info':
                    settings = load_settings()
                    console.print(Panel(
                        f"[cyan]LLM Model:[/cyan] {settings.llm_model}\n"
                        f"[cyan]Embedding Model:[/cyan] {settings.embedding_model}\n"
                        f"[cyan]Database:[/cyan] {settings.database_url[:50]}...",
                        title="Configuration",
                        border_style="magenta"
                    ))
                    continue

                if user_input.lower() == 'clear':
                    console.clear()
                    display_welcome()
                    message_history = []
                    continue

                if not user_input:
                    continue

                # Stream the interaction
                response, new_messages = await stream_agent_interaction(
                    user_input, message_history, deps
                )
                message_history.extend(new_messages)
                console.print()

            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' to quit[/yellow]")
                continue

    finally:
        await deps.cleanup()
        console.print("\n[dim]Session ended.[/dim]")


async def run_single_query(query: str) -> None:
    """Run a single non-interactive query and print the result.

    Args:
        query: The question to ask the agent.
    """
    deps = AgentDependencies()
    await deps.initialize()
    console.print("[bold green][OK][/bold green] Knowledge base connected\n")

    try:
        response, _ = await stream_agent_interaction(query, [], deps)
        if not response:
            console.print("[yellow]No response received.[/yellow]")
    finally:
        await deps.cleanup()


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Hierarchical RAG Workshop CLI")
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Initialize database and ingest documents"
    )
    parser.add_argument(
        "--generate-docs",
        action="store_true",
        help="Generate mock documents"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Single-shot non-interactive query"
    )
    parser.add_argument(
        "--eval",
        action="store_true",
        help="Run full evaluation of test_questions.md"
    )
    parser.add_argument(
        "--eval-output",
        type=str,
        default=None,
        help="JSON output path for eval results (default: eval_results_<timestamp>.json)"
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Suppress noisy HTTP client loggers (httpx/httpcore log every POST request at INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)

    if args.generate_docs:
        from .generate_docs import generate_documents
        await generate_documents()
    elif args.setup:
        from .ingest import run_setup
        await run_setup()
    elif args.eval:
        from .eval import run_evaluation
        await run_evaluation(output_path=args.eval_output)
    elif args.query:
        await run_single_query(args.query)
    else:
        await run_interactive_chat()


if __name__ == "__main__":
    asyncio.run(main())
