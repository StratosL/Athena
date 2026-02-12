Run comprehensive validation of the Hierarchical RAG Workshop to ensure all components are working correctly.

Execute the following validations in sequence and report results:

## 1. Environment Validation

```bash
# Check .env exists and has required variables
test -f .env && echo "✅ .env exists" || echo "❌ .env missing"
grep -q "OPENROUTER_API_KEY" .env && echo "✅ OPENROUTER_API_KEY set" || echo "❌ OPENROUTER_API_KEY missing"
grep -q "DATABASE_URL" .env && echo "✅ DATABASE_URL set" || echo "❌ DATABASE_URL missing"
```

**Expected:** All three checks pass

## 2. Dependencies Check

```bash
uv sync --dry-run 2>&1 | head -5
```

**Expected:** "Resolved X packages" or "All packages up to date"

## 3. Database Connectivity

```bash
uv run python -c "
import asyncio
from settings import load_settings
import asyncpg

async def check_db():
    settings = load_settings()
    conn = await asyncpg.connect(settings.database_url)
    version = await conn.fetchval('SELECT version()')
    print(f'✅ PostgreSQL connected: {version[:50]}...')

    # Check pgvector
    ext = await conn.fetchval(\"SELECT extname FROM pg_extension WHERE extname = 'vector'\")
    if ext:
        print('✅ pgvector extension installed')
    else:
        print('❌ pgvector extension NOT installed')

    await conn.close()

asyncio.run(check_db())
"
```

**Expected:** PostgreSQL version shown, pgvector extension confirmed

## 4. Schema Validation

```bash
uv run python -c "
import asyncio
from settings import load_settings
import asyncpg

async def check_schema():
    settings = load_settings()
    conn = await asyncpg.connect(settings.database_url)

    tables = ['categories', 'documents', 'document_chunks']
    for table in tables:
        exists = await conn.fetchval(
            \"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = \$1)\",
            table
        )
        status = '✅' if exists else '❌'
        print(f'{status} Table: {table}')

    await conn.close()

asyncio.run(check_schema())
"
```

**Expected:** All three tables exist (categories, documents, document_chunks)

## 5. Data Validation

```bash
uv run python -c "
import asyncio
from settings import load_settings
import asyncpg

async def check_data():
    settings = load_settings()
    conn = await asyncpg.connect(settings.database_url)

    cat_count = await conn.fetchval('SELECT COUNT(*) FROM categories')
    doc_count = await conn.fetchval('SELECT COUNT(*) FROM documents')
    chunk_count = await conn.fetchval('SELECT COUNT(*) FROM document_chunks')

    print(f'Categories: {cat_count}')
    print(f'Documents: {doc_count}')
    print(f'Chunks: {chunk_count}')

    if cat_count > 0 and doc_count > 0 and chunk_count > 0:
        print('✅ Data is populated')
    else:
        print('⚠️ Data may need to be ingested (run --setup)')

    await conn.close()

asyncio.run(check_data())
"
```

**Expected:** Non-zero counts for all tables (after ingestion)

## 6. OpenRouter API Validation

```bash
uv run python -c "
import asyncio
from settings import load_settings
from openai import AsyncOpenAI

async def check_openrouter():
    settings = load_settings()

    # Test embedding endpoint
    client = AsyncOpenAI(
        api_key=settings.openrouter_api_key,
        base_url='https://openrouter.ai/api/v1'
    )

    try:
        response = await client.embeddings.create(
            model=settings.embedding_model,
            input='test'
        )
        dim = len(response.data[0].embedding)
        print(f'✅ Embeddings working ({dim} dimensions)')
    except Exception as e:
        print(f'❌ Embeddings failed: {e}')

asyncio.run(check_openrouter())
"
```

**Expected:** Embeddings working with 1536 dimensions

## 7. Agent Import Validation

