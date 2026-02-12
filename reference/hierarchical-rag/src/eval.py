"""Automated evaluation harness for Hierarchical RAG Workshop.

Runs test questions from test_questions.md through the agent, captures tool calls,
scores hierarchical RAG behavior (categorical + structural), and produces a report.

Usage:
    uv run python -m src.cli --eval
    uv run python -m src.cli --eval --eval-output my_results.json
"""

import json
import logging
import re
import time
from datetime import datetime, timezone
from enum import IntEnum
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.messages import PartDeltaEvent, PartStartEvent, TextPartDelta
from pydantic_ai.models.openrouter import OpenRouterModel
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table

from .agents import get_rag_agent, AgentDependencies
from .settings import load_settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------


class QuestionTier(IntEnum):
    """Test question difficulty tier."""
    SINGLE_CATEGORY = 1
    CROSS_DOCUMENT = 2
    CROSS_CATEGORY = 3
    BROAD_ADVERSARIAL = 4


class TestQuestion(BaseModel):
    """A parsed test question from test_questions.md."""
    question_id: int
    tier: QuestionTier
    question_text: str
    expected_behavior: str
    expected_answer: str


class ToolCallRecord(BaseModel):
    """Record of a single tool call made by the agent."""
    tool_name: str
    args: dict[str, Any] = Field(default_factory=dict)


class ToolCallScores(BaseModel):
    """Programmatic scores based on tool call patterns."""
    called_list_categories: bool = False
    used_category_filtering: bool = False
    used_context_expansion: bool = False
    category_identification_score: int = Field(default=0, ge=0, le=3)
    category_filtering_score: int = Field(default=0, ge=0, le=3)
    context_expansion_score: int = Field(default=0, ge=0, le=3)

    @property
    def total(self) -> int:
        """Total programmatic score (max 9)."""
        return (
            self.category_identification_score
            + self.category_filtering_score
            + self.context_expansion_score
        )


class LLMJudgeScores(BaseModel):
    """Scores from the LLM judge."""
    accuracy_score: int = Field(default=0, ge=0, le=4)
    accuracy_reasoning: str = ""
    synthesis_score: int = Field(default=0, ge=0, le=4)
    synthesis_reasoning: str = ""
    citation_score: int = Field(default=0, ge=0, le=2)
    citation_reasoning: str = ""

    @property
    def total(self) -> int:
        """Total judge score (max 10)."""
        return self.accuracy_score + self.synthesis_score + self.citation_score


class JudgeOutput(BaseModel):
    """Structured output model for the LLM judge agent."""
    accuracy_score: int = Field(ge=0, le=4, description="0-4: How accurate are the facts?")
    accuracy_reasoning: str = Field(description="Why this accuracy score?")
    synthesis_score: int = Field(ge=0, le=4, description="0-4: How well does the answer synthesize across documents?")
    synthesis_reasoning: str = Field(description="Why this synthesis score?")
    citation_score: int = Field(ge=0, le=2, description="0-2: Does the answer cite sources?")
    citation_reasoning: str = Field(description="Why this citation score?")


class QuestionResult(BaseModel):
    """Complete result for a single evaluated question."""
    question: TestQuestion
    tool_calls: list[ToolCallRecord] = Field(default_factory=list)
    response_text: str = ""
    tool_call_scores: ToolCallScores = Field(default_factory=ToolCallScores)
    llm_judge_scores: LLMJudgeScores = Field(default_factory=LLMJudgeScores)
    total_score: int = 0
    max_score: int = 19
    error: Optional[str] = None
    duration_seconds: float = 0.0


class TierSummary(BaseModel):
    """Summary statistics for a question tier."""
    tier: int
    tier_name: str
    question_count: int = 0
    avg_score: float = 0.0
    avg_tool_call_score: float = 0.0
    avg_judge_score: float = 0.0
    category_filter_rate: float = 0.0


class EvalReport(BaseModel):
    """Complete evaluation report."""
    timestamp: str
    model: str
    total_questions: int = 0
    total_score: int = 0
    max_possible_score: int = 0
    avg_score: float = 0.0
    pass_rate: float = 0.0
    tier_summaries: list[TierSummary] = Field(default_factory=list)
    question_results: list[QuestionResult] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Test Question Parser
# ---------------------------------------------------------------------------

