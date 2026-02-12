# Hierarchical RAG Agent

Multi-Level Retrieval with PostgreSQL + pgvector using Pydantic AI Agent

## Overview

This project demonstrates **hierarchical RAG (Retrieval-Augmented Generation)** using two complementary patterns:

1. **Categorical Hierarchy** - Metadata-driven routing across documents using category trees
2. **Structural Hierarchy** - Parent-child chunk navigation within documents

A single **Pydantic AI agent** with specialized tools navigates both hierarchy layers to provide contextually rich answers. Documents are processed with **Docling's HybridChunker** for intelligent, token-aware chunking that preserves document structure.

## Tech Stack

- **Runtime**: Python 3.11+
- **Package Manager**: uv
- **Agent Framework**: Pydantic AI with native OpenRouter integration
- **Database**: PostgreSQL + pgvector extension
- **Document Processing**: Docling (HybridChunker)
- **Embeddings**: OpenRouter (text-embedding-3-small, 1536 dim)
- **CLI**: Rich (formatted terminal output with streaming)

## Prerequisites

1. **Python 3.11+** installed
2. **PostgreSQL** with pgvector extension
   - Local: Run the Postgres Docker container, comes with pgvector
   - Cloud: Neon, Supabase, or other managed PostgreSQL with pgvector
3. **OpenRouter API key** from https://openrouter.ai/keys
4. **uv** package manager: `pip install uv`

## Quick Start

```bash
# Install dependencies
uv sync

# Copy environment template and configure
cp .env.example .env
# Edit .env with your DATABASE_URL and OPENROUTER_API_KEY

# Setup database and ingest the included sample documents
uv run python -m src.cli --setup

# Start interactive chat
uv run python -m src.cli
```

The repository includes sample documents in `docs/` ready for ingestion. If you want to regenerate them or create your own mock data, run `uv run python -m src.cli --generate-docs`.

## Architecture

```
                    User Query
                         |
                         v
    +---------------------------------------------+
    |              RAG Agent                       |
    |                                              |
    |  Tools:                                      |
    |  - list_categories() -> Category tree        |
    |  - search_knowledge_base() -> Vector search  |
    |  - get_chunk_context() -> Parent context     |
    |  - get_document_overview() -> Doc summary    |
    +---------------------------------------------+
                         |
                         v
    +---------------------------------------------+
    |           PostgreSQL + pgvector              |
    |                                              |
    |  Categories (self-referential)               |
    |       +-- Documents (with summaries)         |
    |            +-- Chunks (3-level hierarchy)    |
    |                 - Level 0: Doc summary       |
    |                 - Level 1: Sections          |
    |                 - Level 2: Leaf chunks       |
    +---------------------------------------------+
```

## Project Structure

```
src/
|-- settings.py              # pydantic-settings configuration
|-- providers.py             # Native OpenRouter model factory
|
|-- db/
|   |-- connection.py        # asyncpg pool with pgvector
|   |-- schema.py            # DDL for categories, documents, chunks
|   +-- operations.py        # Async CRUD with hierarchical queries
|
|-- ingestion/
|   |-- chunker.py           # Docling HybridChunker wrapper
|   |-- embeddings.py        # OpenRouter embedding generation
|   |-- hierarchy.py         # 3-level chunk hierarchy builder
|   +-- pipeline.py          # Full ingestion orchestration
|
|-- agents/
|   |-- dependencies.py      # AgentDependencies dataclass
|   |-- prompts.py           # System prompt for hierarchical RAG
|   |-- rag_agent.py         # Pydantic AI agent with native OpenRouter
|   +-- tools.py             # Hierarchical search tools
|
|-- generate_docs.py         # Mock document generation
|-- ingest.py                # Setup and ingestion entry point
+-- cli.py                   # Interactive streaming CLI
```

## Key Concepts

### Two Hierarchy Patterns

**1. Categorical Hierarchy (across documents)**
- Categories form a tree (e.g., Security > Compliance > GDPR)
- Enables scoped search within specific domains
- Reduces search space before vector similarity

