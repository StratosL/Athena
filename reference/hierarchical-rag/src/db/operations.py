"""Database operations for Hierarchical RAG Workshop.

This module contains all CRUD operations for categories, documents, and chunks
with support for hierarchical queries using recursive CTEs.
"""

import json
import logging
from typing import List, Dict, Any, Optional

import asyncpg

logger = logging.getLogger(__name__)


# =============================================================================
# CATEGORY OPERATIONS
# =============================================================================

async def insert_category(
    pool: asyncpg.Pool,
    name: str,
    slug: str,
    parent_id: Optional[int],
    description: str,
    level: int
) -> int:
    """Insert a new category.

    Args:
        pool: Database connection pool.
        name: Category name.
        slug: URL-safe slug.
        parent_id: Parent category ID (None for root).
        description: Category description.
        level: Hierarchy level (0=root, 1=department, 2=subcategory).

    Returns:
        ID of the inserted category.
    """
    async with pool.acquire() as conn:
        result = await conn.fetchval(
            """
            INSERT INTO categories (name, slug, parent_category_id, description, level)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
            """,
            name, slug, parent_id, description, level
        )
        return result


async def get_categories_by_level(
    pool: asyncpg.Pool,
    level: int
) -> List[Dict[str, Any]]:
    """Get all categories at a specific level.

    Args:
        pool: Database connection pool.
        level: Hierarchy level to query.

    Returns:
        List of category dictionaries.
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, name, slug, parent_category_id, description, level
            FROM categories
            WHERE level = $1
            ORDER BY name
            """,
            level
        )
        return [dict(row) for row in rows]


async def get_subcategories(
    pool: asyncpg.Pool,
    parent_id: int
) -> List[Dict[str, Any]]:
    """Get child categories of a parent category.

    Args:
        pool: Database connection pool.
        parent_id: Parent category ID.

    Returns:
        List of subcategory dictionaries.
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, name, slug, parent_category_id, description, level
            FROM categories
            WHERE parent_category_id = $1
            ORDER BY name
            """,
            parent_id
        )
        return [dict(row) for row in rows]


async def get_category_by_slug(
    pool: asyncpg.Pool,
    slug: str
) -> Optional[Dict[str, Any]]:
    """Get a category by its slug.

    Args:
        pool: Database connection pool.
        slug: Category slug.

    Returns:
        Category dictionary or None if not found.
    """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT id, name, slug, parent_category_id, description, level
            FROM categories
            WHERE slug = $1
            """,
            slug
        )
        return dict(row) if row else None


async def get_category_tree(pool: asyncpg.Pool) -> List[Dict[str, Any]]:
    """Get the full category tree with document counts.

    Returns a nested tree structure with children arrays.

    Args:
        pool: Database connection pool.

    Returns:
        List of root category dictionaries with nested children.
    """
    async with pool.acquire() as conn:
        # Get all categories with document counts
        rows = await conn.fetch(
            """
            SELECT
                c.id, c.name, c.slug, c.parent_category_id, c.description, c.level,
                COUNT(d.id) AS doc_count
            FROM categories c
            LEFT JOIN documents d ON d.category_id = c.id
            GROUP BY c.id
            ORDER BY c.level, c.name
            """
        )

        # Build tree structure
        categories = {row["id"]: {**dict(row), "children": []} for row in rows}

        # Organize into tree
        roots = []
        for cat_id, cat in categories.items():
            parent_id = cat["parent_category_id"]
            if parent_id is None:
                roots.append(cat)
            elif parent_id in categories:
                categories[parent_id]["children"].append(cat)

        return roots


async def get_category_path(
    pool: asyncpg.Pool,
    category_id: int
) -> str:
    """Get the full path of a category (e.g., "Security > Compliance").

    Args:
        pool: Database connection pool.
        category_id: Category ID.

    Returns:
        Category path string.
    """
    async with pool.acquire() as conn:
        # Use recursive CTE to get ancestors
        rows = await conn.fetch(
            """
            WITH RECURSIVE ancestors AS (
                SELECT id, name, parent_category_id, 0 AS depth
                FROM categories
                WHERE id = $1

                UNION ALL

                SELECT c.id, c.name, c.parent_category_id, a.depth + 1
                FROM categories c
                JOIN ancestors a ON c.id = a.parent_category_id
            )
            SELECT name FROM ancestors
            ORDER BY depth DESC
            """,
            category_id
        )
        return " > ".join(row["name"] for row in rows)


# =============================================================================
# DOCUMENT OPERATIONS
# =============================================================================

async def insert_document(
    pool: asyncpg.Pool,
    title: str,
    category_id: int,
    source_path: str,
    summary: str,
    summary_embedding: List[float],
    metadata: Dict[str, Any]
) -> int:
    """Insert a new document.

    Args:
        pool: Database connection pool.
        title: Document title.
        category_id: Category ID.
        source_path: Path to source file.
        summary: Document summary.
        summary_embedding: Summary embedding vector.
        metadata: Document metadata.

    Returns:
        ID of the inserted document.
    """
    # Pass embedding as list - pgvector asyncpg registration handles conversion
    async with pool.acquire() as conn:
        result = await conn.fetchval(
            """
            INSERT INTO documents (title, category_id, source_path, summary, summary_embedding, metadata)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
            """,
            title, category_id, source_path, summary, summary_embedding, json.dumps(metadata)
        )
        return result


async def get_documents_by_category(
    pool: asyncpg.Pool,
    category_id: int
) -> List[Dict[str, Any]]:
    """Get all documents in a category.

    Args:
        pool: Database connection pool.
        category_id: Category ID.

    Returns:
        List of document dictionaries.
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, title, source_path, summary, metadata, created_at
            FROM documents
            WHERE category_id = $1
            ORDER BY title
            """,
            category_id
        )
        return [dict(row) for row in rows]


async def get_document_by_id(
    pool: asyncpg.Pool,
    document_id: int
) -> Optional[Dict[str, Any]]:
    """Get a document by ID.

    Args:
        pool: Database connection pool.
        document_id: Document ID.

    Returns:
        Document dictionary or None.
    """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT d.*, c.name AS category_name
            FROM documents d
            JOIN categories c ON c.id = d.category_id
            WHERE d.id = $1
            """,
            document_id
        )
        return dict(row) if row else None


