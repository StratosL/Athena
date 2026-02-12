"""Elasticsearch client for knowledge write-back operations.

Handles indexing conversation summaries into the athena-conversations index.
Note indexing is handled by the indexer/ sub-project, not here.
"""

import logging
from datetime import UTC, datetime

from elasticsearch import AsyncElasticsearch

logger = logging.getLogger(__name__)


class KnowledgeStore:
    """Elasticsearch client for writing conversation summaries."""

    def __init__(self, elastic_url: str, api_key: str, conversations_index: str) -> None:
        self.es = AsyncElasticsearch(hosts=[elastic_url], api_key=api_key)
        self.conversations_index = conversations_index

    async def close(self) -> None:
        """Close the Elasticsearch client."""
        await self.es.close()

    async def save_conversation(
        self,
        summary: str,
        topics: list[str],
        extracted_tasks: list[str] | None = None,
        task_ids_created: list[str] | None = None,
    ) -> str:
        """Index a conversation summary. Returns the document ID."""
        doc = {
            "summary": summary,
            "summary_semantic": summary,  # ELSER embeds at index time
            "topics": topics,
            "extracted_tasks": extracted_tasks or [],
            "task_ids_created": task_ids_created or [],
            "timestamp": datetime.now(UTC).isoformat(),
        }
        result = await self.es.index(index=self.conversations_index, document=doc)
        logger.info("Saved conversation summary: %s", result["_id"])
        return result["_id"]