**2. Structural Hierarchy (within documents)**
- Chunks have parent-child relationships
- Level 0: Document summary
- Level 1: Section summaries
- Level 2: Leaf chunks (paragraphs)
- Enables context expansion after initial retrieval

### Agent Tools

| Tool | Purpose | Hierarchy Pattern |
|------|---------|-------------------|
| `list_categories` | Navigate category tree | Categorical |
| `search_knowledge_base` | Vector search with category filter | Both |
| `get_chunk_context` | Expand to parent/siblings | Structural |
| `get_document_overview` | Get document summary | Structural |

### Retrieval Strategy

1. Agent uses `list_categories` to understand available topics
2. Agent searches with `search_knowledge_base` (optionally filtered)
3. Agent expands context with `get_chunk_context` for relevant chunks
4. Agent synthesizes answer with proper citations

## Database Schema

### Categories (Categorical Hierarchy)
```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    parent_category_id INT REFERENCES categories(id),
    description TEXT,
    level INT NOT NULL DEFAULT 0
);
```

### Documents
```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(512) NOT NULL,
    category_id INT NOT NULL REFERENCES categories(id),
    summary TEXT,
    summary_embedding VECTOR(1536),
    metadata JSONB DEFAULT '{}'
);
```

### Document Chunks (Structural Hierarchy)
```sql
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INT NOT NULL REFERENCES documents(id),
    parent_chunk_id INT REFERENCES document_chunks(id),
    content TEXT NOT NULL,
    content_embedding VECTOR(1536),
    chunk_level INT NOT NULL DEFAULT 0,  -- 0=summary, 1=section, 2=leaf
    heading_path TEXT[] DEFAULT '{}'
);
```

## CLI Commands

```bash
# Interactive chat
uv run python -m src.cli

# Setup database and ingest documents
uv run python -m src.cli --setup

# Generate new mock documents (optional)
uv run python -m src.cli --generate-docs

# Verbose logging
uv run python -m src.cli --verbose

# Single-shot query (non-interactive)
uv run python -m src.cli --query "What are our Python naming conventions?"

# Run automated evaluation
uv run python -m src.cli --eval

# Evaluation with custom output path
uv run python -m src.cli --eval --eval-output results.json
```

### Chat Commands

- `exit` / `quit` / `q` - Exit the CLI
- `info` - Show configuration details
- `clear` - Clear screen and reset history

## Testing the Agent

Once your knowledge base is set up, you can test the agent's behavior in two ways:

### Single-Shot Queries (`--query`)

Use `--query` to send a single question and see the full streamed response, including which tools the agent calls. This is the fastest way to verify behavior after changing prompts or tools.

```bash
uv run python -m src.cli --query "What is our GDPR breach notification timeline?"
```

The output shows the agent's reasoning: whether it calls `list_categories` to discover topics, uses `category_ids` filtering in `search_knowledge_base`, and expands context with `get_chunk_context` or `get_document_overview`.

### Automated Evaluation (`--eval`)

The eval harness runs all 16 test questions from `test_questions.md` through the agent and produces a scored report. Each question is scored on:

- **Tool call behavior (0-9):** Did the agent identify categories, filter searches, and expand context?
- **Answer quality (0-10):** LLM judge scores accuracy, cross-document synthesis, and source citation

```bash
# Run full evaluation
uv run python -m src.cli --eval

# Save results to a specific file
uv run python -m src.cli --eval --eval-output my_results.json
```

The report includes a tier summary table, per-question breakdown, and tool call analysis. Results are also saved as JSON for tracking improvements over time.

## Example Queries

Try these queries to see hierarchical retrieval in action:

1. "How do I configure a VPN tunnel between two office locations?"
2. "What are the GDPR requirements for data retention?"
3. "What are our Python coding standards for error handling?"
4. "What steps should I follow before deploying to production?"
5. "What security considerations apply to cloud infrastructure?"

## Acknowledgments

- [Pydantic AI](https://ai.pydantic.dev/) for the agent framework
- [pgvector](https://github.com/pgvector/pgvector) for vector similarity
- [Docling](https://github.com/DS4SD/docling) for document processing
- [OpenRouter](https://openrouter.ai/) for LLM and embedding access
