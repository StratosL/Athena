"""Document ingestion pipeline for Hierarchical RAG Workshop.

Reference: examples/ingestion/ingest.py - Adapted for hierarchical structure.

This module orchestrates the complete ingestion process:
1. Insert categories from taxonomy
2. Process documents with Docling
3. Build chunk hierarchy
4. Generate embeddings
5. Save to PostgreSQL
"""

import os
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime

import asyncpg
from docling.document_converter import DocumentConverter
from rich.console import Console
from rich.progress import Progress, TaskID

from ..settings import load_settings
from ..db.connection import get_pool, close_pool
from ..db.schema import create_schema, clean_tables
from ..db import operations as db_ops
from ..generate_docs import CATEGORY_TAXONOMY, slugify
from .chunker import DoclingHybridChunker, ChunkingConfig
from .embeddings import EmbeddingGenerator
from .hierarchy import build_chunk_hierarchy, extract_document_summary

logger = logging.getLogger(__name__)
console = Console()


@dataclass
class IngestionConfig:
    """Configuration for document ingestion."""

    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_tokens: int = 512
    batch_size: int = 100
    clean_before_ingest: bool = True


@dataclass
class IngestionResult:
    """Result of document ingestion."""

    document_id: int
    title: str
    chunks_created: int
    processing_time_ms: float
    errors: List[str]


