"""Docling HybridChunker for hierarchical RAG.

Reference: examples/ingestion/chunker.py - Adapted with heading path extraction.

This module uses Docling's built-in HybridChunker which combines:
- Token-aware chunking (uses actual tokenizer)
- Document structure preservation (headings, sections, tables)
- Semantic boundary respect (paragraphs, code blocks)
- Contextualized output (chunks include heading hierarchy)
"""

import re
import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from transformers import AutoTokenizer
from docling.chunking import HybridChunker
from docling_core.types.doc import DoclingDocument

logger = logging.getLogger(__name__)


@dataclass
class ChunkingConfig:
    """Configuration for DoclingHybridChunker.

    Reference: examples/ingestion/chunker.py:33-48
    """

    max_tokens: int = 512  # Maximum tokens for embedding models
    chunk_size: int = 1000  # Fallback character size
    chunk_overlap: int = 200  # Fallback overlap
    min_chunk_size: int = 100  # Minimum chunk size

    def __post_init__(self):
        """Validate configuration."""
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("Chunk overlap must be less than chunk size")
        if self.min_chunk_size <= 0:
            raise ValueError("Minimum chunk size must be positive")


@dataclass
class DocumentChunk:
    """Represents a document chunk with heading path for hierarchy.

    Reference: examples/ingestion/chunker.py:50-66
    """

    content: str
    contextualized_content: str  # For embedding (includes heading context)
    index: int
    heading_path: List[str]  # e.g., ["Overview", "Getting Started"]
    metadata: Dict[str, Any]
    token_count: Optional[int] = None


