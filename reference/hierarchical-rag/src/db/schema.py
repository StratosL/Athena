"""Database schema DDL for Hierarchical RAG Workshop.

This module contains the DDL statements for creating the database schema
with support for both categorical and structural hierarchies.
"""

import logging
import asyncpg

logger = logging.getLogger(__name__)


# DDL for enabling pgvector extension
ENABLE_PGVECTOR = """
CREATE EXTENSION IF NOT EXISTS vector;
"""


# DDL for categories table (categorical hierarchy - across documents)
CREATE_CATEGORIES_TABLE = """
-- Self-referential categories table for unlimited nesting depth
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    parent_category_id INT REFERENCES categories(id) ON DELETE CASCADE,
    description TEXT,
    level INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
"""

CREATE_CATEGORIES_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_categories_parent ON categories(parent_category_id);
CREATE INDEX IF NOT EXISTS idx_categories_level ON categories(level);
CREATE INDEX IF NOT EXISTS idx_categories_slug ON categories(slug);
"""


# DDL for documents table
CREATE_DOCUMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(512) NOT NULL,
    category_id INT NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    source_path TEXT,
    doc_type VARCHAR(50) DEFAULT 'markdown',
    summary TEXT,
    summary_embedding VECTOR(1536),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
"""

CREATE_DOCUMENTS_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_documents_category ON documents(category_id);
CREATE INDEX IF NOT EXISTS idx_documents_metadata ON documents USING gin(metadata);

-- HNSW index for document summary embeddings
CREATE INDEX IF NOT EXISTS idx_documents_summary_hnsw ON documents
    USING hnsw (summary_embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
"""


# DDL for document_chunks table (structural hierarchy - within documents)
CREATE_CHUNKS_TABLE = """
-- Self-referential chunks table for parent-child relationships
CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    parent_chunk_id INT REFERENCES document_chunks(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    content_embedding VECTOR(1536),
    chunk_level INT NOT NULL DEFAULT 0,
    sequence_number INT NOT NULL,
    heading_path TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
"""

CREATE_CHUNKS_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_chunks_document ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_parent ON document_chunks(parent_chunk_id);
CREATE INDEX IF NOT EXISTS idx_chunks_level ON document_chunks(chunk_level);
CREATE INDEX IF NOT EXISTS idx_chunks_doc_level ON document_chunks(document_id, chunk_level);
CREATE INDEX IF NOT EXISTS idx_chunks_metadata ON document_chunks USING gin(metadata);

-- HNSW index for chunk content embeddings
CREATE INDEX IF NOT EXISTS idx_chunks_embedding_hnsw ON document_chunks
    USING hnsw (content_embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Partial index for leaf-level searches (most common query pattern)
CREATE INDEX IF NOT EXISTS idx_chunks_leaf_embedding ON document_chunks
    USING hnsw (content_embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64)
    WHERE chunk_level = 2;
"""


# Drop statements for cleanup
DROP_SCHEMA = """
DROP TABLE IF EXISTS document_chunks CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
"""


async def create_schema(pool: asyncpg.Pool) -> None:
    """Create the database schema.

    Args:
        pool: Database connection pool.
    """
    async with pool.acquire() as conn:
        logger.info("Enabling pgvector extension...")
        await conn.execute(ENABLE_PGVECTOR)

        logger.info("Creating categories table...")
        await conn.execute(CREATE_CATEGORIES_TABLE)
        await conn.execute(CREATE_CATEGORIES_INDEXES)

        logger.info("Creating documents table...")
        await conn.execute(CREATE_DOCUMENTS_TABLE)
        await conn.execute(CREATE_DOCUMENTS_INDEXES)

        logger.info("Creating document_chunks table...")
        await conn.execute(CREATE_CHUNKS_TABLE)
        await conn.execute(CREATE_CHUNKS_INDEXES)

        logger.info("Database schema created successfully")


async def drop_schema(pool: asyncpg.Pool) -> None:
    """Drop the database schema.

    Args:
        pool: Database connection pool.
    """
    async with pool.acquire() as conn:
        logger.warning("Dropping database schema...")
        await conn.execute(DROP_SCHEMA)
        logger.info("Database schema dropped")


async def check_pgvector_extension(pool: asyncpg.Pool) -> bool:
    """Check if pgvector extension is installed.

    Args:
        pool: Database connection pool.

    Returns:
        True if pgvector is installed, False otherwise.
    """
    async with pool.acquire() as conn:
        result = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')"
        )
        return result


async def clean_tables(pool: asyncpg.Pool) -> None:
    """Clean all data from tables without dropping them.

    Args:
        pool: Database connection pool.
    """
    async with pool.acquire() as conn:
        async with conn.transaction():
            logger.warning("Cleaning all tables...")
            await conn.execute("DELETE FROM document_chunks")
            await conn.execute("DELETE FROM documents")
            await conn.execute("DELETE FROM categories")
            logger.info("Tables cleaned")