TIER_NAMES = {
    1: "Single-Category Deep Navigation",
    2: "Cross-Document Within Category",
    3: "Cross-Category Synthesis",
    4: "Broad / Adversarial",
}


def parse_test_questions(file_path: Optional[str] = None) -> list[TestQuestion]:
    """Parse test questions from test_questions.md.

    Args:
        file_path: Path to test_questions.md. Defaults to project root.

    Returns:
        List of parsed TestQuestion objects.

    Raises:
        FileNotFoundError: If the test questions file doesn't exist.
        ValueError: If parsing doesn't find exactly 16 questions.
    """
    if file_path is None:
        file_path = str(Path(__file__).parent.parent / "test_questions.md")

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Test questions file not found: {path}\n"
            f"Expected at project root: test_questions.md"
        )

    content = path.read_text(encoding="utf-8")

    # Parse tiers and questions
    questions: list[TestQuestion] = []
    current_tier: int = 0

    # Split into sections by ## or ### headers
    lines = content.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]

        # Detect tier headers: ## Tier N:
        tier_match = re.match(r"^## Tier (\d+):", line)
        if tier_match:
            current_tier = int(tier_match.group(1))
            i += 1
            continue

        # Detect question headers: ### QN: "..."
        q_match = re.match(r'^### Q(\d+):\s*"(.+?)"', line)
        if q_match:
            question_id = int(q_match.group(1))
            question_text = q_match.group(2)

            # Extract expected behavior (look for **Expected behavior:** line)
            expected_behavior = ""
            expected_answer = ""
            i += 1

            while i < len(lines):
                bline = lines[i]

                if bline.startswith("**Expected behavior:**"):
                    expected_behavior = bline.replace("**Expected behavior:**", "").strip()
                    i += 1
                    continue

                # Extract expected answer from <details> block
                if "<details>" in bline:
                    # Skip to after <summary>...</summary>
                    i += 1
                    while i < len(lines) and "</summary>" not in lines[i]:
                        i += 1
                    i += 1  # skip </summary> line

                    # Collect answer lines until </details>
                    answer_lines: list[str] = []
                    while i < len(lines) and "</details>" not in lines[i]:
                        answer_lines.append(lines[i])
                        i += 1
                    expected_answer = "\n".join(answer_lines).strip()
                    i += 1
                    break

                # If we hit the next question or tier, stop
                if bline.startswith("### Q") or bline.startswith("## Tier") or bline.startswith("## Scoring"):
                    break

                i += 1

            if current_tier > 0:
                questions.append(TestQuestion(
                    question_id=question_id,
                    tier=QuestionTier(current_tier),
                    question_text=question_text,
                    expected_behavior=expected_behavior,
                    expected_answer=expected_answer,
                ))
            continue

        i += 1

    if len(questions) != 16:
        raise ValueError(
            f"Expected 16 test questions, found {len(questions)}. "
            f"Check test_questions.md format."
        )

    logger.info("Parsed %d test questions across %d tiers", len(questions), len(set(q.tier for q in questions)))
    return questions


# ---------------------------------------------------------------------------
# Question Runner
# ---------------------------------------------------------------------------


async def run_question(
    question: TestQuestion,
    deps: AgentDependencies,
    console: Console,
) -> QuestionResult:
    """Run a single question through the agent and capture results.

    Args:
        question: The test question to run.
        deps: Initialized agent dependencies.
        console: Rich console for output.

    Returns:
        QuestionResult with response text and tool call records.
    """
    result = QuestionResult(question=question)
    start_time = time.monotonic()

    try:
        agent = get_rag_agent()
        response_text = ""
        tool_calls: list[ToolCallRecord] = []

        async with agent.iter(
            question.question_text,
            deps=deps,
            message_history=[],  # Fresh context per question
        ) as run:
            async for node in run:
                if Agent.is_model_request_node(node):
                    async with node.stream(run.ctx) as request_stream:
                        async for event in request_stream:
                            if isinstance(event, PartStartEvent) and event.part.part_kind == "text":
                                if event.part.content:
                                    response_text += event.part.content
                            elif isinstance(event, PartDeltaEvent) and isinstance(event.delta, TextPartDelta):
                                if event.delta.content_delta:
                                    response_text += event.delta.content_delta

                elif Agent.is_call_tools_node(node):
                    async with node.stream(run.ctx) as tool_stream:
                        async for event in tool_stream:
                            event_type = type(event).__name__
                            if event_type == "FunctionToolCallEvent":
                                tool_name = "Unknown"
                                if hasattr(event, "part") and hasattr(event.part, "tool_name"):
                                    tool_name = event.part.tool_name

                                args: dict[str, Any] = {}
                                if hasattr(event.part, "args"):
                                    if isinstance(event.part.args, dict):
                                        args = event.part.args
                                    elif isinstance(event.part.args, str):
                                        try:
                                            args = json.loads(event.part.args)
                                        except (json.JSONDecodeError, TypeError):
                                            args = {"raw": event.part.args}

                                tool_calls.append(ToolCallRecord(
                                    tool_name=tool_name,
                                    args=args,
                                ))

        result.response_text = response_text.strip()
        result.tool_calls = tool_calls

    except Exception as e:
        result.error = str(e)
        logger.error("Error running Q%d: %s", question.question_id, e)

    result.duration_seconds = time.monotonic() - start_time
    return result