# =============================================================================
# CHUNK OPERATIONS
# =============================================================================

async def insert_chunk(
    pool: asyncpg.Pool,
    document_id: int,
    parent_chunk_id: Optional[int],
    content: str,
    content_embedding: List[float],
    chunk_level: int,
    sequence_number: int,
    heading_path: List[str],
    metadata: Dict[str, Any]
) -> int:
    """Insert a new chunk.

    Args:
        pool: Database connection pool.
        document_id: Parent document ID.
        parent_chunk_id: Parent chunk ID (for hierarchy).
        content: Chunk content.
        content_embedding: Content embedding vector.
        chunk_level: Hierarchy level (0=summary, 1=section, 2=leaf).
        sequence_number: Order within parent.
        heading_path: Heading path array.
        metadata: Chunk metadata.

    Returns:
        ID of the inserted chunk.
    """
    # Pass embedding as list - pgvector asyncpg registration handles conversion
    async with pool.acquire() as conn:
        result = await conn.fetchval(
            """
            INSERT INTO document_chunks
            (document_id, parent_chunk_id, content, content_embedding,
             chunk_level, sequence_number, heading_path, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id
            """,
            document_id, parent_chunk_id, content, content_embedding,
            chunk_level, sequence_number, heading_path, json.dumps(metadata)
        )
        return result


