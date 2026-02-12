"""Chunk hierarchy builder for Hierarchical RAG.

This module transforms flat Docling chunks into a 3-level hierarchy:
- Level 0: Document summary (1 chunk per document)
- Level 1: Section summaries (1 per unique top-level heading)
- Level 2: Leaf chunks (original Docling chunks)
"""

import logging
from typing import List, Dict, Any, Optional

from .chunker import DocumentChunk

logger = logging.getLogger(__name__)


def build_chunk_hierarchy(
    docling_chunks: List[DocumentChunk],
    document_summary: str,
    document_title: str
) -> List[Dict[str, Any]]:
    """Build 3-level hierarchy from flat Docling chunks.

    Takes flat Docling chunks and builds a hierarchical structure:
    - Level 0: Document summary (1 chunk)
    - Level 1: Section summaries (1 per unique top-level heading)
    - Level 2: Leaf chunks (original Docling chunks)

    Args:
        docling_chunks: Flat list of DocumentChunk from Docling.
        document_summary: Document summary for level 0.
        document_title: Document title for metadata.

    Returns:
        List of hierarchical chunk dictionaries with parent relationships.
    """
    if not docling_chunks:
        # Return just the document summary if no chunks
        return [{
            "content": document_summary,
            "contextualized_content": document_summary,
            "chunk_level": 0,
            "heading_path": [],
            "parent_index": None,
            "sequence_number": 0,
            "metadata": {
                "type": "document_summary",
                "title": document_title,
            },
        }]

    hierarchy: List[Dict[str, Any]] = []

    # Level 0: Document summary
    hierarchy.append({
        "content": document_summary,
        "contextualized_content": document_summary,
        "chunk_level": 0,
        "heading_path": [],
        "parent_index": None,
        "sequence_number": 0,
        "metadata": {
            "type": "document_summary",
            "title": document_title,
        },
        "children_indices": [],  # Will be populated
    })

    # Level 1: Group by top-level heading
    section_map: Dict[str, int] = {}  # heading -> index in hierarchy

    for chunk in docling_chunks:
        top_heading = chunk.heading_path[0] if chunk.heading_path else "General"

        if top_heading not in section_map:
            section_idx = len(hierarchy)
            section_map[top_heading] = section_idx

            hierarchy.append({
                "content": "",  # Will be filled with concatenated content
                "contextualized_content": "",
                "chunk_level": 1,
                "heading_path": [top_heading],
                "parent_index": 0,  # Points to document summary
                "sequence_number": len(section_map) - 1,
                "metadata": {
                    "type": "section",
                    "title": document_title,
                    "section_heading": top_heading,
                },
                "children_indices": [],
            })

            # Add to document summary's children
            hierarchy[0]["children_indices"].append(section_idx)

    # Level 2: Leaf chunks linked to their section
    for chunk in docling_chunks:
        top_heading = chunk.heading_path[0] if chunk.heading_path else "General"
        parent_idx = section_map[top_heading]
        leaf_idx = len(hierarchy)

        hierarchy.append({
            "content": chunk.content,
            "contextualized_content": chunk.contextualized_content,
            "chunk_level": 2,
            "heading_path": chunk.heading_path,
            "parent_index": parent_idx,
            "sequence_number": chunk.index,
            "metadata": {
                "type": "leaf",
                "title": document_title,
                "token_count": chunk.token_count,
                **chunk.metadata,
            },
        })

        # Add to section's children
        hierarchy[parent_idx]["children_indices"].append(leaf_idx)

    # Fill section content (concatenate children or truncate)
    for idx, node in enumerate(hierarchy):
        if node["chunk_level"] == 1 and not node["content"]:
            children_content = []
            for child_idx in node.get("children_indices", []):
                children_content.append(hierarchy[child_idx]["content"])

            # Use first 500 chars as section summary
            combined = " ".join(children_content)
            node["content"] = combined[:500] + "..." if len(combined) > 500 else combined

            # Contextualized version includes heading
            heading = node["heading_path"][0] if node["heading_path"] else ""
            node["contextualized_content"] = f"{heading}\n\n{node['content']}"

    logger.info(
        f"Built hierarchy: 1 doc summary, {len(section_map)} sections, "
        f"{len(docling_chunks)} leaf chunks"
    )

    return hierarchy


def extract_document_summary(
    content: str,
    max_length: int = 500
) -> str:
    """Extract a summary from document content.

    Uses the first section of the document as the summary.
    Can be replaced with LLM-based summarization.

    Args:
        content: Full document content.
        max_length: Maximum summary length.

    Returns:
        Document summary string.
    """
    # Try to find the first meaningful section
    lines = content.split('\n')
    summary_lines = []
    in_summary = False
    total_chars = 0

    for line in lines:
        stripped = line.strip()

        # Skip title (# heading at start)
        if stripped.startswith('# ') and not in_summary:
            in_summary = True
            continue

        # Stop at next major heading
        if stripped.startswith('## ') and summary_lines:
            break

        if in_summary and stripped:
            summary_lines.append(stripped)
            total_chars += len(stripped)

            if total_chars >= max_length:
                break

    summary = ' '.join(summary_lines)

    # Truncate if still too long
    if len(summary) > max_length:
        summary = summary[:max_length].rsplit(' ', 1)[0] + "..."

    return summary if summary else content[:max_length]


def get_hierarchy_stats(hierarchy: List[Dict[str, Any]]) -> Dict[str, int]:
    """Get statistics about the hierarchy.

    Args:
        hierarchy: List of hierarchical chunk dictionaries.

    Returns:
        Dictionary with hierarchy statistics.
    """
    stats = {
        "total_chunks": len(hierarchy),
        "level_0_count": 0,
        "level_1_count": 0,
        "level_2_count": 0,
    }

    for node in hierarchy:
        level = node.get("chunk_level", 0)
        if level == 0:
            stats["level_0_count"] += 1
        elif level == 1:
            stats["level_1_count"] += 1
        elif level == 2:
            stats["level_2_count"] += 1

    return stats