class DoclingHybridChunker:
    """Docling HybridChunker wrapper for intelligent document splitting.

    Reference: examples/ingestion/chunker.py:68-269

    This chunker uses Docling's built-in HybridChunker which:
    - Respects document structure (sections, paragraphs, tables)
    - Is token-aware (fits embedding model limits)
    - Preserves semantic coherence
    - Includes heading context in chunks
    """

    def __init__(self, config: ChunkingConfig):
        """Initialize chunker.

        Args:
            config: Chunking configuration.
        """
        self.config = config

        # Initialize tokenizer for token-aware chunking
        # Reference: examples/ingestion/chunker.py:89-91
        model_id = "sentence-transformers/all-MiniLM-L6-v2"
        logger.info(f"Initializing tokenizer: {model_id}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)

        # Create HybridChunker
        # Reference: examples/ingestion/chunker.py:94-98
        self.chunker = HybridChunker(
            tokenizer=self.tokenizer,
            max_tokens=config.max_tokens,
            merge_peers=True  # Merge small adjacent chunks
        )

        logger.info(f"HybridChunker initialized (max_tokens={config.max_tokens})")

    def chunk_document(
        self,
        docling_doc: DoclingDocument,
        title: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[DocumentChunk]:
        """Chunk a DoclingDocument using HybridChunker.

        Reference: examples/ingestion/chunker.py:102-185

        Args:
            docling_doc: Pre-converted DoclingDocument from Docling.
            title: Document title.
            source: Document source path.
            metadata: Additional metadata.

        Returns:
            List of document chunks with contextualized content.
        """
        base_metadata = {
            "title": title,
            "source": source,
            "chunk_method": "hybrid",
            **(metadata or {})
        }

        try:
            # Use HybridChunker to chunk the DoclingDocument
            # Reference: examples/ingestion/chunker.py:143-145
            chunk_iter = self.chunker.chunk(dl_doc=docling_doc)
            chunks = list(chunk_iter)

            document_chunks = []
            for i, chunk in enumerate(chunks):
                # Get contextualized text (includes heading hierarchy)
                # Reference: examples/ingestion/chunker.py:152
                contextualized_text = self.chunker.contextualize(chunk=chunk)
                token_count = len(self.tokenizer.encode(contextualized_text))

                # Extract heading path from chunk metadata
                heading_path = []
                if hasattr(chunk, 'meta') and hasattr(chunk.meta, 'headings'):
                    heading_path = list(chunk.meta.headings) if chunk.meta.headings else []

                document_chunks.append(DocumentChunk(
                    content=chunk.text,
                    contextualized_content=contextualized_text.strip(),
                    index=i,
                    heading_path=heading_path,
                    metadata={
                        **base_metadata,
                        "total_chunks": len(chunks),
                        "token_count": token_count,
                        "has_context": True,
                    },
                    token_count=token_count
                ))

            logger.info(f"Created {len(document_chunks)} chunks using HybridChunker")
            return document_chunks

        except Exception as e:
            logger.error(f"HybridChunker failed: {e}")
            raise

    def chunk_markdown(
        self,
        content: str,
        title: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[DocumentChunk]:
        """Chunk raw markdown content using regex-based parsing.

        This is a fallback method when DoclingDocument is not available.

        Args:
            content: Raw markdown content.
            title: Document title.
            source: Document source path.
            metadata: Additional metadata.

        Returns:
            List of document chunks with heading paths.
        """
        if not content.strip():
            return []

        base_metadata = {
            "title": title,
            "source": source,
            "chunk_method": "markdown_fallback",
            **(metadata or {})
        }

        chunks = []
        lines = content.split('\n')
        current_headings: Dict[int, str] = {}
        current_content: List[str] = []
        chunk_index = 0

        for line in lines:
            # Check for heading
            heading_match = re.match(r'^(#{1,3})\s+(.+)$', line)

            if heading_match:
                # Save previous chunk if content exists
                if current_content:
                    content_text = '\n'.join(current_content).strip()
                    if content_text and len(content_text) >= self.config.min_chunk_size:
                        heading_path = [
                            current_headings.get(i, '')
                            for i in range(1, 4)
                            if current_headings.get(i)
                        ]

                        # Build contextualized content
                        context_prefix = " > ".join(heading_path) + "\n\n" if heading_path else ""
                        contextualized = context_prefix + content_text
                        token_count = len(self.tokenizer.encode(contextualized))

                        chunks.append(DocumentChunk(
                            content=content_text,
                            contextualized_content=contextualized,
                            index=chunk_index,
                            heading_path=heading_path,
                            metadata={
                                **base_metadata,
                                "token_count": token_count,
                            },
                            token_count=token_count
                        ))
                        chunk_index += 1

                    current_content = []

                # Update heading hierarchy
                level = len(heading_match.group(1))
                heading_text = heading_match.group(2).strip()
                current_headings[level] = heading_text

                # Clear lower-level headings
                for lvl in range(level + 1, 4):
                    current_headings.pop(lvl, None)
            else:
                current_content.append(line)

        # Don't forget last chunk
        if current_content:
            content_text = '\n'.join(current_content).strip()
            if content_text and len(content_text) >= self.config.min_chunk_size:
                heading_path = [
                    current_headings.get(i, '')
                    for i in range(1, 4)
                    if current_headings.get(i)
                ]

                context_prefix = " > ".join(heading_path) + "\n\n" if heading_path else ""
                contextualized = context_prefix + content_text
                token_count = len(self.tokenizer.encode(contextualized))

                chunks.append(DocumentChunk(
                    content=content_text,
                    contextualized_content=contextualized,
                    index=chunk_index,
                    heading_path=heading_path,
                    metadata={
                        **base_metadata,
                        "token_count": token_count,
                    },
                    token_count=token_count
                ))

        # Update total_chunks in metadata
        for chunk in chunks:
            chunk.metadata["total_chunks"] = len(chunks)

        logger.info(f"Created {len(chunks)} chunks using markdown fallback")
        return chunks


def create_chunker(config: Optional[ChunkingConfig] = None) -> DoclingHybridChunker:
    """Create DoclingHybridChunker with optional configuration.

    Args:
        config: Optional chunking configuration.

    Returns:
        DoclingHybridChunker instance.
    """
    return DoclingHybridChunker(config or ChunkingConfig())