```bash
uv run python -c "
try:
    from providers import get_llm_model
    model = get_llm_model()
    print(f'✅ Agent model loaded: {model}')
except Exception as e:
    print(f'❌ Agent model failed: {e}')

try:
    from agents.rag_agent import rag_agent
    print(f'✅ RAG agent imported')
except Exception as e:
    print(f'❌ RAG agent import failed: {e}')
"
```

**Expected:** Both model and agent import successfully

## 8. Hierarchical Query Test

```bash
uv run python -c "
import asyncio
from settings import load_settings
import asyncpg

async def test_hierarchy():
    settings = load_settings()
    conn = await asyncpg.connect(settings.database_url)

    # Test category hierarchy
    result = await conn.fetch('''
        SELECT c.name, c.level, COUNT(d.id) as doc_count
        FROM categories c
        LEFT JOIN documents d ON d.category_id = c.id
        GROUP BY c.id, c.name, c.level
        ORDER BY c.level, c.name
    ''')

    if result:
        print('Category hierarchy:')
        for row in result[:5]:
            indent = '  ' * row['level']
            print(f\"{indent}{row['name']} ({row['doc_count']} docs)\")
        print('✅ Category hierarchy working')
    else:
        print('⚠️ No categories found')

    # Test chunk hierarchy
    chunk_levels = await conn.fetch('''
        SELECT chunk_level, COUNT(*) as count
        FROM document_chunks
        GROUP BY chunk_level
        ORDER BY chunk_level
    ''')

    if chunk_levels:
        print('\\nChunk hierarchy:')
        for row in chunk_levels:
            level_name = ['Document Summary', 'Section', 'Leaf'][row['chunk_level']]
            print(f\"  Level {row['chunk_level']} ({level_name}): {row['count']} chunks\")
        print('✅ Chunk hierarchy working')
    else:
        print('⚠️ No chunks found')

    await conn.close()

asyncio.run(test_hierarchy())
"
```

**Expected:** Both category and chunk hierarchies populated correctly

## 9. Vector Search Test

```bash
uv run python -c "
import asyncio
from settings import load_settings
import asyncpg
from openai import AsyncOpenAI

async def test_vector_search():
    settings = load_settings()
    conn = await asyncpg.connect(settings.database_url)

    # Generate test embedding
    client = AsyncOpenAI(
        api_key=settings.openrouter_api_key,
        base_url='https://openrouter.ai/api/v1'
    )

    response = await client.embeddings.create(
        model=settings.embedding_model,
        input='VPN configuration networking'
    )
    embedding = response.data[0].embedding
    embedding_str = '[' + ','.join(map(str, embedding)) + ']'

    # Test vector search
    results = await conn.fetch('''
        SELECT dc.id, dc.chunk_level,
               1 - (dc.content_embedding <=> \$1::vector) as similarity,
               d.title
        FROM document_chunks dc
        JOIN documents d ON d.id = dc.document_id
        WHERE dc.chunk_level = 2
        ORDER BY dc.content_embedding <=> \$1::vector
        LIMIT 3
    ''', embedding_str)

    if results:
        print('Vector search results:')
        for row in results:
            print(f\"  {row['title']}: {row['similarity']:.3f}\")
        print('✅ Vector search working')
    else:
        print('❌ Vector search returned no results')

    await conn.close()

asyncio.run(test_vector_search())
"
```

**Expected:** Returns top 3 similar chunks with similarity scores

## 10. Summary Report

After all validations complete, provide a summary report with:

| Component | Status |
|-----------|--------|
| Environment (.env) | ✅/❌ |
| Dependencies | ✅/❌ |
| Database Connection | ✅/❌ |
| pgvector Extension | ✅/❌ |
| Schema (3 tables) | ✅/❌ |
| Data Populated | ✅/❌ |
| OpenRouter Embeddings | ✅/❌ |
| Agent Import | ✅/❌ |
| Category Hierarchy | ✅/❌ |
| Chunk Hierarchy | ✅/❌ |
| Vector Search | ✅/❌ |

**Overall Status: PASS/FAIL**

If any component fails, provide:
- Error message
- Suggested fix
- Reference to relevant documentation or INITIAL.md section
