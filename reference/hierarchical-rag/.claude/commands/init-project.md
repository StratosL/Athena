# Initialize Hierarchical RAG Workshop

Run the following commands to set up the project locally.

## Prerequisites

- Python 3.12+
- PostgreSQL with pgvector extension
- uv package manager
- OpenRouter API key (https://openrouter.ai/keys)

## 1. Create Environment File

```bash
cp .env.example .env
```

Then edit `.env` and set:
- `DATABASE_URL` - Your PostgreSQL connection string
- `OPENROUTER_API_KEY` - Your OpenRouter API key (used for BOTH LLM and embeddings)

**IMPORTANT**: Pause and wait for user to confirm they've updated `.env` before proceeding.

## 2. Install Dependencies

```bash
uv sync
```

Installs all Python packages from pyproject.toml including:
- pydantic-ai-slim[openrouter]
- asyncpg, pgvector
- docling, transformers
- rich

## 3. Set Up PostgreSQL with pgvector

If using Docker:
```bash
docker run -d --name hierarchical-rag-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=hierarchical_rag \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

Or if PostgreSQL is already running, ensure pgvector extension is available:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## 4. Initialize Database Schema

```bash
uv run python -m src.cli --setup
```

This will:
- Create the `categories`, `documents`, and `document_chunks` tables
- Create HNSW indexes for vector search
- Verify pgvector extension is installed

**Expected output**: Schema creation success messages, no errors.

## 5. Generate Mock Documents

```bash
uv run python -m src.cli --generate-docs
```

This uses sub-agents to generate realistic IT knowledge base documents in the `docs/` folder organized by category:
- Infrastructure (Networking, Cloud)
- Development (Python, API Design)
- Security (Compliance, Incident Response)
- Operations (Monitoring, Deployment)

**Expected output**: 16 markdown documents created in `docs/` directory.

## 6. Run Ingestion Pipeline

```bash
uv run python -m src.cli --setup
```

(Run setup again after docs are generated to ingest them)

This will:
- Insert categories from taxonomy
- Chunk documents using Docling HybridChunker
- Build 3-level chunk hierarchy (summary → sections → leaves)
- Generate embeddings via OpenRouter
- Store everything in PostgreSQL with pgvector

**Expected output**: Progress bar, document/chunk counts, no errors.

## 7. Start Interactive CLI

```bash
uv run python -m src.cli
```

You should see the welcome panel and be able to ask questions about the IT knowledge base.

## 8. Validate Setup

Test the system with these queries:

```
You: How do I configure a VPN tunnel?
```
Should retrieve from Infrastructure > Networking

```
You: What are the GDPR data retention requirements?
```
Should retrieve from Security > Compliance

```
You: info
```
Should show current configuration (LLM model, embedding model, database)

## Quick Reference

| Command | Description |
|---------|-------------|
| `uv run python -m src.cli` | Start interactive CLI |
| `uv run python -m src.cli --setup` | Initialize DB + ingest docs |
| `uv run python -m src.cli --generate-docs` | Generate mock documents |
| `uv run python -m src.cli --verbose` | CLI with detailed logging |

## Cleanup

```bash
# Stop Docker database
docker stop hierarchical-rag-db && docker rm hierarchical-rag-db

# Or drop tables manually
psql $DATABASE_URL -c "DROP TABLE IF EXISTS document_chunks, documents, categories CASCADE;"
```

## Troubleshooting

**"pgvector extension not found"**
- Install pgvector in PostgreSQL or use the pgvector/pgvector Docker image

**"OPENROUTER_API_KEY not set"**
- Ensure `.env` file exists and contains your API key

**"Connection refused"**
- Check DATABASE_URL in `.env`
- Ensure PostgreSQL is running on the specified port

**"Model not found"**
- Verify LLM_MODEL in `.env` is a valid OpenRouter model ID
- Check https://openrouter.ai/models for available models
