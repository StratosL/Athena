# Structured Implementation Plan: Hierarchical RAG Proof of Concept

## Overview

Build a CLI-based Pydantic AI agent that demonstrates hierarchical RAG using PostgreSQL + pgvector. The system combines **two patterns of hierarchical retrieval**: categorical hierarchy (metadata-driven routing across documents) and structural hierarchy (parent-child chunk navigation within documents). The agent is a single Pydantic AI agent with tools that navigate both hierarchy layers.

**Tech Stack:**
- **Runtime**: Python 3.12+
- **Package Manager**: uv
- **Agent Framework**: Pydantic AI with **native OpenRouter integration** (NOT OpenAI compatibility mode)
- **Database**: PostgreSQL + pgvector extension
- **Document Processing**: Docling (HybridChunker)
- **LLM Provider**: OpenRouter (using `pydantic-ai-slim[openrouter]`)
- **Embeddings**: OpenRouter `openai/text-embedding-3-small` (1536 dim) — SAME API key as LLM
- **Database Driver**: asyncpg
- **Environment Config**: pydantic-settings (with python-dotenv)
- **CLI Output**: Rich (for formatted terminal output with streaming)

---

## Reference Files Summary

**CRITICAL**: The coding agent MUST reference the example files in `examples/` directory. Each file provides battle-tested patterns that should be adapted for the hierarchical RAG implementation:

| Reference File | Purpose | Adapt For |
|----------------|---------|-----------|
| `examples/settings.py` | pydantic-settings configuration with env vars | Settings class with OpenRouter + embedding config |
| `examples/providers.py` | OpenRouter model initialization via OpenAI compat | **CHANGE**: Use native `OpenRouterModel` instead |
| `examples/dependencies.py` | AgentDependencies dataclass with db pool + OpenAI client | Keep pattern, add category caching |
| `examples/agent.py` | Pydantic AI agent with tools + streaming | Agent structure with hierarchical tools |
| `examples/tools.py` | Search tool implementations | Hierarchical search tools |
| `examples/prompts.py` | System prompt patterns | Hierarchical RAG system prompt |
| `examples/cli.py` | Rich console CLI with streaming + tool visibility | Interactive CLI with verbose mode |
| `examples/ingestion/chunker.py` | Docling HybridChunker wrapper | Chunk hierarchy builder |
| `examples/ingestion/embedder.py` | Embedding generation with batching | Same pattern, add summary embeddings |
| `examples/ingestion/ingest.py` | Full ingestion pipeline | Hierarchical ingestion with categories |
| `examples/.env.example` | Environment variable template | OpenRouter + embedding + DB config |

---

## Key Differences from Examples

### 1. LLM Provider: Native OpenRouter (NOT OpenAI Compatibility)

The examples use OpenAI compatibility mode (`OpenAIProvider` with `base_url`). This project MUST use Pydantic AI's **native OpenRouter integration**:

```python
# WRONG (from examples/providers.py) - DO NOT USE
from pydantic_ai.providers.openai import OpenAIProvider
provider = OpenAIProvider(base_url="https://openrouter.ai/api/v1", api_key=api_key)

# CORRECT - Use native OpenRouter
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

provider = OpenRouterProvider(api_key=settings.openrouter_api_key)
model = OpenRouterModel(settings.llm_model, provider=provider)
```

### 2. Database Schema: Hierarchical vs Flat

The examples use a simple flat schema (`documents` + `chunks`). This project requires:
- `categories` table (self-referential for unlimited nesting)
- `documents` table with `category_id` foreign key + `summary_embedding`
- `document_chunks` table with `parent_chunk_id` (self-referential for structural hierarchy)

### 3. Ingestion: Category-Aware with Chunk Hierarchy Building

The examples ingest files into flat chunks. This project must:
- Parse category from file path (`docs/security/compliance/file.md` → Security > Compliance)
- Build 3-level chunk hierarchy (document summary → sections → leaf chunks)
- Generate embeddings for both summaries AND chunks

### 4. Tools: Hierarchical Navigation

The examples have `semantic_search` and `hybrid_search`. This project needs:
- `list_categories` - Navigate category tree
- `search_knowledge_base` - Vector search filtered by category
- `get_chunk_context` - Expand context via parent chunks
- `get_document_overview` - Document-level summary

---

## Detailed Reference Line Numbers

For the coding agent to efficiently reference the example files, here are the specific line numbers for key patterns:

### `examples/settings.py`
| Lines | Pattern | Use For |
|-------|---------|---------|
| 12-20 | `BaseSettings` with `model_config` | Settings class structure |
| 23-26 | `database_url` field | Database URL config |
| 29-47 | LLM provider fields | **ADAPT** for OpenRouter native |
| 66-74 | Pool size fields | DB pool configuration |
| 77-85 | Embedding fields | Embedding model config |
| 88-98 | `load_settings()` with error handling | Settings loading pattern |

### `examples/dependencies.py`
| Lines | Pattern | Use For |
|-------|---------|---------|
| 10-21 | `AgentDependencies` dataclass | Dependencies structure |
| 24-42 | `initialize()` method | Lazy initialization |
| 44-48 | `cleanup()` method | Resource cleanup |
| 50-60 | `get_embedding()` method | Embedding helper |

### `examples/agent.py`
| Lines | Pattern | Use For |
|-------|---------|---------|
| 24-28 | `Agent()` creation | **CHANGE**: Use `OpenRouterModel` |
| 31-103 | `@rag_agent.tool` decorator | Tool definition pattern |
| 105-132 | `@rag_agent.instructions` | Dynamic instructions |

### `examples/tools.py`
| Lines | Pattern | Use For |
|-------|---------|---------|
| 22-26 | Tool function signature | `RunContext[AgentDependencies]` |
| 49 | Embedding generation | `deps.get_embedding(query)` |
| 52-53 | Vector string format | `'[' + ','.join(map(str, emb)) + ']'` |
| 55-62 | Database query | `asyncpg` fetch pattern |
| 64-76 | Result formatting | Search result formatting |

### `examples/cli.py`
| Lines | Pattern | Use For |
|-------|---------|---------|
| 31-53 | `stream_agent_interaction` | Streaming function signature |
| 66-70 | `agent.iter()` | Streaming agent execution |
| 79-101 | Text streaming | `PartStartEvent`, `PartDeltaEvent` |
| 104-151 | Tool event handling | `FunctionToolCallEvent` |
| 167-180 | `display_welcome()` | Rich Panel for welcome |
| 183-256 | Main conversation loop | Message history management |

### `examples/ingestion/chunker.py`
| Lines | Pattern | Use For |
|-------|---------|---------|
| 33-48 | `ChunkingConfig` dataclass | Chunking configuration |
| 50-66 | `DocumentChunk` dataclass | Chunk representation |
| 68-100 | `DoclingHybridChunker.__init__` | HybridChunker setup |
| 89-91 | Tokenizer initialization | `AutoTokenizer.from_pretrained` |
| 94-98 | HybridChunker creation | `merge_peers=True` |
| 102-185 | `chunk_document()` method | Main chunking logic |
| 143-145 | `chunker.chunk()` call | Docling chunking |
| 152 | `chunker.contextualize()` | Context-enriched text |
| 187-256 | Fallback chunking | Simple chunking when no DoclingDoc |

### `examples/ingestion/embedder.py`
| Lines | Pattern | Use For |
|-------|---------|---------|
| 33-61 | `EmbeddingGenerator` class | Embedding generation |
| 52-56 | Model configurations | Dimension/token limits |
| 63-82 | `generate_embedding()` | Single embedding |
| 84-109 | `generate_embeddings_batch()` | Batch embedding |
| 111-167 | `embed_chunks()` | Chunk embedding with progress |

### `examples/ingestion/ingest.py`
| Lines | Pattern | Use For |
|-------|---------|---------|
| 34-51 | Config/Result dataclasses | Pipeline configuration |
| 59-109 | `DocumentIngestionPipeline.__init__` | Pipeline setup |
| 111-170 | `ingest_documents()` | Main ingestion loop |
| 172-250 | `_ingest_single_document()` | Single doc processing |
| 275-328 | `_read_document()` | Docling document conversion |
| 416-463 | `_save_to_postgres()` | Database insertion |

