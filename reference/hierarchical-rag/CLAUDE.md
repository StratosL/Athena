# Hierarchical RAG Workshop - Global Development Rules

## 1. Core Principles

**NATIVE OPENROUTER IS NON-NEGOTIABLE**
- Use `pydantic_ai.models.openrouter.OpenRouterModel` directly
- NEVER use `OpenAIProvider` with `base_url` for OpenRouter
- API key is read automatically from `OPENROUTER_API_KEY` env var

**ASYNC EVERYWHERE**
- All database operations use `asyncpg` (never psycopg2)
- All embedding calls are async via `AsyncOpenAI`
- CLI uses `asyncio.run()` at entry point only

**TYPE SAFETY IS REQUIRED**
- Full Pydantic models for all data structures
- Type hints on all function signatures
- Use `Optional[T]` or `T | None` explicitly

**REFERENCE THE EXAMPLES**
- Implementation patterns exist in `examples/` directory
- Always check examples before implementing new modules
- Adapt patterns, don't reinvent

---

## 2. Tech Stack

```
Runtime:        Python 3.12+
Package Mgr:    uv (NEVER pip)
Agent:          pydantic-ai-slim[openrouter]
LLM:            OpenRouter (native integration)
Embeddings:     OpenRouter openai/text-embedding-3-small (SAME API key)
Database:       PostgreSQL + pgvector
DB Driver:      asyncpg
Doc Processing: docling + transformers
Config:         pydantic-settings
CLI:            Rich (console, Panel, Prompt)
```

**Single API Key**: Both LLM and embeddings use `OPENROUTER_API_KEY` - no separate OpenAI key needed.

**Install command:**
```bash
uv add "pydantic-ai-slim[openrouter]" pydantic-settings asyncpg pgvector python-dotenv rich openai docling transformers
```

---

## 3. Architecture

```
src/
├── __init__.py
├── settings.py              # pydantic-settings config → load_settings()
├── providers.py             # get_llm_model() factory → OpenRouterModel
│
├── db/
│   ├── __init__.py
│   ├── connection.py        # get_pool() with pgvector registration
│   ├── schema.py            # DDL for categories, documents, chunks
│   └── operations.py        # Async CRUD with CTEs for hierarchy
│
├── ingestion/
│   ├── __init__.py
│   ├── chunker.py           # DoclingHybridChunker wrapper
│   ├── embeddings.py        # EmbeddingGenerator (OpenRouter endpoint)
│   ├── hierarchy.py         # build_chunk_hierarchy() for 3 levels
│   └── pipeline.py          # DocumentIngestionPipeline orchestration
│
├── agents/
│   ├── __init__.py
│   ├── dependencies.py      # AgentDependencies dataclass
│   ├── prompts.py           # SYSTEM_PROMPT constant
│   ├── tools.py             # @rag_agent.tool decorated functions
│   └── rag_agent.py         # Agent(get_llm_model(), deps_type=...)
│
├── generate_docs.py         # Mock document generation (uses sub-agents)
├── ingest.py                # Ingestion entry point
└── cli.py                   # Streaming CLI with Rich
```

**Key Flow:**
```
.env → settings.py → providers.py → rag_agent.py → tools.py → db/operations.py
```

---

## 4. Code Style

**Naming:**
- `snake_case` for functions, variables, file names
- `PascalCase` for classes and Pydantic models
- Verbose names: `document_chunk_id` not `id`, `category_name` not `name`

**Type Hints:**
```python
async def search_chunks(
    pool: asyncpg.Pool,
    embedding: str,
    category_ids: list[int] | None,
    top_k: int = 5
) -> list[dict[str, Any]]:
    """Search chunks with optional category filtering."""
```

**Docstrings:** Google-style with Args/Returns
```python
def build_chunk_hierarchy(chunks: list[DocumentChunk], summary: str) -> list[dict]:
    """
    Build 3-level hierarchy from flat Docling chunks.

    Args:
        chunks: Flat list of DocumentChunk from Docling
        summary: Document summary for level 0

    Returns:
        Hierarchical list with parent_chunk_id relationships
    """
```

---

## 5. Database Conventions

**Vector Format for asyncpg:**
```python
# PostgreSQL vector string format - NO SPACES after commas
embedding_str = '[' + ','.join(map(str, embedding_list)) + ']'

# In query: cast explicitly
await conn.fetch("SELECT * FROM match_chunks($1::vector, $2)", embedding_str, top_k)
```

**Self-Referential Hierarchies:**
```sql
-- Categories: parent_category_id references categories(id)
-- Chunks: parent_chunk_id references document_chunks(id)
-- Use recursive CTEs for traversal
```

**Three-Level Chunk Hierarchy:**
- Level 0: Document summary (1 per document)
- Level 1: Section chunks (1 per top-level heading)
- Level 2: Leaf chunks (from Docling HybridChunker)