class DocumentIngestionPipeline:
    """Pipeline for ingesting documents into hierarchical RAG system.

    Reference: examples/ingestion/ingest.py:59-109
    """

    def __init__(
        self,
        config: IngestionConfig,
        documents_folder: str = "docs"
    ):
        """Initialize ingestion pipeline.

        Args:
            config: Ingestion configuration.
            documents_folder: Folder containing documents.
        """
        self.config = config
        self.documents_folder = documents_folder

        # Initialize components
        self.chunker_config = ChunkingConfig(
            max_tokens=config.max_tokens,
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap
        )

        self.chunker = DoclingHybridChunker(self.chunker_config)
        self.embedder = EmbeddingGenerator(batch_size=config.batch_size)
        self.doc_converter = DocumentConverter()

        self._pool: Optional[asyncpg.Pool] = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize database connections and schema."""
        if self._initialized:
            return

        logger.info("Initializing ingestion pipeline...")

        # Get database pool
        self._pool = await get_pool()

        # Create schema
        await create_schema(self._pool)

        # Clean if requested
        if self.config.clean_before_ingest:
            await clean_tables(self._pool)

        self._initialized = True
        logger.info("Ingestion pipeline initialized")

    async def close(self) -> None:
        """Close database connections."""
        if self._initialized:
            await close_pool()
            self._initialized = False

    async def ingest_all(
        self,
        progress_callback: Optional[callable] = None
    ) -> List[IngestionResult]:
        """Ingest all documents from the taxonomy.

        Args:
            progress_callback: Optional callback for progress updates.

        Returns:
            List of ingestion results.
        """
        if not self._initialized:
            await self.initialize()

        results = []

        # Step 1: Insert categories
        console.print("\n[bold blue]Step 1: Setting up category hierarchy...[/bold blue]")
        await self._insert_categories()

        # Step 2: Find and process documents
        console.print("\n[bold blue]Step 2: Processing documents...[/bold blue]")
        document_files = self._find_document_files()

        if not document_files:
            console.print(f"[yellow]No documents found in {self.documents_folder}[/yellow]")
            return results

        console.print(f"Found {len(document_files)} documents to process\n")

        with Progress() as progress:
            task = progress.add_task("[cyan]Ingesting documents...", total=len(document_files))

            for i, (file_path, category_slug, subcategory_slug) in enumerate(document_files):
                try:
                    result = await self._ingest_single_document(
                        file_path, category_slug, subcategory_slug
                    )
                    results.append(result)

                    if progress_callback:
                        progress_callback(i + 1, len(document_files))

                except Exception as e:
                    logger.error(f"Failed to process {file_path}: {e}")
                    results.append(IngestionResult(
                        document_id=0,
                        title=os.path.basename(file_path),
                        chunks_created=0,
                        processing_time_ms=0,
                        errors=[str(e)]
                    ))

                progress.advance(task)

        # Log summary
        total_chunks = sum(r.chunks_created for r in results)
        total_errors = sum(len(r.errors) for r in results)

        console.print(f"\n[bold green]Ingestion complete![/bold green]")
        console.print(f"  Documents: {len(results)}")
        console.print(f"  Total chunks: {total_chunks}")
        if total_errors > 0:
            console.print(f"  [yellow]Errors: {total_errors}[/yellow]")

        return results

    async def _insert_categories(self) -> Dict[str, int]:
        """Insert categories from taxonomy.

        Returns:
            Dictionary mapping category slugs to IDs.
        """
        category_ids = {}

        for category, cat_data in CATEGORY_TAXONOMY.items():
            category_slug = slugify(category)

            # Insert root category
            cat_id = await db_ops.insert_category(
                self._pool,
                name=category,
                slug=category_slug,
                parent_id=None,
                description=cat_data["description"],
                level=0
            )
            category_ids[category_slug] = cat_id
            logger.info(f"Inserted category: {category} (id={cat_id})")

            # Insert subcategories
            for subcategory, subcat_data in cat_data["subcategories"].items():
                subcategory_slug = slugify(subcategory)
                full_slug = f"{category_slug}/{subcategory_slug}"

                subcat_id = await db_ops.insert_category(
                    self._pool,
                    name=subcategory,
                    slug=full_slug,
                    parent_id=cat_id,
                    description=subcat_data["description"],
                    level=1
                )
                category_ids[full_slug] = subcat_id
                logger.info(f"  Inserted subcategory: {subcategory} (id={subcat_id})")

        console.print(f"  Created {len(category_ids)} categories")
        return category_ids

    def _find_document_files(self) -> List[tuple]:
        """Find all document files with their category info.

        Returns:
            List of (file_path, category_slug, subcategory_slug) tuples.
        """
        docs_path = Path(self.documents_folder)
        if not docs_path.exists():
            return []

        files = []
        for md_file in docs_path.glob("**/*.md"):
            # Parse category from path: docs/category/subcategory/file.md
            rel_path = md_file.relative_to(docs_path)
            parts = rel_path.parts

            if len(parts) >= 3:
                category_slug = parts[0]
                subcategory_slug = parts[1]
                files.append((str(md_file), category_slug, subcategory_slug))
            else:
                logger.warning(f"Skipping file with unexpected path: {md_file}")

        return files

    async def _ingest_single_document(
        self,
        file_path: str,
        category_slug: str,
        subcategory_slug: str
    ) -> IngestionResult:
        """Ingest a single document.

        Args:
            file_path: Path to the document.
            category_slug: Category slug.
            subcategory_slug: Subcategory slug.

        Returns:
            Ingestion result.
        """
        start_time = datetime.now()
        errors = []

        # Read document
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract title
        title = self._extract_title(content, file_path)
        logger.info(f"Processing: {title}")

        # Get category ID
        full_slug = f"{category_slug}/{subcategory_slug}"
        category = await db_ops.get_category_by_slug(self._pool, full_slug)

        if not category:
            raise ValueError(f"Category not found: {full_slug}")

        category_id = category["id"]

        # Extract document summary
        summary = extract_document_summary(content)

        # Generate summary embedding
        summary_embedding = await self.embedder.generate_embedding(summary)

        # Insert document
        document_id = await db_ops.insert_document(
            self._pool,
            title=title,
            category_id=category_id,
            source_path=file_path,
            summary=summary,
            summary_embedding=summary_embedding,
            metadata={"file_path": file_path, "category_slug": full_slug}
        )

        # Chunk document
        try:
            # Try Docling first
            result = self.doc_converter.convert(file_path)
            chunks = self.chunker.chunk_document(
                docling_doc=result.document,
                title=title,
                source=file_path
            )
        except Exception as e:
            logger.warning(f"Docling failed, using markdown fallback: {e}")
            chunks = self.chunker.chunk_markdown(
                content=content,
                title=title,
                source=file_path
            )

        if not chunks:
            errors.append("No chunks created")
            return IngestionResult(
                document_id=document_id,
                title=title,
                chunks_created=0,
                processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                errors=errors
            )

        # Build hierarchy
        hierarchy = build_chunk_hierarchy(chunks, summary, title)

        # Generate embeddings for all chunks
        all_texts = [node["contextualized_content"] or node["content"] for node in hierarchy]
        all_embeddings = await self.embedder.generate_embeddings_batch(all_texts)

        # Insert chunks with hierarchy
        chunk_id_map = {}  # index -> database ID
        total_chunks = 0

        for idx, (node, embedding) in enumerate(zip(hierarchy, all_embeddings)):
            # Resolve parent ID
            parent_db_id = None
            if node["parent_index"] is not None:
                parent_db_id = chunk_id_map.get(node["parent_index"])

            chunk_db_id = await db_ops.insert_chunk(
                self._pool,
                document_id=document_id,
                parent_chunk_id=parent_db_id,
                content=node["content"],
                content_embedding=embedding,
                chunk_level=node["chunk_level"],
                sequence_number=node["sequence_number"],
                heading_path=node["heading_path"],
                metadata=node["metadata"]
            )

            chunk_id_map[idx] = chunk_db_id
            total_chunks += 1

        processing_time = (datetime.now() - start_time).total_seconds() * 1000

        logger.info(f"  Created {total_chunks} chunks in {processing_time:.1f}ms")

        return IngestionResult(
            document_id=document_id,
            title=title,
            chunks_created=total_chunks,
            processing_time_ms=processing_time,
            errors=errors
        )

    def _extract_title(self, content: str, file_path: str) -> str:
        """Extract title from document content or filename.

        Args:
            content: Document content.
            file_path: File path.

        Returns:
            Document title.
        """
        lines = content.split('\n')
        for line in lines[:10]:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()

        # Fallback to filename
        return os.path.splitext(os.path.basename(file_path))[0].replace('-', ' ').title()


async def run_ingestion(
    documents_folder: str = "docs",
    clean_before_ingest: bool = True
) -> List[IngestionResult]:
    """Run the full ingestion pipeline.

    Args:
        documents_folder: Folder containing documents.
        clean_before_ingest: Whether to clean existing data.

    Returns:
        List of ingestion results.
    """
    config = IngestionConfig(clean_before_ingest=clean_before_ingest)
    pipeline = DocumentIngestionPipeline(config, documents_folder)

    try:
        return await pipeline.ingest_all()
    finally:
        await pipeline.close()