**Reference**: The coding agent should follow Cole's patterns for Pydantic AI agents and CLIs from the example files listed above.

---

## Phase 1: Project Scaffolding

### 1.1 Initialize the project with uv

```bash
uv init hierarchical-rag-workshop
cd hierarchical-rag-workshop
uv python install 3.12
```

### 1.2 Install dependencies

**Reference**: See `examples/.env.example` for the full list of environment variables used in the reference project.

```bash
# Core dependencies with native OpenRouter support
uv add "pydantic-ai-slim[openrouter]" pydantic-settings asyncpg pgvector python-dotenv rich openai

# Docling for document processing - use full docling for HybridChunker
uv add docling transformers
```

**Note on Docling**: The reference implementation at `examples/ingestion/chunker.py` uses the full `docling` package with `HybridChunker`. This requires:
- `docling` (includes document converter and chunker)
- `transformers` (for tokenizer used by HybridChunker)

The chunker uses `sentence-transformers/all-MiniLM-L6-v2` tokenizer for token-aware chunking. See `examples/ingestion/chunker.py:89-91` for the pattern.

### 1.3 Create `.env.example`

**Reference**: Adapt from `examples/.env.example` but simplify for this workshop. Key difference:
- Use `OPENROUTER_API_KEY` for BOTH LLM and embeddings (single key)

```env
# ===========================================
# DATABASE CONFIGURATION
# ===========================================
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/hierarchical_rag

# Connection pool settings (from examples/settings.py:66-74)
DB_POOL_MIN_SIZE=2
DB_POOL_MAX_SIZE=10

# ===========================================
# OPENROUTER CONFIGURATION (SINGLE KEY FOR LLM + EMBEDDINGS)
# ===========================================
# Get your key at: https://openrouter.ai/keys
# Pydantic AI automatically reads this for LLM
# We also use it for embeddings via OpenRouter's embedding API
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# LLM Model (for RAG agent)
LLM_MODEL=anthropic/claude-3-5-haiku-20241022

# Embedding Model (OpenRouter provides OpenAI embeddings)
# See: https://openrouter.ai/docs/api/reference/embeddings
EMBEDDING_MODEL=openai/text-embedding-3-small
EMBEDDING_DIMENSION=1536
```

**Important**: OpenRouter provides BOTH LLM and embeddings with a single API key. The embedding endpoint is at `https://openrouter.ai/api/v1/embeddings` and uses an OpenAI-compatible API.

### 1.4 Project file structure

**Reference**: This structure mirrors the organization in `examples/` with adaptations for hierarchical RAG.

```
hierarchical-rag-workshop/
├── pyproject.toml
├── .env.example
├── .python-version
├── README.md
├── docs/                          # Generated mock documents (same as before)
│   ├── infrastructure/
│   │   ├── networking/
│   │   │   ├── network-architecture-guide.md
│   │   │   ├── vpn-configuration.md
│   │   │   └── firewall-policies.md
│   │   └── cloud/
│   │       ├── aws-setup-guide.md
│   │       └── azure-migration-plan.md
│   ├── development/
│   │   ├── python/
│   │   │   ├── coding-standards.md
│   │   │   └── testing-guidelines.md
│   │   └── api/
│   │       ├── rest-api-design.md
│   │       └── graphql-best-practices.md
│   ├── security/
│   │   ├── compliance/
│   │   │   ├── gdpr-compliance-guide.md
│   │   │   └── soc2-requirements.md
│   │   └── incident-response/
│   │       ├── incident-response-playbook.md
│   │       └── vulnerability-management.md
│   └── operations/
│       ├── monitoring/
│       │   ├── observability-guide.md
│       │   └── alerting-setup.md
│       └── deployment/
│           ├── ci-cd-pipeline.md
│           └── deployment-checklist.md
└── src/
    ├── __init__.py
    │
    │   # ===== CONFIGURATION (Reference: examples/settings.py) =====
    ├── settings.py                # pydantic-settings config class
    ├── providers.py               # OpenRouter model initialization (NATIVE, not OpenAI compat)
    │
    │   # ===== DATABASE (Reference: examples/dependencies.py for pool pattern) =====
    ├── db/
    │   ├── __init__.py
    │   ├── connection.py          # asyncpg connection pool
    │   ├── schema.py              # DDL statements + schema setup
    │   └── operations.py          # DB CRUD operations (hierarchical queries)
    │
    │   # ===== INGESTION (Reference: examples/ingestion/) =====
    ├── ingestion/
    │   ├── __init__.py
    │   ├── chunker.py             # Docling HybridChunker (Reference: examples/ingestion/chunker.py)
    │   ├── embeddings.py          # Embedding generation (Reference: examples/ingestion/embedder.py)
    │   ├── hierarchy.py           # NEW: Build chunk hierarchy from flat Docling chunks
    │   └── pipeline.py            # Full ingestion (Reference: examples/ingestion/ingest.py)
    │
    │   # ===== AGENT (Reference: examples/agent.py, tools.py, prompts.py) =====
    ├── agents/
    │   ├── __init__.py
    │   ├── dependencies.py        # AgentDependencies (Reference: examples/dependencies.py)
    │   ├── prompts.py             # System prompts (Reference: examples/prompts.py)
    │   ├── tools.py               # Hierarchical search tools (Reference: examples/tools.py)
    │   └── rag_agent.py           # Single RAG agent (Reference: examples/agent.py)
    │
    │   # ===== ENTRY POINTS =====
    ├── generate_docs.py           # Mock document generation script
    ├── ingest.py                  # Ingestion entry point
    └── cli.py                     # Interactive CLI (Reference: examples/cli.py)
```

### 1.5 Settings Module (`src/settings.py`)

**Reference**: Directly adapt from `examples/settings.py` which uses `pydantic-settings` for typed configuration.

```python
"""Settings configuration for Hierarchical RAG Workshop.

Reference: examples/settings.py - Adapt the pattern but use native OpenRouter.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict

class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Database Configuration (same as examples/settings.py:23-26)
    database_url: str = Field(
        ...,
        description="PostgreSQL connection URL with PGVector extension"
    )
    db_pool_min_size: int = Field(default=2)
    db_pool_max_size: int = Field(default=10)

    # OpenRouter Configuration - SINGLE KEY FOR LLM + EMBEDDINGS
    openrouter_api_key: str = Field(
        ...,
        description="OpenRouter API key (used for both LLM and embeddings)"
    )

    # LLM Configuration - NATIVE OPENROUTER
    llm_model: str = Field(
        default="anthropic/claude-3-5-haiku-20241022",
        description="OpenRouter model name for LLM"
    )

    # Embedding Configuration - VIA OPENROUTER
    # OpenRouter provides OpenAI embeddings at https://openrouter.ai/api/v1/embeddings
    embedding_model: str = Field(
        default="openai/text-embedding-3-small",
        description="OpenRouter embedding model ID"
    )
    embedding_dimension: int = Field(default=1536)


def load_settings() -> Settings:
    """Load settings with proper error handling."""
    try:
        return Settings()
    except Exception as e:
        error_msg = f"Failed to load settings: {e}"
        if "database_url" in str(e).lower():
            error_msg += "\nMake sure to set DATABASE_URL in your .env file"
        if "openrouter_api_key" in str(e).lower():
            error_msg += "\nMake sure to set OPENROUTER_API_KEY in your .env file"
        raise ValueError(error_msg) from e
```

### 1.6 Providers Module (`src/providers.py`)

**Reference**: `examples/providers.py` uses OpenAI compatibility mode. We MUST use native OpenRouter instead.

