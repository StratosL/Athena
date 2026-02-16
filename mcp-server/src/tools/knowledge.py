"""Knowledge write-back MCP tools — persist conversation context to Elasticsearch.

- save_conversation_summary: index conversation summaries for long-term memory
"""

import json
import logging
from datetime import UTC, datetime

from src.server import knowledge_store, mcp, vault_manager

logger = logging.getLogger(__name__)


def _parse_csv(value: str) -> list[str]:
    """Parse a comma-separated string into a list of stripped non-empty strings."""
    return [t.strip() for t in value.split(",") if t.strip()]


def _append_to_daily_note(summary: str, topics: list[str]) -> str | None:
    """Append a conversation summary block to today's daily note.

    Creates the daily note if it doesn't exist. Returns the note path on success,
    or None if the write fails (non-fatal).
    """
    now = datetime.now(UTC)
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    note_path = f"Daily Notes/{date_str}.md"

    topic_str = ", ".join(topics) if topics else "general"
    block = f"## Conversation Summary ({time_str} UTC)\n\n**Topics:** {topic_str}\n\n{summary}"

    try:
        vault_manager.append_to_note(note_path, block)
        return note_path
    except FileNotFoundError:
        # Daily note doesn't exist yet — create it
        weekday_name = now.strftime("%A")
        month_name = now.strftime("%B")
        day = now.day
        year = now.year
        header = f"# {weekday_name}, {month_name} {day}, {year}"
        content = f"{header}\n\n{block}"
        try:
            vault_manager.write_note(
                note_path,
                content,
                tags=["daily", "journal"],
            )
            return note_path
        except Exception:
            logger.warning("Failed to create daily note: %s", note_path, exc_info=True)
            return None
    except Exception:
        logger.warning("Failed to append to daily note: %s", note_path, exc_info=True)
        return None


@mcp.tool()
async def save_conversation_summary(
    summary: str,
    topics: str,
    extracted_tasks: str = "",
    task_ids_created: str = "",
) -> str:
    """Save a conversation summary to Elasticsearch for future recall.

    Call this after productive conversations to preserve context for future sessions.

    Args:
        summary: A concise summary of the conversation and key decisions.
        topics: Comma-separated topic keywords (e.g. "api-refactoring, task-planning").
        extracted_tasks: Comma-separated task descriptions that were identified.
        task_ids_created: Comma-separated Artemis task IDs that were created.
    """
    topic_list = _parse_csv(topics)
    result: dict = {}

    # Write to Elasticsearch
    if knowledge_store is None:
        result["es_error"] = "Elasticsearch not configured. Set ELASTIC_URL and ELASTIC_API_KEY."
    else:
        try:
            task_list = _parse_csv(extracted_tasks) if extracted_tasks else None
            id_list = _parse_csv(task_ids_created) if task_ids_created else None

            doc_id = await knowledge_store.save_conversation(
                summary=summary,
                topics=topic_list,
                extracted_tasks=task_list,
                task_ids_created=id_list,
            )
            result["es_document_id"] = doc_id
        except Exception as e:
            result["es_error"] = f"Failed to save to Elasticsearch: {e}"

    # Append to daily note
    daily_note_path = _append_to_daily_note(summary, topic_list)
    if daily_note_path:
        result["daily_note"] = daily_note_path

    result["success"] = "es_document_id" in result or "daily_note" in result
    return json.dumps(result)