async def search_chunks(
    pool: asyncpg.Pool,
    query_embedding: List[float],
    category_ids: Optional[List[int]],
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """Search chunks with optional category filtering.

    This is the KEY hierarchical search query that combines:
    - Categorical hierarchy (filter by category)
    - Structural hierarchy (include parent context)

    Args:
        pool: Database connection pool.
        query_embedding: Query embedding as list of floats.
        category_ids: Optional list of category IDs to filter.
        top_k: Number of results to return.

    Returns:
        List of search results with parent context.
    """
    async with pool.acquire() as conn:
        # The combined hierarchical search query
        # pgvector asyncpg registration handles list to vector conversion
        rows = await conn.fetch(
            """
            WITH filtered_chunks AS (
                SELECT
                    dc.id,
                    dc.document_id,
                    dc.parent_chunk_id,
                    dc.content,
                    dc.chunk_level,
                    dc.heading_path,
                    dc.metadata,
                    1 - (dc.content_embedding <=> $1) AS similarity
                FROM document_chunks dc
                JOIN documents d ON d.id = dc.document_id
                WHERE dc.chunk_level = 2  -- Leaf chunks only
                AND ($2::int[] IS NULL OR d.category_id = ANY($2::int[]))
                ORDER BY dc.content_embedding <=> $1
                LIMIT $3
            ),
            parent_context AS (
                SELECT DISTINCT ON (p.id)
                    p.id,
                    p.content AS parent_content,
                    p.heading_path AS parent_heading_path,
                    p.chunk_level
                FROM filtered_chunks fc
                JOIN document_chunks p ON p.id = fc.parent_chunk_id
            )
            SELECT
                fc.id AS chunk_id,
                fc.document_id,
                fc.content,
                fc.similarity,
                fc.heading_path,
                fc.metadata,
                d.title AS document_title,
                c.name AS category_name,
                pc.parent_content,
                pc.parent_heading_path
            FROM filtered_chunks fc
            JOIN documents d ON d.id = fc.document_id
            JOIN categories c ON c.id = d.category_id
            LEFT JOIN parent_context pc ON pc.id = fc.parent_chunk_id
            ORDER BY fc.similarity DESC
            """,
            query_embedding, category_ids, top_k
        )

        results = []
        for row in rows:
            result = dict(row)
            # Add category path
            result["category_path"] = await get_category_path(pool, row["document_id"])
            results.append(result)

        return results


async def get_chunk_with_context(
    pool: asyncpg.Pool,
    chunk_id: int
) -> Optional[Dict[str, Any]]:
    """Get a chunk with its parent and sibling context.

    Args:
        pool: Database connection pool.
        chunk_id: Chunk ID.

    Returns:
        Dictionary with chunk, parent, and siblings.
    """
    async with pool.acquire() as conn:
        # Get the chunk
        chunk = await conn.fetchrow(
            """
            SELECT dc.*, d.title AS document_title
            FROM document_chunks dc
            JOIN documents d ON d.id = dc.document_id
            WHERE dc.id = $1
            """,
            chunk_id
        )

        if not chunk:
            return None

        result = {
            "chunk_id": chunk["id"],
            "chunk_content": chunk["content"],
            "heading_path": chunk["heading_path"],
            "chunk_level": chunk["chunk_level"],
            "document_title": chunk["document_title"],
        }

        # Get parent if exists
        if chunk["parent_chunk_id"]:
            parent = await conn.fetchrow(
                """
                SELECT content, heading_path
                FROM document_chunks
                WHERE id = $1
                """,
                chunk["parent_chunk_id"]
            )
            if parent:
                result["parent_content"] = parent["content"]
                result["parent_heading_path"] = parent["heading_path"]

        # Get siblings
        if chunk["parent_chunk_id"]:
            siblings = await conn.fetch(
                """
                SELECT id, content, sequence_number
                FROM document_chunks
                WHERE parent_chunk_id = $1
                AND id != $2
                ORDER BY sequence_number
                """,
                chunk["parent_chunk_id"], chunk_id
            )
            result["siblings"] = [
                {"id": s["id"], "content": s["content"], "sequence": s["sequence_number"]}
                for s in siblings
            ]

        # Build hierarchy path
        hierarchy_path = []
        current_id = chunk["parent_chunk_id"]
        while current_id:
            ancestor = await conn.fetchrow(
                "SELECT parent_chunk_id, heading_path FROM document_chunks WHERE id = $1",
                current_id
            )
            if ancestor and ancestor["heading_path"]:
                hierarchy_path.insert(0, ancestor["heading_path"][0] if ancestor["heading_path"] else "")
            current_id = ancestor["parent_chunk_id"] if ancestor else None

        result["hierarchy_path"] = hierarchy_path + (chunk["heading_path"] or [])

        return result


async def get_document_overview(
    pool: asyncpg.Pool,
    document_id: int
) -> Optional[Dict[str, Any]]:
    """Get a high-level overview of a document.

    Args:
        pool: Database connection pool.
        document_id: Document ID.

    Returns:
        Document overview with sections.
    """
    async with pool.acquire() as conn:
        # Get document
        doc = await conn.fetchrow(
            """
            SELECT d.*, c.name AS category_name
            FROM documents d
            JOIN categories c ON c.id = d.category_id
            WHERE d.id = $1
            """,
            document_id
        )

        if not doc:
            return None

        # Get category path
        category_path = await get_category_path(pool, doc["category_id"])

        # Get sections (level 1 chunks)
        sections = await conn.fetch(
            """
            SELECT
                dc.heading_path,
                COUNT(*) FILTER (WHERE child.id IS NOT NULL) AS chunk_count
            FROM document_chunks dc
            LEFT JOIN document_chunks child ON child.parent_chunk_id = dc.id
            WHERE dc.document_id = $1 AND dc.chunk_level = 1
            GROUP BY dc.id, dc.heading_path
            ORDER BY dc.sequence_number
            """,
            document_id
        )

        return {
            "document_id": doc["id"],
            "title": doc["title"],
            "category_path": category_path,
            "summary": doc["summary"],
            "sections": [
                {
                    "heading": s["heading_path"][0] if s["heading_path"] else "General",
                    "chunk_count": s["chunk_count"]
                }
                for s in sections
            ]
        }