```python
"""Model providers for Hierarchical RAG Workshop.

Reference: examples/providers.py - BUT USE NATIVE OPENROUTER, NOT OPENAI COMPAT.

The examples use:
    from pydantic_ai.providers.openai import OpenAIProvider
    provider = OpenAIProvider(base_url=base_url, api_key=api_key)

We use native OpenRouter:
    from pydantic_ai.models.openrouter import OpenRouterModel
    from pydantic_ai.providers.openrouter import OpenRouterProvider
"""

from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
from settings import load_settings


def get_llm_model() -> OpenRouterModel:
    """
    Get LLM model using NATIVE OpenRouter integration.

    Pydantic AI automatically reads OPENROUTER_API_KEY from environment.
    See: https://ai.pydantic.dev/models/openrouter/
    """
    settings = load_settings()

    # Native OpenRouter - API key is read automatically from OPENROUTER_API_KEY env var
    # If you need to pass it explicitly:
    # provider = OpenRouterProvider(api_key="your-key")
    # model = OpenRouterModel(settings.llm_model, provider=provider)

    # Simplest approach - let Pydantic AI handle the API key
    return OpenRouterModel(settings.llm_model)


def get_model_info() -> dict:
    """Get information about current model configuration."""
    settings = load_settings()
    return {
        "llm_provider": "openrouter",
        "llm_model": settings.llm_model,
        "embedding_model": settings.embedding_model,
    }
```

---

## Phase 2: Mock Document Generation

This phase generates realistic mock documentation for an "Enterprise IT Knowledge Base" that demonstrates both hierarchy patterns.

**IMPORTANT — Use sub-agents for document generation**: When implementing this phase, use sub-agents (agent delegation) to generate the mock document content. For each document in the taxonomy below, delegate to a sub-agent that generates the markdown content. This keeps the generation parallelizable and cleanly separated. The sub-agent should be given the document title, category, subcategory, and description as context, and should return well-structured markdown with clear heading hierarchy.

### 2.1 Category structure definition

Define the category taxonomy as a data structure used both for document generation and for seeding the `categories` table during ingestion:

```python
CATEGORY_TAXONOMY = {
    "Infrastructure": {
        "description": "Hardware, networking, and cloud infrastructure documentation",
        "subcategories": {
            "Networking": {
                "description": "Network architecture, protocols, and configuration",
                "documents": [
                    "Network Architecture Guide",
                    "VPN Configuration",
                    "Firewall Policies"
                ]
            },
            "Cloud": {
                "description": "Cloud platform setup and migration guides",
                "documents": [
                    "AWS Setup Guide",
                    "Azure Migration Plan"
                ]
            }
        }
    },
    "Development": {
        "description": "Software development standards and practices",
        "subcategories": {
            "Python": {
                "description": "Python-specific coding practices and tooling",
                "documents": [
                    "Coding Standards",
                    "Testing Guidelines"
                ]
            },
            "API Design": {
                "description": "API architecture and design patterns",
                "documents": [
                    "REST API Design Guide",
                    "GraphQL Best Practices"
                ]
            }
        }
    },
    "Security": {
        "description": "Security compliance, policies, and incident management",
        "subcategories": {
            "Compliance": {
                "description": "Regulatory compliance frameworks and requirements",
                "documents": [
                    "GDPR Compliance Guide",
                    "SOC2 Requirements"
                ]
            },
            "Incident Response": {
                "description": "Security incident detection and response procedures",
                "documents": [
                    "Incident Response Playbook",
                    "Vulnerability Management"
                ]
            }
        }
    },
    "Operations": {
        "description": "System operations, monitoring, and deployment",
        "subcategories": {
            "Monitoring": {
                "description": "System observability and alerting configuration",
                "documents": [
                    "Observability Guide",
                    "Alerting Setup"
                ]
            },
            "Deployment": {
                "description": "CI/CD pipelines and deployment procedures",
                "documents": [
                    "CI/CD Pipeline Guide",
                    "Deployment Checklist"
                ]
            }
        }
    }
}
```

### 2.2 Document generation requirements

Each generated document must meet these requirements for Docling's HybridChunker to work effectively:

- Use clear heading hierarchy: `#` for title, `##` for major sections (4-6 per doc), `###` for subsections (2-3 per section)
- Include realistic technical content — not placeholder text
- Include occasional bullet lists, code blocks, and tables where appropriate
- Total length: 800-1500 words per document
- Content should be specific enough that vector search can distinguish between documents
- Different documents in the same subcategory must cover DISTINCT topics

Save each document to: `docs/{category_slug}/{subcategory_slug}/{filename-slug}.md`
Create directories as needed.

### 2.3 Expected document structure (example)

Each generated document should follow this pattern:

```markdown
# VPN Configuration Guide

## Overview
Brief introduction to VPN setup in the enterprise context...

## Site-to-Site VPN Architecture
### IPSec Tunnel Configuration
Detailed content about IPSec tunnels...

### Routing and Traffic Management
Content about routing over VPN...

## Remote Access VPN
### Client Configuration
Content about client setup...

### Authentication and MFA
Content about authentication...

## Troubleshooting
### Common Issues
Troubleshooting content...

### Diagnostic Commands
Commands and tools...

## Security Considerations
Content about VPN security best practices...
```

---

## Phase 3: Database Setup

### 3.1 Database schema (DDL)

Create these tables in order. The coding agent should put this SQL in `src/db/schema.py` and execute it via asyncpg.

```sql
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================
-- CATEGORICAL HIERARCHY (Pattern 2 - across documents)
-- ============================================

-- Self-referential categories table for unlimited nesting depth
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,  -- URL-safe identifier
    parent_category_id INT REFERENCES categories(id) ON DELETE CASCADE,
    description TEXT,
    level INT NOT NULL DEFAULT 0,       -- 0=root, 1=department, 2=subcategory
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_categories_parent ON categories(parent_category_id);
CREATE INDEX IF NOT EXISTS idx_categories_level ON categories(level);
CREATE INDEX IF NOT EXISTS idx_categories_slug ON categories(slug);

-- ============================================
-- DOCUMENTS
-- ============================================

CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(512) NOT NULL,
    category_id INT NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    source_path TEXT,                   -- Path to source file
    doc_type VARCHAR(50) DEFAULT 'markdown',
    summary TEXT,                       -- LLM-generated summary for top-level matching
    summary_embedding VECTOR(1536),     -- Embedding of the summary
    metadata JSONB DEFAULT '{}',        -- Flexible metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_documents_category ON documents(category_id);
CREATE INDEX IF NOT EXISTS idx_documents_metadata ON documents USING gin(metadata);

-- HNSW index for document summary embeddings
CREATE INDEX IF NOT EXISTS idx_documents_summary_hnsw ON documents
    USING hnsw (summary_embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- ============================================
-- STRUCTURAL HIERARCHY (Pattern 1 - within documents)
-- ============================================

-- Self-referential chunks table for parent-child relationships
CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    parent_chunk_id INT REFERENCES document_chunks(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    content_embedding VECTOR(1536),
    chunk_level INT NOT NULL DEFAULT 0, -- 0=document summary, 1=section, 2=leaf
    sequence_number INT NOT NULL,       -- Order within parent
    heading_path TEXT[] DEFAULT '{}',   -- e.g., ARRAY['VPN Config', 'Architecture', 'IPSec']
    metadata JSONB DEFAULT '{}',        -- headings, page_info, content_type from Docling
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

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
```

### 3.2 Connection management (`src/db/connection.py`)

**Reference**: See `examples/dependencies.py:29-35` for the pool creation pattern and `examples/ingestion/ingest.py` for how the pool is used throughout ingestion.

Use asyncpg with connection pooling:

```python
"""Database connection management.

Reference: examples/dependencies.py:29-35 for pool pattern
Reference: examples/ingestion/ingest.py for pool usage in pipeline
"""

import asyncpg
from pgvector.asyncpg import register_vector
from settings import load_settings

# Global pool (same pattern as examples/ingestion/ingest.py uses db_pool)
_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    """Get or create the database connection pool."""
    global _pool
    if _pool is None:
        settings = load_settings()
        _pool = await asyncpg.create_pool(
            settings.database_url,
            min_size=settings.db_pool_min_size,
            max_size=settings.db_pool_max_size,
            init=_init_connection  # Register pgvector on each connection
        )
    return _pool


async def _init_connection(conn: asyncpg.Connection):
    """Initialize each connection with pgvector support."""
    await register_vector(conn)


async def close_pool():
    """Close the database connection pool."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
```

