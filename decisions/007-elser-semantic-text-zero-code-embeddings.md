# ADR-007: ELSER v2 with `semantic_text` for Zero-Code Embeddings

**Date:** 2026-02-12
**Status:** Accepted
**Context:** Athena needs semantic search over Obsidian notes in Elasticsearch

---

## Problem

Keyword search misses conceptually related content. Searching "how to handle user login" should find a note titled "Authentication Module" that discusses JWT patterns — even if the word "login" never appears. We need vector/semantic search, which requires an embedding model.

## Options

### Option A: Client-Side Embeddings (OpenAI, Cohere, etc.) — Rejected

Call an embedding API from the indexer, store vectors in ES `dense_vector` fields.

- **Pro:** Model choice flexibility, well-documented patterns
- **Con:** API cost per note, embedding code in the indexer, re-embedding on model changes, chunking logic needed for long notes

### Option B: Self-Hosted ELSER (`.elser-2-elasticsearch`) — Rejected

Deploy ELSER model on ES ML nodes, use `text_expansion` queries.

- **Pro:** No external API calls, runs on own infrastructure
- **Con:** Requires ML node configuration, memory allocation, manual model deployment. Serverless doesn't support self-hosted models.

### Option C: Elastic-Hosted ELSER with `semantic_text` (Selected)

Use the built-in `.elser-2-elastic` inference endpoint with ES's `semantic_text` field type.

- **Pro:** Zero embedding code. ES handles chunking, inference, and sparse vector storage at index time. Available out-of-the-box on Serverless.
- **Con:** Locked into Elastic's model. No fine-tuning. Sparse vectors (not dense) — different trade-off profile.

## Decision

Use `semantic_text` field type referencing `.elser-2-elastic`:

```json
{
  "content_semantic": {
    "type": "semantic_text",
    "inference_id": ".elser-2-elastic"
  }
}
```

The indexer sets `content_semantic = content` (same text) and ES handles everything else.

## Consequences

- **Zero embedding code** — no chunking logic, no API calls, no vector math
- Indexer is ~100 lines simpler than it would be with client-side embeddings
- ELSER v2 produces sparse vectors (learned sparse retrieval) — excellent for English text, strong at semantic expansion
- Semantic search quality validated: "How to handle user login" → Authentication Module at #1 despite zero keyword overlap
- Locked into Elastic ecosystem — moving to another vector DB would require rewriting the embedding pipeline
- `semantic_text` handles chunking automatically for long notes — no manual chunk size tuning
- Inference happens at index time, not query time — queries are fast
