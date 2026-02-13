"""Bulk indexing of parsed Obsidian notes into Elasticsearch."""

import logging
from dataclasses import dataclass, field
from pathlib import Path

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from src.config import IndexerSettings
from src.mappings import CONVERSATIONS_INDEX_MAPPING, NOTES_INDEX_MAPPING
from src.parser import ParsedNote, parse_note, parse_vault

logger = logging.getLogger(__name__)


@dataclass
class IndexResult:
    """Summary of a bulk indexing run."""

    total_files: int = 0
    indexed: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def failed(self) -> int:
        return len(self.errors)


class VaultIndexer:
    """Indexes Obsidian vault notes into Elasticsearch with checksum-based deduplication."""

    def __init__(self, settings: IndexerSettings) -> None:
        self.settings = settings
        self.es = self._create_es_client()
        self.vault_root = Path(settings.vault_path).resolve()

    def _create_es_client(self) -> AsyncElasticsearch:
        return AsyncElasticsearch(
            hosts=[self.settings.elastic_url],
            api_key=self.settings.elastic_api_key,
        )

    async def close(self) -> None:
        """Close the Elasticsearch client connection."""
        await self.es.close()

    async def setup_indices(self) -> dict[str, bool]:
        """Create Elasticsearch indices if they don't already exist.

        Returns:
            Dict mapping index name to whether it was newly created.
        """
        results: dict[str, bool] = {}
        index_configs = {
            self.settings.notes_index: NOTES_INDEX_MAPPING,
            self.settings.conversations_index: CONVERSATIONS_INDEX_MAPPING,
        }

        for index_name, mapping in index_configs.items():
            exists = await self.es.indices.exists(index=index_name)
            if exists:
                logger.info("Index '%s' already exists", index_name)
                results[index_name] = False
            else:
                await self.es.indices.create(index=index_name, body=mapping)
                logger.info("Created index '%s'", index_name)
                results[index_name] = True

        return results

    async def _fetch_existing_checksums(self) -> dict[str, str]:
        """Fetch all (vault_relative_path, checksum) pairs from the notes index.

        Uses the scroll API to handle indices larger than 1000 docs.
        """
        checksums: dict[str, str] = {}

        exists = await self.es.indices.exists(index=self.settings.notes_index)
        if not exists:
            return checksums

        resp = await self.es.search(
            index=self.settings.notes_index,
            body={"query": {"match_all": {}}, "_source": ["vault_relative_path", "checksum"]},
            scroll="2m",
            size=1000,
        )

        scroll_id = resp.get("_scroll_id")
        hits = resp["hits"]["hits"]

        while hits:
            for hit in hits:
                src = hit["_source"]
                checksums[src["vault_relative_path"]] = src["checksum"]

            if scroll_id is None:
                break
            resp = await self.es.scroll(scroll_id=scroll_id, scroll="2m")
            scroll_id = resp.get("_scroll_id")
            hits = resp["hits"]["hits"]

        if scroll_id:
            await self.es.clear_scroll(scroll_id=scroll_id)

        return checksums

    async def index_vault(self) -> IndexResult:
        """Parse and bulk-index the entire vault, skipping unchanged files.

        Returns:
            IndexResult with counts and any errors.
        """
        result = IndexResult()
        parsed = parse_vault(self.vault_root)
        result.total_files = len(parsed)

        # Collect parse errors
        notes: list[ParsedNote] = []
        for note, error in parsed:
            if error:
                result.errors.append(error)
            elif note:
                notes.append(note)

        if not notes:
            logger.info("No notes to index")
            return result

        # Fetch existing checksums for dedup
        existing_checksums = await self._fetch_existing_checksums()

        # Build bulk actions, skipping unchanged files
        actions: list[dict] = []
        for note in notes:
            existing = existing_checksums.get(note.vault_relative_path)
            if existing == note.checksum:
                result.skipped += 1
                continue
            actions.append(
                {
                    "_index": self.settings.notes_index,
                    "_id": note.es_doc_id(),
                    "_source": note.to_es_document(),
                }
            )

        if not actions:
            logger.info("All %d notes unchanged, nothing to index", len(notes))
            return result

        # Bulk index
        success_count, error_items = await async_bulk(self.es, actions, raise_on_error=False)
        result.indexed = success_count

        if isinstance(error_items, list):
            for err in error_items:
                result.errors.append(str(err))

        logger.info(
            "Indexed %d notes (%d skipped, %d errors)",
            result.indexed,
            result.skipped,
            result.failed,
        )
        return result

    async def index_single_note(self, file_path: Path) -> bool:
        """Parse and index a single note (used by watcher).

        Returns:
            True if indexed successfully, False otherwise.
        """
        try:
            note = parse_note(file_path, self.vault_root)
            await self.es.index(
                index=self.settings.notes_index,
                id=note.es_doc_id(),
                document=note.to_es_document(),
            )
            logger.info("Indexed note: %s", note.vault_relative_path)
            return True
        except Exception as e:
            logger.error("Failed to index %s: %s", file_path, e)
            return False

    async def delete_note(self, file_path: Path) -> bool:
        """Delete a note from ES by its vault-relative path (used by watcher).

        Returns:
            True if deleted successfully, False otherwise.
        """
        try:
            file_path = file_path.resolve()
            vault_relative_path = str(file_path.relative_to(self.vault_root))
            import hashlib

            doc_id = hashlib.sha256(vault_relative_path.encode()).hexdigest()
            await self.es.delete(
                index=self.settings.notes_index,
                id=doc_id,
                ignore=[404],  # type: ignore[call-arg]  # ES runtime param not in type stubs
            )
            logger.info("Deleted note: %s", vault_relative_path)
            return True
        except Exception as e:
            logger.error("Failed to delete %s: %s", file_path, e)
            return False