**Important**: Register the pgvector vector type with each connection acquired from the pool using the `init` callback. This is cleaner than registering after each acquire. The asyncpg pgvector integration allows passing numpy arrays or lists directly as vector parameters.

**Note**: The examples at `examples/tools.py:52-62` show how to convert embeddings to PostgreSQL vector string format:
```python
# PostgreSQL vector format: '[1.0,2.0,3.0]' (no spaces after commas)
embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
```

### 3.3 Database operations (`src/db/operations.py`)

Implement these key functions:

```python
# Category operations
async def insert_category(pool, name, slug, parent_id, description, level) -> int
async def get_categories_by_level(pool, level: int) -> list[dict]
async def get_subcategories(pool, parent_id: int) -> list[dict]
async def get_category_by_slug(pool, slug: str) -> dict | None
async def get_category_tree(pool) -> list[dict]  # Full tree structure

# Document operations
async def insert_document(pool, title, category_id, source_path, summary, summary_embedding, metadata) -> int
async def get_documents_by_category(pool, category_id: int) -> list[dict]
async def search_document_summaries(pool, query_embedding, category_ids: list[int], top_k: int) -> list[dict]

# Chunk operations
async def insert_chunk(pool, document_id, parent_chunk_id, content, content_embedding, chunk_level, sequence_number, heading_path, metadata) -> int
async def search_chunks(pool, query_embedding, category_ids: list[int] | None, top_k: int) -> list[dict]
async def get_chunk_with_parent(pool, chunk_id: int) -> dict
async def get_sibling_chunks(pool, parent_chunk_id: int) -> list[dict]
async def get_chunk_hierarchy(pool, chunk_id: int) -> list[dict]  # Recursive CTE upward
```

**Critical SQL for hierarchical search** — the `search_chunks` function should implement the combined retrieval pattern:

```sql
-- Combined: filter by category (Pattern 2) + vector search (Pattern 1) + parent context
WITH filtered_chunks AS (
    SELECT 
        dc.id, dc.document_id, dc.parent_chunk_id, dc.content,
        dc.chunk_level, dc.heading_path, dc.metadata,
        1 - (dc.content_embedding <=> $1::vector) AS similarity
    FROM document_chunks dc
    JOIN documents d ON d.id = dc.document_id
    WHERE dc.chunk_level = 2  -- Leaf chunks only
    AND ($2::int[] IS NULL OR d.category_id = ANY($2::int[]))
    ORDER BY dc.content_embedding <=> $1::vector
    LIMIT $3
),
parent_context AS (
    SELECT DISTINCT ON (p.id)
        p.id, p.content AS parent_content, 
        p.heading_path AS parent_heading_path, p.chunk_level
    FROM filtered_chunks fc
    JOIN document_chunks p ON p.id = fc.parent_chunk_id
)
SELECT 
    fc.id AS chunk_id,
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
ORDER BY fc.similarity DESC;
```

---

## Phase 4: Document Ingestion Pipeline

**Reference**: The `examples/ingestion/` folder contains a complete ingestion pipeline that should be adapted for hierarchical RAG:
- `examples/ingestion/chunker.py` - Docling HybridChunker wrapper with fallback
- `examples/ingestion/embedder.py` - Batch embedding generation
- `examples/ingestion/ingest.py` - Full pipeline orchestration

### 4.1 Docling HybridChunker integration (`src/ingestion/chunker.py`)

**Reference**: Directly adapt from `examples/ingestion/chunker.py` which provides a robust HybridChunker wrapper with:
- Token-aware chunking using `sentence-transformers/all-MiniLM-L6-v2` tokenizer (line 89-91)
- `ChunkingConfig` dataclass for configuration (lines 33-48)
- `DocumentChunk` dataclass for chunk representation (lines 50-66)
- Fallback to simple chunking when DoclingDocument unavailable (lines 187-256)

```python
"""Docling HybridChunker for hierarchical RAG.

Reference: examples/ingestion/chunker.py - Copy the DoclingHybridChunker class
and ChunkingConfig/DocumentChunk dataclasses directly.

Key patterns from the reference:
- Line 89-91: Tokenizer initialization
- Line 94-98: HybridChunker initialization with merge_peers=True
- Line 143-145: Using chunker.chunk(dl_doc=docling_doc)
- Line 152: Using chunker.contextualize(chunk) for embedding text
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import logging

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


@dataclass
class DocumentChunk:
    """Represents a document chunk.

    Reference: examples/ingestion/chunker.py:50-66
    """
    content: str
    contextualized_content: str  # For embedding (includes heading context)
    index: int
    heading_path: List[str]
    metadata: Dict[str, Any]
    token_count: Optional[int] = None


class DoclingHybridChunker:
    """Docling HybridChunker wrapper.

    Reference: examples/ingestion/chunker.py:68-269
    Copy the full implementation from the reference file.
    """

    def __init__(self, config: ChunkingConfig):
        self.config = config

        # Initialize tokenizer (Reference: examples/ingestion/chunker.py:89-91)
        model_id = "sentence-transformers/all-MiniLM-L6-v2"
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)

        # Create HybridChunker (Reference: examples/ingestion/chunker.py:94-98)
        self.chunker = HybridChunker(
            tokenizer=self.tokenizer,
            max_tokens=config.max_tokens,
            merge_peers=True  # Merge small adjacent chunks
        )

    def chunk_document(
        self,
        docling_doc: DoclingDocument,
        title: str,
        source: str
    ) -> List[DocumentChunk]:
        """Chunk a DoclingDocument using HybridChunker.

        Reference: examples/ingestion/chunker.py:102-185
        """
        chunk_iter = self.chunker.chunk(dl_doc=docling_doc)
        chunks = list(chunk_iter)

        document_chunks = []
        for i, chunk in enumerate(chunks):
            # Get contextualized text (Reference: examples/ingestion/chunker.py:152)
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
                    "title": title,
                    "source": source,
                    "token_count": token_count,
                },
                token_count=token_count
            ))

        return document_chunks
```

**Fallback approach** if Docling's `DoclingDocument` creation from raw markdown is problematic: implement a simpler markdown-aware chunker that parses heading structure using regex and splits accordingly. The key is preserving heading hierarchy metadata:

```python
import re

def simple_markdown_chunker(markdown_content: str) -> list[dict]:
    """Fallback: Parse markdown headings and create hierarchical chunks."""
    lines = markdown_content.split('\n')
    chunks = []
    current_headings = {}
    current_content = []
    
    for line in lines:
        heading_match = re.match(r'^(#{1,3})\s+(.+)$', line)
        if heading_match:
            # Save previous chunk
            if current_content:
                content_text = '\n'.join(current_content).strip()
                if content_text:
                    heading_path = [current_headings.get(i, '') for i in range(1, 4) if current_headings.get(i)]
                    chunks.append({
                        "content": content_text,
                        "heading_path": heading_path,
                        "sequence_number": len(chunks),
                        "metadata": {"headings": heading_path},
                    })
                current_content = []
            
            level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()
            current_headings[level] = heading_text
            # Clear lower-level headings
            for l in range(level + 1, 4):
                current_headings.pop(l, None)
        else:
            current_content.append(line)
    
    # Don't forget last chunk
    if current_content:
        content_text = '\n'.join(current_content).strip()
        if content_text:
            heading_path = [current_headings.get(i, '') for i in range(1, 4) if current_headings.get(i)]
            chunks.append({
                "content": content_text,
                "heading_path": heading_path,
                "sequence_number": len(chunks),
                "metadata": {"headings": heading_path},
            })
    
    return chunks
```

### 4.2 Embedding generation (`src/ingestion/embeddings.py`)

**Reference**: Adapt from `examples/ingestion/embedder.py` but use OpenRouter for embeddings.

**Key Change**: Use OpenRouter's embedding API instead of direct OpenAI:
- Endpoint: `https://openrouter.ai/api/v1/embeddings`
- Model ID: `openai/text-embedding-3-small` (OpenRouter format)
- Authentication: Same `OPENROUTER_API_KEY` as LLM