# ---------------------------------------------------------------------------
# Programmatic Tool Call Scoring
# ---------------------------------------------------------------------------


def score_tool_calls(
    question: TestQuestion,
    tool_calls: list[ToolCallRecord],
) -> ToolCallScores:
    """Score tool call patterns programmatically.

    Args:
        question: The test question for context.
        tool_calls: List of tool calls made by the agent.

    Returns:
        ToolCallScores with individual and aggregate scores.
    """
    scores = ToolCallScores()

    # Check if list_categories was called
    called_list_categories = any(tc.tool_name == "list_categories" for tc in tool_calls)
    scores.called_list_categories = called_list_categories

    # Check if search_knowledge_base used category_ids
    search_calls = [tc for tc in tool_calls if tc.tool_name == "search_knowledge_base"]
    used_category_filtering = any(
        tc.args.get("category_ids") is not None and len(tc.args.get("category_ids", [])) > 0
        for tc in search_calls
    )
    scores.used_category_filtering = used_category_filtering

    # Check for context expansion tools
    context_calls = [
        tc for tc in tool_calls
        if tc.tool_name in ("get_chunk_context", "get_document_overview")
    ]
    scores.used_context_expansion = len(context_calls) > 0

    # --- Category Identification (0-3) ---
    if called_list_categories:
        scores.category_identification_score = 3
    elif used_category_filtering:
        # Somehow knew category IDs without listing - partial credit
        scores.category_identification_score = 1
    else:
        scores.category_identification_score = 0

    # --- Category Filtering (0-3) ---
    # Q14 ("encryption across org") is a special case - broad search is correct
    if question.question_id == 14:
        # Full points whether they filtered or not, since broad search is valid
        if len(search_calls) > 0:
            scores.category_filtering_score = 3
        else:
            scores.category_filtering_score = 0
    else:
        if used_category_filtering:
            scores.category_filtering_score = 3
        elif len(search_calls) > 0:
            # Searched but didn't filter
            scores.category_filtering_score = 1
        else:
            scores.category_filtering_score = 0

    # --- Context Expansion (0-3) ---
    if len(context_calls) >= 2:
        scores.context_expansion_score = 3
    elif len(context_calls) == 1:
        scores.context_expansion_score = 2
    else:
        scores.context_expansion_score = 0

    return scores


# ---------------------------------------------------------------------------
# LLM Judge
# ---------------------------------------------------------------------------

JUDGE_SYSTEM_PROMPT = """You are an expert evaluator for a Retrieval-Augmented Generation (RAG) system.
You will score the agent's response against an expected answer on three dimensions.

Score STRICTLY based on the rubric:

**Accuracy (0-4):**
- 4: All key facts, numbers, and details match the expected answer
- 3: Most facts correct, minor omissions
- 2: Some correct information but notable gaps or errors
- 1: Mostly incorrect or very incomplete
- 0: Completely wrong or empty response

**Cross-Document Synthesis (0-4):**
- 4: Seamlessly integrates information from multiple documents/sources
- 3: References multiple sources with reasonable integration
- 2: Mentions multiple sources but doesn't connect them well
- 1: Only uses information from a single source
- 0: No synthesis attempted or empty response

**Source Citation (0-2):**
- 2: Clearly cites document titles and/or sections
- 1: Vague references to sources
- 0: No source attribution

Be fair but strict. The agent doesn't need to match the expected answer word-for-word,
but should cover the key facts and structure."""