**Pool Initialization - Always Use Settings:**
```python
from pgvector.asyncpg import register_vector
from settings import load_settings

async def _init_connection(conn: asyncpg.Connection):
    await register_vector(conn)

settings = load_settings()
pool = await asyncpg.create_pool(
    settings.database_url,  # From .env, never hardcoded
    min_size=settings.db_pool_min_size,
    max_size=settings.db_pool_max_size,
    init=_init_connection
)
```

---

## 6. Pydantic AI Patterns

**Provider Factory (src/providers.py):**
```python
from pydantic_ai.models.openrouter import OpenRouterModel
from settings import load_settings

def get_llm_model() -> OpenRouterModel:
    """Get LLM model from settings - NEVER hardcode model names."""
    settings = load_settings()
    return OpenRouterModel(settings.llm_model)
```

**Agent Creation (src/agents/rag_agent.py):**
```python
from pydantic_ai import Agent
from providers import get_llm_model
from agents.dependencies import AgentDependencies
from agents.prompts import SYSTEM_PROMPT

# Model comes from settings via provider factory
rag_agent = Agent(
    get_llm_model(),
    deps_type=AgentDependencies,
    system_prompt=SYSTEM_PROMPT
)

# WRONG - Never hardcode model names
# agent = Agent(OpenRouterModel("anthropic/claude-3-5-haiku-20241022"))  # NO!
```

**Tool Registration:**
```python
@rag_agent.tool
async def search_knowledge_base(
    ctx: RunContext[AgentDependencies],
    query: str,
    category_ids: list[int] | None = None
) -> str:
    """Tool docstring becomes the tool description for the LLM."""
    embedding = await ctx.deps.get_embedding(query)
    # ... implementation
```

**Streaming CLI Pattern (src/cli.py):**
```python
async with rag_agent.iter(user_input, deps=deps, message_history=history) as run:
    async for node in run:
        if Agent.is_model_request_node(node):
            async with node.stream(run.ctx) as stream:
                async for event in stream:
                    # Handle PartStartEvent, PartDeltaEvent
        elif Agent.is_call_tools_node(node):
            # Handle tool calls
```

**System Prompt Best Practices:**

The agent's system prompt (`src/agents/prompts.py`) follows these principles:

1. **Default Behavior, Not Escape Hatches**: Make the desired behavior the default path
   - ❌ WRONG: "If unsure which category, search without filtering first"
   - ✅ RIGHT: "Only search without category_ids if the question truly spans multiple unrelated areas"

2. **Concrete Examples Over Abstract Instructions**: Show the full tool call pattern
   - ❌ WRONG: "Use search_knowledge_base with relevant category_ids"
   - ✅ RIGHT: "User asks about 'GDPR compliance' → call list_categories, identify Compliance (id: 20), then call search_knowledge_base(query='GDPR requirements', category_ids=[20])"

3. **Clear Step Sequences**: Number the retrieval steps explicitly (1. List categories, 2. Search with category_ids, 3. Get chunk context...)

**When Modifying Prompts:**
- Test with real queries (see `.claude/testing-results.md`)
- Ensure at least 50% of topic-specific queries use category filtering
- Add examples showing exact tool call signatures
- Avoid phrases that give the agent an "easy out" to skip intended behavior

---

## 7. Environment Configuration

**Required Environment Variables:**
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/hierarchical_rag

# OpenRouter (SINGLE KEY for both LLM and embeddings)
# Pydantic AI reads this automatically for LLM
# We also use it for embeddings via OpenRouter's embedding API
OPENROUTER_API_KEY=sk-or-v1-...

# Models
LLM_MODEL=anthropic/claude-3-5-haiku-20241022
EMBEDDING_MODEL=openai/text-embedding-3-small
```

**Settings Class Pattern:**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    database_url: str
    openrouter_api_key: str  # Single key for LLM + embeddings
    llm_model: str = "anthropic/claude-3-5-haiku-20241022"
    embedding_model: str = "openai/text-embedding-3-small"  # OpenRouter model ID
```

---

## 8. Development Commands

```bash
# Install dependencies
uv sync

# Generate mock documents
uv run python -m src.cli --generate-docs

# Setup database and ingest
uv run python -m src.cli --setup

# Run interactive CLI
uv run python -m src.cli

# Run with verbose logging
uv run python -m src.cli --verbose

# Test a single question against the agent (non-interactive)
uv run python -m src.cli --query "What are our Python naming conventions?"

# Run full automated evaluation of all 16 test questions
uv run python -m src.cli --eval

# Run evaluation with custom output path
uv run python -m src.cli --eval --eval-output my_results.json
```

**Testing with `--query`:**

Once the knowledge base is set up (`--setup`), use `--query` to quickly test how the agent handles a specific question. This is the fastest way to verify agent behavior after making changes to prompts, tools, or retrieval logic. The output shows the agent's streamed response including all tool calls, so you can see whether it calls `list_categories`, uses `category_ids` filtering, and expands context.

```bash
# Quick smoke test after prompt changes
uv run python -m src.cli --query "What is our GDPR breach notification timeline?"

# Test cross-category synthesis
uv run python -m src.cli --query "What security controls span from code development through production?"
```

