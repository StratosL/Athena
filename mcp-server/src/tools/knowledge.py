"""Knowledge write-back MCP tools — persist conversation context to Elasticsearch.

- save_conversation_summary: index conversation summaries for long-term memory
"""

import json
import logging

from src.server import knowledge_store, mcp

logger = logging.getLogger(__name__)


def _parse_csv(value: str) -> list[str]:
    """Parse a comma-separated string into a list of stripped non-empty strings."""
    return [t.strip() for t in value.split(",") if t.strip()]


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
    if knowledge_store is None:
        return json.dumps(
            {"error": "Elasticsearch not configured. Set ELASTIC_URL and ELASTIC_API_KEY."}
        )

    try:
        topic_list = _parse_csv(topics)
        task_list = _parse_csv(extracted_tasks) if extracted_tasks else None
        id_list = _parse_csv(task_ids_created) if task_ids_created else None

        doc_id = await knowledge_store.save_conversation(
            summary=summary,
            topics=topic_list,
            extracted_tasks=task_list,
            task_ids_created=id_list,
        )
        return json.dumps({"success": True, "document_id": doc_id})
    except Exception as e:
        return json.dumps({"error": f"Failed to save conversation: {e}"})