async def score_with_llm_judge(
    question: TestQuestion,
    response_text: str,
    tool_calls: list[ToolCallRecord],
) -> LLMJudgeScores:
    """Score the agent's response using an LLM judge.

    Args:
        question: The test question with expected answer.
        response_text: The agent's actual response.
        tool_calls: Tool calls made (for context).

    Returns:
        LLMJudgeScores with accuracy, synthesis, and citation scores.
    """
    if not response_text.strip():
        return LLMJudgeScores(
            accuracy_score=0,
            accuracy_reasoning="Empty response",
            synthesis_score=0,
            synthesis_reasoning="Empty response",
            citation_score=0,
            citation_reasoning="Empty response",
        )

    try:
        settings = load_settings()
        judge_agent = Agent(
            OpenRouterModel(settings.llm_model),
            output_type=JudgeOutput,
            system_prompt=JUDGE_SYSTEM_PROMPT,
        )

        tool_call_summary = "\n".join(
            f"  - {tc.tool_name}({', '.join(f'{k}={v}' for k, v in tc.args.items())})"
            for tc in tool_calls
        ) or "  (no tool calls)"

        judge_prompt = f"""Evaluate this RAG agent response.

**Question (Tier {question.tier}):** {question.question_text}

**Expected Answer:**
{question.expected_answer}

**Agent's Response:**
{response_text}

**Tool Calls Made:**
{tool_call_summary}

Score the agent's response on accuracy, cross-document synthesis, and source citation."""

        result = await judge_agent.run(judge_prompt)
        judge_output: JudgeOutput = result.output

        return LLMJudgeScores(
            accuracy_score=judge_output.accuracy_score,
            accuracy_reasoning=judge_output.accuracy_reasoning,
            synthesis_score=judge_output.synthesis_score,
            synthesis_reasoning=judge_output.synthesis_reasoning,
            citation_score=judge_output.citation_score,
            citation_reasoning=judge_output.citation_reasoning,
        )

    except Exception as e:
        logger.warning("LLM judge failed for Q%d: %s", question.question_id, e)
        return LLMJudgeScores(
            accuracy_score=0,
            accuracy_reasoning=f"Judge error: {e}",
            synthesis_score=0,
            synthesis_reasoning=f"Judge error: {e}",
            citation_score=0,
            citation_reasoning=f"Judge error: {e}",
        )


# ---------------------------------------------------------------------------
# Report Display
# ---------------------------------------------------------------------------


def _score_color(score: int, max_score: int) -> str:
    """Get Rich color for a score value."""
    ratio = score / max_score if max_score > 0 else 0
    if ratio >= 0.75:
        return "green"
    elif ratio >= 0.5:
        return "yellow"
    else:
        return "red"