```python
"""Embedding generation for hierarchical RAG via OpenRouter.

Reference: examples/ingestion/embedder.py - Adapt the pattern.
CHANGE: Use OpenRouter's embedding API instead of direct OpenAI.

OpenRouter Embeddings API: https://openrouter.ai/docs/api/reference/embeddings
"""

import logging
from typing import List
from openai import AsyncOpenAI
from settings import load_settings

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generates embeddings via OpenRouter's embedding API.

    Uses the same OPENROUTER_API_KEY as the LLM - single key for everything.
    """

    def __init__(self, batch_size: int = 100):
        settings = load_settings()
        self.model = settings.embedding_model  # "openai/text-embedding-3-small"
        self.batch_size = batch_size

        # Use OpenRouter's OpenAI-compatible embedding endpoint
        # Same API key as LLM - single key for everything!
        self.client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1"
        )

        # Model configurations
        self.model_configs = {
            "openai/text-embedding-3-small": {"dimensions": 1536, "max_tokens": 8191},
            "openai/text-embedding-3-large": {"dimensions": 3072, "max_tokens": 8191},
            "openai/text-embedding-ada-002": {"dimensions": 1536, "max_tokens": 8191}
        }
        self.config = self.model_configs.get(
            self.model,
            {"dimensions": 1536, "max_tokens": 8191}
        )

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text via OpenRouter."""
        # Truncate if too long
        if len(text) > self.config["max_tokens"] * 4:
            text = text[:self.config["max_tokens"] * 4]

        response = await self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding

    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts via OpenRouter."""
        # Truncate texts if too long
        processed_texts = []
        for text in texts:
            if len(text) > self.config["max_tokens"] * 4:
                text = text[:self.config["max_tokens"] * 4]
            processed_texts.append(text)

        all_embeddings = []
        for i in range(0, len(processed_texts), self.batch_size):
            batch = processed_texts[i:i + self.batch_size]
            response = await self.client.embeddings.create(
                model=self.model,
                input=batch
            )
            all_embeddings.extend([d.embedding for d in response.data])

        return all_embeddings

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings for this model."""
        return self.config["dimensions"]
```

### 4.3 Ingestion pipeline (`src/ingestion/pipeline.py`)

The ingestion pipeline should:

1. **Insert categories** from the `CATEGORY_TAXONOMY` into the `categories` table with correct parent-child relationships and levels
2. **For each document file** in the `docs/` directory:
   a. Read the markdown content
   b. Determine which category it belongs to based on its file path (e.g., `docs/security/compliance/gdpr-compliance-guide.md` → Security > Compliance)
   c. **Generate a document summary** using an LLM call (or take the first section as summary)
   d. **Embed the summary** and insert into `documents` table
   e. **Chunk the document** using Docling's HybridChunker
   f. **Build parent-child relationships** between chunks:
      - Group chunks by their heading path
      - Create a Level 0 chunk (document summary)
      - Create Level 1 chunks (one per top-level section heading)
      - Create Level 2 chunks (leaf chunks from Docling)
      - Link Level 2 → Level 1 via `parent_chunk_id` based on matching heading paths
      - Link Level 1 → Level 0 via `parent_chunk_id`
   g. **Embed all chunks** (use the contextualized content from Docling for embedding)
   h. **Insert chunks** into `document_chunks` table with correct relationships
3. **Print progress** using Rich console (progress bar, document count, chunk count)

**Building the structural hierarchy from Docling chunks:**

Docling's HybridChunker produces flat chunks with heading metadata. We need to reconstruct the parent-child tree:

```python
def build_chunk_hierarchy(docling_chunks: list[dict], document_summary: str) -> list[dict]:
    """
    Takes flat Docling chunks and builds a 3-level hierarchy:
    Level 0: Document summary (1 chunk)
    Level 1: Section summaries (1 per unique top-level heading)
    Level 2: Leaf chunks (original Docling chunks)
    """
    # Level 0: Document summary
    hierarchy = [{
        "content": document_summary,
        "chunk_level": 0,
        "heading_path": [],
        "parent_chunk_id": None,
        "sequence_number": 0,
        "metadata": {"type": "document_summary"},
        "children_indices": [],  # Will be populated
    }]
    
    # Level 1: Group by top-level heading
    section_map = {}  # heading -> index in hierarchy
    for chunk in docling_chunks:
        top_heading = chunk["heading_path"][0] if chunk["heading_path"] else "Ungrouped"
        if top_heading not in section_map:
            section_idx = len(hierarchy)
            section_map[top_heading] = section_idx
            # Concatenate all chunks under this heading for the section summary
            hierarchy.append({
                "content": "",  # Will be filled with concatenated content or LLM summary
                "chunk_level": 1,
                "heading_path": [top_heading],
                "parent_chunk_id": 0,  # Points to document summary (index 0)
                "sequence_number": len(section_map) - 1,
                "metadata": {"type": "section"},
                "children_indices": [],
            })
            hierarchy[0]["children_indices"].append(section_idx)
    
    # Level 2: Leaf chunks linked to their section
    for chunk in docling_chunks:
        top_heading = chunk["heading_path"][0] if chunk["heading_path"] else "Ungrouped"
        parent_idx = section_map[top_heading]
        leaf_idx = len(hierarchy)
        
        hierarchy.append({
            "content": chunk["content"],
            "contextualized_content": chunk.get("contextualized_content", chunk["content"]),
            "chunk_level": 2,
            "heading_path": chunk["heading_path"],
            "parent_chunk_id": parent_idx,  # Points to section
            "sequence_number": chunk["sequence_number"],
            "metadata": chunk.get("metadata", {}),
        })
        hierarchy[parent_idx]["children_indices"].append(leaf_idx)
    
    # Fill section content (concatenate children or truncate)
    for idx, node in enumerate(hierarchy):
        if node["chunk_level"] == 1 and not node["content"]:
            children_content = []
            for child_idx in node.get("children_indices", []):
                children_content.append(hierarchy[child_idx]["content"])
            # Use first 500 chars as section summary, or generate via LLM
            combined = " ".join(children_content)
            node["content"] = combined[:500] + "..." if len(combined) > 500 else combined
    
    return hierarchy
```

---

## Phase 5: Pydantic AI Agent (Single Agent with Tools)

**Reference**: The agent architecture is based on these example files:
- `examples/agent.py` - Agent structure with tools
- `examples/dependencies.py` - AgentDependencies dataclass
- `examples/prompts.py` - System prompt patterns
- `examples/tools.py` - Search tool implementations

### 5.1 Dependencies model (`src/agents/dependencies.py`)

**Reference**: Directly adapt from `examples/dependencies.py` which provides:
- Dataclass with db_pool, openai_client, settings (lines 10-21)
- `initialize()` method for lazy initialization (lines 24-42)
- `cleanup()` method for resource cleanup (lines 44-48)
- `get_embedding()` helper method (lines 50-60)

```python
"""Agent dependencies for hierarchical RAG.

Reference: examples/dependencies.py - Adapt the AgentDependencies class.
CHANGE: Use OpenRouter for embeddings (same API key as LLM).
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import asyncpg
from openai import AsyncOpenAI
from settings import load_settings


@dataclass
class AgentDependencies:
    """Dependencies injected into the agent and available in all tools.

    Reference: examples/dependencies.py:10-70
    """

    # Core dependencies
    db_pool: Optional[asyncpg.Pool] = None
    embedding_client: Optional[AsyncOpenAI] = None  # OpenRouter client for embeddings
    settings: Optional[Any] = None

    # Cache for category tree (NEW for hierarchical RAG)
    category_cache: Dict[str, Any] = field(default_factory=dict)

    async def initialize(self):
        """Initialize external connections."""
        if not self.settings:
            self.settings = load_settings()

        # Initialize database pool
        if not self.db_pool:
            self.db_pool = await asyncpg.create_pool(
                self.settings.database_url,
                min_size=self.settings.db_pool_min_size,
                max_size=self.settings.db_pool_max_size
            )

        # Initialize OpenRouter client for embeddings
        # Uses same API key as LLM - single key for everything!
        if not self.embedding_client:
            self.embedding_client = AsyncOpenAI(
                api_key=self.settings.openrouter_api_key,
                base_url="https://openrouter.ai/api/v1"
            )

    async def cleanup(self):
        """Clean up external connections."""
        if self.db_pool:
            await self.db_pool.close()
            self.db_pool = None

    async def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text via OpenRouter."""
        if not self.embedding_client:
            await self.initialize()

        response = await self.embedding_client.embeddings.create(
            model=self.settings.embedding_model,  # "openai/text-embedding-3-small"
            input=text
        )
        return response.data[0].embedding
```