**Testing with `--eval`:**

The eval harness (`src/eval.py`) runs all 16 test questions from `test_questions.md`, captures tool call patterns, scores hierarchical RAG behavior programmatically (category identification, filtering, context expansion), and uses an LLM judge for answer quality (accuracy, synthesis, citation). Results are saved as JSON and displayed as a Rich summary table.

---

## 9. Common Patterns

**AgentDependencies (src/agents/dependencies.py):**
```python
from dataclasses import dataclass, field
from typing import Any
import asyncpg
from openai import AsyncOpenAI
from settings import load_settings

@dataclass
class AgentDependencies:
    """Dependencies injected into agent tools."""
    db_pool: asyncpg.Pool | None = None
    embedding_client: AsyncOpenAI | None = None
    settings: Any | None = None

    async def initialize(self):
        """Lazy initialization of connections."""
        if not self.settings:
            self.settings = load_settings()
        if not self.db_pool:
            self.db_pool = await asyncpg.create_pool(
                self.settings.database_url,
                min_size=self.settings.db_pool_min_size,
                max_size=self.settings.db_pool_max_size
            )
        if not self.embedding_client:
            self.embedding_client = AsyncOpenAI(
                api_key=self.settings.openrouter_api_key,
                base_url="https://openrouter.ai/api/v1"
            )

    async def cleanup(self):
        """Close connections on shutdown."""
        if self.db_pool:
            await self.db_pool.close()
            self.db_pool = None

    async def get_embedding(self, text: str) -> list[float]:
        """Generate embedding via OpenRouter."""
        if not self.embedding_client:
            await self.initialize()
        response = await self.embedding_client.embeddings.create(
            model=self.settings.embedding_model,
            input=text
        )
        return response.data[0].embedding
```

**Database Connection Pool (src/db/connection.py):**
```python
from pgvector.asyncpg import register_vector
import asyncpg
from settings import load_settings

_pool: asyncpg.Pool | None = None

async def _init_connection(conn: asyncpg.Connection):
    await register_vector(conn)

async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        settings = load_settings()
        _pool = await asyncpg.create_pool(
            settings.database_url,
            min_size=settings.db_pool_min_size,
            max_size=settings.db_pool_max_size,
            init=_init_connection
        )
    return _pool
```

**Hierarchical Search Query (src/db/operations.py):**
```sql
WITH filtered_chunks AS (
    SELECT dc.*, 1 - (dc.content_embedding <=> $1::vector) AS similarity
    FROM document_chunks dc
    JOIN documents d ON d.id = dc.document_id
    WHERE dc.chunk_level = 2  -- Leaf chunks only
    AND ($2::int[] IS NULL OR d.category_id = ANY($2))
    ORDER BY dc.content_embedding <=> $1::vector
    LIMIT $3
)
SELECT fc.*, d.title, c.name AS category_name
FROM filtered_chunks fc
JOIN documents d ON d.id = fc.document_id
JOIN categories c ON c.id = d.category_id;
```

---

## 10. Critical Gotchas

1. **NEVER Hardcode**: All configuration comes from `settings.py` via `load_settings()`
   - Model names, API keys, database URLs, pool sizes - ALL from settings
2. **Single API Key**: `OPENROUTER_API_KEY` works for BOTH LLM and embeddings
3. **Provider Factory**: Use `get_llm_model()` from `providers.py`, never instantiate models directly
4. **Embedding Endpoint**: `https://openrouter.ai/api/v1` with model `openai/text-embedding-3-small`
5. **Vector String Format**: `'[1.0,2.0,3.0]'` with NO spaces after commas
6. **Native OpenRouter**: Import `OpenRouterModel` from `pydantic_ai.models.openrouter`
7. **pgvector Registration**: Must use `init=_init_connection` callback on pool creation
8. **Async All The Way**: Never use sync database calls or blocking operations
9. **Chunk Hierarchy**: Level 0 = doc summary, Level 1 = sections, Level 2 = leaves
10. **Settings Singleton**: Call `load_settings()` when needed, don't pass settings around

---

## 11. AI Coding Assistant Instructions

When working with this codebase:

1. **NEVER hardcode configuration** - all values come from `load_settings()`
2. **Check `examples/` first** - patterns exist for most modules
3. **Use the provider factory** - `get_llm_model()` from `providers.py` for agent creation
4. **Reference INITIAL.md** - has specific line references to example files
5. **Async by default** - all DB and API operations must be async
6. **Type everything** - no untyped functions or variables
7. **Google-style docstrings** - with Args and Returns sections
8. **Validate env setup** - pause for user input if .env is missing
9. **Log with context** - include category_id, chunk_id, document_id in log messages
10. **Stream responses** - use `agent.iter()` pattern from examples/cli.py
11. **Test hierarchical queries** - verify parent-child relationships work correctly

**Configuration Flow:**
```
.env → Settings (pydantic-settings) → load_settings() → used everywhere
```

This codebase demonstrates hierarchical RAG patterns. Maintain the two-level hierarchy design (categorical + structural) throughout all implementations.