def display_eval_report(report: EvalReport, console: Console) -> None:
    """Display the evaluation report with Rich formatting.

    Args:
        report: The completed evaluation report.
        console: Rich console for output.
    """
    # --- Summary Panel ---
    score_color = _score_color(report.total_score, report.max_possible_score)
    summary_text = (
        f"[bold]Model:[/bold] {report.model}\n"
        f"[bold]Questions:[/bold] {report.total_questions}\n"
        f"[bold]Overall Score:[/bold] [{score_color}]{report.total_score}/{report.max_possible_score}[/{score_color}] "
        f"({report.avg_score:.1f} avg per question)\n"
        f"[bold]Pass Rate:[/bold] [{score_color}]{report.pass_rate:.0%}[/{score_color}] "
        f"(questions scoring >= 50%)"
    )
    console.print(Panel(summary_text, title="Evaluation Summary", border_style="blue"))
    console.print()

    # --- Tier Summary Table ---
    tier_table = Table(title="Tier Summary", show_lines=True)
    tier_table.add_column("Tier", style="bold")
    tier_table.add_column("Questions", justify="center")
    tier_table.add_column("Avg Score", justify="center")
    tier_table.add_column("Avg Tool", justify="center")
    tier_table.add_column("Avg Judge", justify="center")
    tier_table.add_column("Cat Filter %", justify="center")

    for ts in report.tier_summaries:
        score_c = _score_color(int(ts.avg_score), 19)
        filter_c = "green" if ts.category_filter_rate >= 0.5 else "yellow" if ts.category_filter_rate > 0 else "red"
        tier_table.add_row(
            f"T{ts.tier}: {ts.tier_name}",
            str(ts.question_count),
            f"[{score_c}]{ts.avg_score:.1f}/19[/{score_c}]",
            f"{ts.avg_tool_call_score:.1f}/9",
            f"{ts.avg_judge_score:.1f}/10",
            f"[{filter_c}]{ts.category_filter_rate:.0%}[/{filter_c}]",
        )

    console.print(tier_table)
    console.print()

    # --- Detailed Results Table ---
    detail_table = Table(title="Detailed Question Results", show_lines=True)
    detail_table.add_column("Q#", style="bold", justify="center", width=4)
    detail_table.add_column("T", justify="center", width=3)
    detail_table.add_column("Cat ID", justify="center", width=6)
    detail_table.add_column("Cat Flt", justify="center", width=7)
    detail_table.add_column("Ctx Exp", justify="center", width=7)
    detail_table.add_column("Accuracy", justify="center", width=8)
    detail_table.add_column("Synth", justify="center", width=6)
    detail_table.add_column("Cite", justify="center", width=5)
    detail_table.add_column("Total", justify="center", width=7)
    detail_table.add_column("Time", justify="right", width=6)
    detail_table.add_column("Status", justify="center", width=7)

    for qr in report.question_results:
        tc = qr.tool_call_scores
        jd = qr.llm_judge_scores
        total_c = _score_color(qr.total_score, qr.max_score)
        status = "[red]ERROR[/red]" if qr.error else f"[{total_c}]OK[/{total_c}]"

        detail_table.add_row(
            str(qr.question.question_id),
            str(qr.question.tier),
            f"{tc.category_identification_score}/3",
            f"{tc.category_filtering_score}/3",
            f"{tc.context_expansion_score}/3",
            f"{jd.accuracy_score}/4",
            f"{jd.synthesis_score}/4",
            f"{jd.citation_score}/2",
            f"[{total_c}]{qr.total_score}/19[/{total_c}]",
            f"{qr.duration_seconds:.1f}s",
            status,
        )

    console.print(detail_table)
    console.print()

    # --- Tool Call Analysis Panel ---
    total_q = len(report.question_results)
    if total_q > 0:
        valid_results = [qr for qr in report.question_results if qr.error is None]
        valid_count = len(valid_results)

        if valid_count > 0:
            list_cat_rate = sum(1 for qr in valid_results if qr.tool_call_scores.called_list_categories) / valid_count
            cat_filter_rate = sum(1 for qr in valid_results if qr.tool_call_scores.used_category_filtering) / valid_count
            ctx_expand_rate = sum(1 for qr in valid_results if qr.tool_call_scores.used_context_expansion) / valid_count

            all_tool_calls = [tc for qr in valid_results for tc in qr.tool_calls]
            tool_counts: dict[str, int] = {}
            for tc in all_tool_calls:
                tool_counts[tc.tool_name] = tool_counts.get(tc.tool_name, 0) + 1

            tool_lines = "\n".join(
                f"  {name}: {count} calls"
                for name, count in sorted(tool_counts.items(), key=lambda x: -x[1])
            )

            analysis_text = (
                f"[bold]Tool Usage Rates (across {valid_count} successful questions):[/bold]\n"
                f"  list_categories called: {list_cat_rate:.0%}\n"
                f"  category_ids filtering used: {cat_filter_rate:.0%}\n"
                f"  Context expansion used: {ctx_expand_rate:.0%}\n\n"
                f"[bold]Total Tool Calls by Type:[/bold]\n{tool_lines}"
            )
            console.print(Panel(analysis_text, title="Tool Call Analysis", border_style="cyan"))
            console.print()


# ---------------------------------------------------------------------------
# Results Persistence
# ---------------------------------------------------------------------------


def save_eval_results(report: EvalReport, output_path: Optional[str] = None) -> str:
    """Save evaluation results to JSON.

    Args:
        report: The completed evaluation report.
        output_path: Optional output file path. Defaults to timestamped filename.

    Returns:
        The path the results were saved to.
    """
    if output_path is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output_path = f"eval_results_{timestamp}.json"

    path = Path(output_path)
    path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    return str(path)