### 5.2 RAG Agent (`src/agents/rag_agent.py`)

**Reference**: Adapt from `examples/agent.py` which shows:
- Agent creation with model and deps_type (lines 24-28)
- Tool definition with `@rag_agent.tool` decorator (lines 31-103)
- Dynamic instructions with `@rag_agent.instructions` (lines 105-132)

A single Pydantic AI agent with tools that navigate both hierarchy layers. The agent decides its own retrieval strategy per query — the hierarchical patterns are expressed through the **tools and data**, not through agent delegation.

**IMPORTANT**: Use native OpenRouter model, NOT the OpenAI compatibility pattern from the examples.

```python
"""Hierarchical RAG agent with native OpenRouter.

Reference: examples/agent.py - Adapt the agent pattern.
Reference: examples/prompts.py - System prompt pattern.

CRITICAL CHANGE: Use native OpenRouterModel instead of OpenAI compatibility.
"""

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openrouter import OpenRouterModel

from settings import load_settings
from agents.dependencies import AgentDependencies
from agents.prompts import HIERARCHICAL_RAG_SYSTEM_PROMPT

# Load settings
settings = load_settings()

# Create the RAG agent with NATIVE OpenRouter
# Reference: https://ai.pydantic.dev/models/openrouter/
rag_agent = Agent(
    OpenRouterModel(settings.llm_model),  # Native OpenRouter, NOT OpenAI compat
    deps_type=AgentDependencies,
    system_prompt=HIERARCHICAL_RAG_SYSTEM_PROMPT
)
```

### 5.3 System Prompt (`src/agents/prompts.py`)

**Reference**: Adapt from `examples/prompts.py` which shows system prompt organization.

```python
"""System prompts for Hierarchical RAG agent.

Reference: examples/prompts.py - Adapt the prompt pattern.
"""

HIERARCHICAL_RAG_SYSTEM_PROMPT = """You are a knowledgeable assistant with access to an enterprise IT
knowledge base organized in a hierarchical structure.

The knowledge base has two levels of organization:
- **Categories**: A tree of departments and subcategories (e.g., Security > Compliance)
- **Document structure**: Documents contain sections and chunks in a parent-child hierarchy

Your retrieval strategy should follow this pattern:
1. Use 'list_categories' to understand what areas the knowledge base covers.
2. Use 'search_knowledge_base' with relevant category_ids to search within the
   right scope. If unsure which category, search without filtering first.
3. Use 'get_chunk_context' on the most relevant results to retrieve the parent
   section for broader context.
4. Optionally use 'get_document_overview' to get the high-level summary of a document.
5. Synthesize the retrieved information into a clear, helpful answer.

Always cite which documents and sections your answer comes from. Include the
category path and heading path so the user knows exactly where the information lives.
"""
```
```

### 5.4 Agent tools (`src/agents/tools.py`)

**Reference**: Adapt from `examples/tools.py` which shows:
- Tool function signatures with `RunContext` (lines 22-26)
- Embedding generation within tools (line 49)
- Database queries with asyncpg (lines 55-62)
- Result formatting (lines 64-76)
- Vector string format for PostgreSQL (lines 52-53, 117-118)

**Tool 1 — Category navigation (categorical hierarchy)**

```python
"""Hierarchical RAG tools.

Reference: examples/tools.py - Adapt the search tool patterns.

Key patterns from the reference:
- Line 22-26: Tool function signature with RunContext[AgentDependencies]
- Line 49: Embedding generation via deps.get_embedding()
- Line 52-53: Vector string format '[1.0,2.0,...]'
- Line 55-62: Database query with asyncpg
"""

from pydantic_ai import RunContext
from typing import Optional, List
from agents.dependencies import AgentDependencies
from db.operations import (
    get_category_tree,
    search_chunks,
    get_chunk_with_context,
    get_document_overview as db_get_document_overview
)


# Import the agent to register tools
from agents.rag_agent import rag_agent


@rag_agent.tool
async def list_categories(ctx: RunContext[AgentDependencies]) -> str:
    """List the full category hierarchy in the knowledge base.
    Use this to understand what topics are available and find the right
    category IDs for scoped searches."""
    tree = await get_category_tree(ctx.deps.db_pool)

    # Format as indented tree
    def format_tree(nodes, indent=0):
        lines = []
        for node in nodes:
            prefix = "  " * indent
            connector = "├── " if indent > 0 else ""
            lines.append(f"{prefix}{connector}{node['name']} (id: {node['id']}) - {node['doc_count']} documents")
            if node.get('children'):
                lines.extend(format_tree(node['children'], indent + 1))
        return lines

    return "\n".join(format_tree(tree))
```

**Tool 2 — Scoped vector search (both hierarchies combined)**

```python
@rag_agent.tool
async def search_knowledge_base(
    ctx: RunContext[AgentDependencies],
    query: str,
    category_ids: Optional[List[int]] = None,
    top_k: int = 5,
) -> str:
    """Search for relevant content in the knowledge base.

    Args:
        query: The search query.
        category_ids: Optional list of category IDs to search within.
                      If provided, only searches documents in those categories.
                      If None, searches across all categories.
        top_k: Number of results to return.

    Returns chunks with their similarity score, document title, category,
    heading path, and chunk IDs (use chunk IDs with get_chunk_context).
    """
    # Generate embedding (Reference: examples/tools.py:49)
    query_embedding = await ctx.deps.get_embedding(query)

    # Convert to PostgreSQL vector format (Reference: examples/tools.py:52-53)
    embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'

    # Search chunks (Reference: examples/tools.py:55-62)
    results = await search_chunks(
        ctx.deps.db_pool, embedding_str, category_ids, top_k
    )

    # Format results (Reference: examples/tools.py:64-76)
    if not results:
        return "No relevant information found in the knowledge base."

    response_parts = [f"Found {len(results)} relevant chunks:\n"]
    for i, result in enumerate(results, 1):
        response_parts.append(
            f"\n--- Result {i} (similarity: {result['similarity']:.3f}) ---\n"
            f"Category: {result['category_path']}\n"
            f"Document: {result['document_title']}\n"
            f"Section: {' > '.join(result['heading_path'])}\n"
            f"Chunk ID: {result['chunk_id']}\n"
            f"Content: {result['content'][:300]}..."
        )

    return "\n".join(response_parts)
```

**Tool 3 — Context expansion (structural hierarchy)**

```python
@rag_agent.tool
async def get_chunk_context(ctx: RunContext[AgentDependencies], chunk_id: int) -> str:
    """Get expanded context for a chunk by retrieving its parent chunk
    and sibling chunks from the document's structural hierarchy.

    This navigates the within-document hierarchy: if you found a relevant
    paragraph (leaf chunk), this returns the full section it belongs to
    (parent chunk) plus adjacent paragraphs (siblings).

    Args:
        chunk_id: The ID of a chunk from search results.
    """
    context = await get_chunk_with_context(ctx.deps.db_pool, chunk_id)

    if not context:
        return f"No chunk found with ID {chunk_id}"

    # Format hierarchical context
    lines = [
        f"=== Context for Chunk {chunk_id} ===\n",
        f"Hierarchy: {' > '.join(context['hierarchy_path'])}\n",
        f"\n--- Parent Section ---\n{context['parent_content']}\n",
        f"\n--- Current Chunk ---\n{context['chunk_content']}\n",
    ]

    if context.get('siblings'):
        lines.append(f"\n--- Sibling Chunks ({len(context['siblings'])}) ---")
        for sib in context['siblings']:
            lines.append(f"\n[{sib['sequence']}] {sib['content'][:200]}...")

    return "\n".join(lines)