# ---------------------------------------------------------------------------
# Main Orchestrator
# ---------------------------------------------------------------------------


async def run_evaluation(output_path: Optional[str] = None) -> None:
    """Run the full evaluation harness.

    Args:
        output_path: Optional path for JSON output file.
    """
    console = Console()

    console.print(Panel(
        "[bold blue]Hierarchical RAG Evaluation Harness[/bold blue]\n\n"
        "Running all test questions and scoring agent behavior.",
        style="blue",
        padding=(1, 2),
    ))
    console.print()

    # 1. Parse test questions
    console.print("[bold]Parsing test questions...[/bold]")
    try:
        questions = parse_test_questions()
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]Error: {e}[/red]")
        return

    console.print(f"[green]Found {len(questions)} questions across {len(set(q.tier for q in questions))} tiers[/green]")
    console.print()

    # 2. Initialize dependencies
    settings = load_settings()
    console.print(f"[dim]Model: {settings.llm_model}[/dim]")

    deps = AgentDependencies()
    await deps.initialize()
    console.print("[bold green][OK][/bold green] Dependencies initialized\n")

    # 3. Run each question
    question_results: list[QuestionResult] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Evaluating questions...", total=len(questions))

        for question in questions:
            progress.update(task, description=f"Q{question.question_id}: {question.question_text[:50]}...")

            # Run the question
            qr = await run_question(question, deps, console)

            # Score tool calls
            qr.tool_call_scores = score_tool_calls(question, qr.tool_calls)

            # Score with LLM judge (skip if agent errored)
            if qr.error is None and qr.response_text:
                qr.llm_judge_scores = await score_with_llm_judge(
                    question, qr.response_text, qr.tool_calls
                )

            # Compute total score
            qr.total_score = qr.tool_call_scores.total + qr.llm_judge_scores.total

            question_results.append(qr)
            progress.advance(task)

            logger.info(
                "Q%d: score=%d/%d, tools=%d, duration=%.1fs%s",
                question.question_id,
                qr.total_score,
                qr.max_score,
                len(qr.tool_calls),
                qr.duration_seconds,
                f" ERROR: {qr.error}" if qr.error else "",
            )

    console.print()

    # 4. Compute tier summaries
    tier_summaries: list[TierSummary] = []
    for tier_val in sorted(set(q.tier for q in questions)):
        tier_results = [qr for qr in question_results if qr.question.tier == tier_val]
        valid_results = [qr for qr in tier_results if qr.error is None]
        count = len(tier_results)
        valid_count = len(valid_results)

        tier_summaries.append(TierSummary(
            tier=tier_val,
            tier_name=TIER_NAMES.get(tier_val, "Unknown"),
            question_count=count,
            avg_score=sum(qr.total_score for qr in tier_results) / count if count > 0 else 0,
            avg_tool_call_score=sum(qr.tool_call_scores.total for qr in tier_results) / count if count > 0 else 0,
            avg_judge_score=sum(qr.llm_judge_scores.total for qr in tier_results) / count if count > 0 else 0,
            category_filter_rate=(
                sum(1 for qr in valid_results if qr.tool_call_scores.used_category_filtering) / valid_count
                if valid_count > 0 else 0
            ),
        ))

    # 5. Build report
    total_score = sum(qr.total_score for qr in question_results)
    max_possible = len(question_results) * 19
    passing = sum(1 for qr in question_results if qr.total_score >= (qr.max_score * 0.5))

    report = EvalReport(
        timestamp=datetime.now(timezone.utc).isoformat(),
        model=settings.llm_model,
        total_questions=len(question_results),
        total_score=total_score,
        max_possible_score=max_possible,
        avg_score=total_score / len(question_results) if question_results else 0,
        pass_rate=passing / len(question_results) if question_results else 0,
        tier_summaries=tier_summaries,
        question_results=question_results,
    )

    # 6. Display and save
    display_eval_report(report, console)

    saved_path = save_eval_results(report, output_path)
    console.print(f"[bold green]Results saved to:[/bold green] {saved_path}")
    console.print()

    # 7. Cleanup
    await deps.cleanup()
    console.print("[dim]Evaluation complete.[/dim]")