```

**Tool 4 — Document overview**

```python
@rag_agent.tool
async def get_document_overview(ctx: RunContext[AgentDependencies], document_id: int) -> str:
    """Get a high-level overview of a document including its summary,
    category, and section structure.

    Args:
        document_id: The document ID from search results.
    """
    doc = await db_get_document_overview(ctx.deps.db_pool, document_id)

    if not doc:
        return f"No document found with ID {document_id}"

    lines = [
        f"=== Document Overview ===\n",
        f"Title: {doc['title']}",
        f"Category: {doc['category_path']}",
        f"\nSummary:\n{doc['summary']}\n",
        f"\nSections:",
    ]

    for section in doc.get('sections', []):
        lines.append(f"  • {section['heading']} ({section['chunk_count']} chunks)")

    return "\n".join(lines)
```

### 5.4 Agent flow diagram

```
User Query
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                     RAG Agent                                │
│                                                             │
│  System prompt guides hierarchical retrieval strategy:      │
│                                                             │
│  1. list_categories()                                       │
│     └── Returns category tree with IDs                      │
│         (categorical hierarchy - Pattern 2)                 │
│                                                             │
│  2. search_knowledge_base(query, category_ids=[...])        │
│     └── Vector search filtered by category                  │
│         (both patterns combined: metadata filter + vectors) │
│                                                             │
│  3. get_chunk_context(chunk_id=...)                          │
│     └── Retrieves parent section + siblings                 │
│         (structural hierarchy - Pattern 1)                  │
│                                                             │
│  4. get_document_overview(document_id=...)                   │
│     └── High-level doc summary (optional)                   │
│                                                             │
│  5. Agent synthesizes answer from retrieved context          │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
Answer with citations (category path + document + section)
```

---

## Phase 6: CLI Interface (`src/cli.py`)

**Reference**: `examples/cli.py` provides a comprehensive CLI implementation with:
- Real-time streaming of agent responses (lines 56-164)
- Tool call visibility during execution (lines 104-151)
- Message history management (lines 197-241)
- Rich console formatting with Panel, Prompt (lines 167-180)
- Special commands (exit, info, clear) (lines 206-227)

Build an interactive CLI using Rich for formatted output.

### 6.1 CLI features

- **Interactive chat loop**: Prompt user for questions, display answers
- **Real-time streaming**: Stream agent responses as they're generated (Reference: `examples/cli.py:56-101`)
- **Tool call visibility**: Show which tools are being called with arguments (Reference: `examples/cli.py:104-151`)
- **Verbose mode** (`--verbose`): Show the hierarchical retrieval process step-by-step
- **Setup mode** (`--setup`): Initialize database and ingest documents
- **Generate mode** (`--generate-docs`): Generate mock documents

### 6.2 CLI entry point structure

**Reference**: Directly adapt from `examples/cli.py` which provides the complete streaming CLI pattern.

```python
"""Interactive CLI with streaming and tool call visibility.

Reference: examples/cli.py - Copy the streaming patterns.

Key patterns from the reference:
- Line 31-53: stream_agent_interaction function signature
- Line 56-164: _stream_agent with node-by-node processing
- Line 66-70: agent.iter() for streaming
- Line 79-101: Streaming text deltas
- Line 104-151: Tool call event handling
- Line 183-256: Main conversation loop
"""

import asyncio
import sys
import argparse
from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from dotenv import load_dotenv

from pydantic_ai import Agent
from pydantic_ai.messages import PartDeltaEvent, PartStartEvent, TextPartDelta

from agents.rag_agent import rag_agent
from agents.dependencies import AgentDependencies
from settings import load_settings

# Load environment variables
load_dotenv(override=True)

console = Console()


async def stream_agent_interaction(
    user_input: str,
    message_history: List,
    deps: AgentDependencies
) -> tuple[str, List]:
    """Stream agent interaction with real-time tool call display.

    Reference: examples/cli.py:31-164
    """
    response_text = ""

    # Stream the agent execution (Reference: examples/cli.py:66-70)
    async with rag_agent.iter(
        user_input,
        deps=deps,
        message_history=message_history
    ) as run:

        async for node in run:
            # Handle model request node - stream text (Reference: examples/cli.py:79-101)
            if Agent.is_model_request_node(node):
                console.print("[bold blue]Assistant:[/bold blue] ", end="")

                async with node.stream(run.ctx) as request_stream:
                    async for event in request_stream:
                        if isinstance(event, PartStartEvent) and event.part.part_kind == 'text':
                            if event.part.content:
                                console.print(event.part.content, end="")
                                response_text += event.part.content

                        elif isinstance(event, PartDeltaEvent) and isinstance(event.delta, TextPartDelta):
                            if event.delta.content_delta:
                                console.print(event.delta.content_delta, end="")
                                response_text += event.delta.content_delta

                console.print()  # New line after streaming

            # Handle tool calls (Reference: examples/cli.py:104-151)
            elif Agent.is_call_tools_node(node):
                async with node.stream(run.ctx) as tool_stream:
                    async for event in tool_stream:
                        event_type = type(event).__name__

                        if event_type == "FunctionToolCallEvent":
                            tool_name = "Unknown"
                            if hasattr(event, 'part') and hasattr(event.part, 'tool_name'):
                                tool_name = event.part.tool_name

                            console.print(f"  [cyan]🔧 Calling:[/cyan] [bold]{tool_name}[/bold]")

                            # Show arguments for search tools
                            if hasattr(event.part, 'args') and isinstance(event.part.args, dict):
                                args = event.part.args
                                if 'query' in args:
                                    console.print(f"    [dim]Query:[/dim] {args['query']}")
                                if 'category_ids' in args and args['category_ids']:
                                    console.print(f"    [dim]Categories:[/dim] {args['category_ids']}")

                        elif event_type == "FunctionToolResultEvent":
                            console.print(f"  [green]✓ Tool completed[/green]")

    # Get new messages for history
    new_messages = run.result.new_messages()
    return (response_text.strip(), new_messages)


def display_welcome():
    """Display welcome message."""
    settings = load_settings()

    welcome = Panel(
        "[bold blue]Hierarchical RAG Workshop[/bold blue]\n\n"
        "[green]Enterprise IT Knowledge Base with Categorical + Structural Hierarchy[/green]\n"
        f"[dim]LLM: {settings.llm_model} (via OpenRouter)[/dim]\n\n"
        "[dim]Commands: 'exit' to quit, 'info' for config, 'clear' to reset[/dim]",
        style="blue",
        padding=(1, 2)
    )
    console.print(welcome)
    console.print()


async def run_interactive_chat():
    """Main conversation loop.

    Reference: examples/cli.py:183-256
    """
    display_welcome()

    # Initialize dependencies
    deps = AgentDependencies()
    await deps.initialize()

    console.print("[bold green]✓[/bold green] Knowledge base connected\n")

    message_history = []

    try:
        while True:
            user_input = Prompt.ask("[bold green]You").strip()

            if user_input.lower() in ['exit', 'quit', 'q']:
                console.print("\n[yellow]👋 Goodbye![/yellow]")
                break

            if user_input.lower() == 'info':
                settings = load_settings()
                console.print(Panel(
                    f"[cyan]LLM Model:[/cyan] {settings.llm_model}\n"
                    f"[cyan]Embedding Model:[/cyan] {settings.embedding_model}\n"
                    f"[cyan]Database:[/cyan] {settings.database_url[:50]}...",
                    title="Configuration",
                    border_style="magenta"
                ))
                continue

            if user_input.lower() == 'clear':
                console.clear()
                display_welcome()
                message_history = []
                continue

            if not user_input:
                continue

            # Stream the interaction
            response, new_messages = await stream_agent_interaction(
                user_input, message_history, deps
            )
            message_history.extend(new_messages)
            console.print()

    finally:
        await deps.cleanup()
        console.print("\n[dim]Session ended.[/dim]")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Hierarchical RAG Workshop CLI")
    parser.add_argument("--setup", action="store_true", help="Initialize database and ingest documents")
    parser.add_argument("--generate-docs", action="store_true", help="Generate mock documents")

    args = parser.parse_args()

    if args.setup:
        from ingest import run_setup
        await run_setup()
    elif args.generate_docs:
        from generate_docs import generate_documents
        await generate_documents()
    else:
        await run_interactive_chat()


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Phase 7: End-to-End Validation

### 7.1 Setup validation checklist

The coding agent should implement validation at each step:

1. **Check `.env` exists**: If not, copy `.env.example` to `.env` and **prompt the user** to fill in their values. Do NOT proceed until the user confirms they've updated it.
   ```
   ⚠️  No .env file found. Created .env from .env.example.
   Please update the following values in .env:
     - DATABASE_URL (your PostgreSQL connection string)
     - OPENROUTER_API_KEY (your OpenRouter API key - works for LLM + embeddings)

   Press Enter when ready to continue...
   ```

2. **Test database connection**: Attempt to connect to PostgreSQL. If it fails, provide clear error messages:
   - Connection refused → "Is PostgreSQL running? Check DATABASE_URL in .env"
   - Authentication failed → "Check username/password in DATABASE_URL"
   - Database doesn't exist → Offer to create it

3. **Check pgvector extension**: `SELECT * FROM pg_extension WHERE extname = 'vector'`. If not installed, attempt `CREATE EXTENSION vector` and inform user if it fails (they need to install pgvector).

4. **Run schema creation**: Execute the DDL from Phase 3. Use `IF NOT EXISTS` for idempotency.

5. **Check if documents exist**: If `docs/` is empty, run document generation (Phase 2).

6. **Check if data is ingested**: `SELECT COUNT(*) FROM documents`. If 0, run ingestion pipeline (Phase 4).

### 7.2 Test queries

After setup, run these validation queries to verify the system works:

```python
TEST_QUERIES = [
    # Should route to Infrastructure > Networking
    "How do I configure a VPN tunnel between two office locations?",
    
    # Should route to Security > Compliance
    "What are the GDPR requirements for data retention?",
    
    # Should route to Development > Python
    "What are our Python coding standards for error handling?",
    
    # Should route to Operations > Deployment
    "What steps should I follow before deploying to production?",
    
    # Cross-category query - should pull from multiple categories
    "What security considerations should I keep in mind when setting up cloud infrastructure?",
]
```

For each test query, verify:
- The category navigator identifies the correct category
- Chunks are retrieved from the expected documents
- Parent context is included in the results
- The final answer references the correct sources

### 7.3 Automated validation script

Create a validation script that runs each test query and reports:
- ✅ Category routing correct
- ✅ Document retrieval from expected source
- ✅ Parent context included
- ✅ Response generated successfully
- ❌ Any failures with details

---

## Phase 8: README

Create a comprehensive README.md with:

### Sections to include:

1. **Title**: "Hierarchical RAG Workshop: Multi-Level Retrieval with PostgreSQL + pgvector"

2. **Overview**: Brief explanation of what this project demonstrates — both patterns of hierarchical RAG combined into a working proof of concept.

3. **Architecture diagram** (ASCII or Mermaid): Show the agent + tools architecture and data flow.

4. **Prerequisites**:
   - Python 3.12+
   - PostgreSQL with pgvector extension
   - OpenAI API key
   - uv package manager

5. **Quick start**:
   ```bash
   # Clone and setup
   uv sync
   cp .env.example .env
   # Edit .env with your values
   
   # Generate mock documents
   uv run python -m src.cli --generate-docs
   
   # Setup database and ingest
   uv run python -m src.cli --setup
   
   # Start interactive chat
   uv run python -m src.cli
   ```

6. **How it works**: Explain both hierarchy patterns and how they combine.

7. **Database schema**: Document the three tables and their relationships.

8. **Project structure**: File tree with descriptions.

9. **Key concepts demonstrated**:
   - Categorical hierarchy for search space reduction
   - Structural hierarchy for context preservation
   - Pydantic AI agent with tools for hierarchical retrieval
   - Docling HybridChunker for structure-aware chunking
   - pgvector HNSW indexes with metadata filtering
   - Recursive CTEs for hierarchy traversal

---

## Implementation Order Summary

Execute these phases in order:

| Phase | What | Depends On | Key References |
| ----- | ---- | ---------- | -------------- |
| 1     | Project scaffolding (uv, deps, file structure) | Nothing | `examples/settings.py`, `examples/.env.example` |
| 2     | Mock document generation (use sub-agents for this) | Phase 1 | — |
| 3     | Database schema + connection management | Phase 1 | `examples/dependencies.py` (pool pattern) |
| 4     | Ingestion pipeline (Docling + embeddings + hierarchy building) | Phases 2, 3 | `examples/ingestion/*` |
| 5     | Pydantic AI agent (single agent with tools) | Phases 3, 4 | `examples/agent.py`, `examples/tools.py`, `examples/prompts.py` |
| 6     | CLI interface | Phase 5 | `examples/cli.py` (streaming pattern) |
| 7     | End-to-end validation (pause for user .env setup) | All | — |
| 8     | README | All | — |

---

## Critical Implementation Notes

### OpenRouter Integration (MOST IMPORTANT)

**DO NOT** use the OpenAI compatibility pattern from the examples:
```python
# WRONG - From examples/providers.py
from pydantic_ai.providers.openai import OpenAIProvider
provider = OpenAIProvider(base_url="https://openrouter.ai/api/v1", api_key=api_key)
```

**DO** use native OpenRouter:
```python
# CORRECT - Native OpenRouter
from pydantic_ai.models.openrouter import OpenRouterModel
model = OpenRouterModel("anthropic/claude-3-5-haiku-20241022")  # API key from OPENROUTER_API_KEY env
```

### Reference File Usage Checklist

When implementing each module, the coding agent should:

1. **`src/settings.py`** — Copy structure from `examples/settings.py`, use single `OPENROUTER_API_KEY`
2. **`src/providers.py`** — Use `OpenRouterModel` NOT `OpenAIProvider` with base_url
3. **`src/db/connection.py`** — Adapt pool pattern from `examples/dependencies.py:29-35`
4. **`src/agents/dependencies.py`** — Adapt from `examples/dependencies.py`, use OpenRouter for embeddings
5. **`src/agents/rag_agent.py`** — Adapt agent pattern from `examples/agent.py` with native OpenRouter
6. **`src/agents/tools.py`** — Adapt search tools from `examples/tools.py`
7. **`src/agents/prompts.py`** — Follow pattern from `examples/prompts.py`
8. **`src/ingestion/chunker.py`** — Copy `DoclingHybridChunker` from `examples/ingestion/chunker.py`
9. **`src/ingestion/embeddings.py`** — Adapt from `examples/ingestion/embedder.py`, use OpenRouter endpoint
10. **`src/ingestion/pipeline.py`** — Adapt `DocumentIngestionPipeline` from `examples/ingestion/ingest.py`
11. **`src/cli.py`** — Copy streaming pattern from `examples/cli.py`

### Other Critical Reminders

- Use `uv` for all package management, never `pip`
- Install with: `uv add "pydantic-ai-slim[openrouter]"` (NOT full pydantic-ai)
- Use `asyncpg` for all database operations, never `psycopg2`
- Use `pydantic-settings` for config (NOT just python-dotenv)
- Use sub-agents to generate the mock documents in Phase 2
- The RAG application itself is a **single Pydantic AI agent** with tools — no sub-agents in the app
- All database operations must be async
- Pause for user input when .env needs to be configured
- Run end-to-end tests before declaring success

### Single API Key for Everything

OpenRouter provides BOTH LLM and embeddings with a single API key:
- `OPENROUTER_API_KEY` — For LLM (Pydantic AI reads this automatically) AND embeddings

**Embedding API Details:**
- Endpoint: `https://openrouter.ai/api/v1/embeddings`
- Model ID: `openai/text-embedding-3-small` (OpenRouter format)
- Uses AsyncOpenAI client with `base_url="https://openrouter.ai/api/v1"`

See `examples/.env.example` for reference (though we simplified to single key).