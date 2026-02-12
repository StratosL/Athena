---
title: Elasticsearch Semantic Search
tags:
  - research
  - elasticsearch
  - semantic-search
  - elser
  - ai
created: 2026-02-04
updated: 2026-02-04
---

# Elasticsearch Semantic Search

## Overview

Elasticsearch now supports native semantic search through **ELSER** (Elastic Learned Sparse EncodeR), a retrieval model trained by Elastic that generates sparse vector representations of text. Unlike dense vector approaches that require separate embedding pipelines, ELSER runs as an inference endpoint inside Elasticsearch itself.

## How ELSER Works

ELSER converts text into sparse vectors where each dimension corresponds to a token in the model's vocabulary. The key advantage over BM25 is that ELSER expands queries with semantically related terms — a search for "authentication" will also match documents about "login", "credentials", and "JWT" without explicit keyword overlap.

### Architecture

The `semantic_text` field type handles inference automatically:

```json
{
  "mappings": {
    "properties": {
      "content_semantic": {
        "type": "semantic_text",
        "inference_id": ".elser-2-elastic"
      }
    }
  }
}
```

Documents indexed into a `semantic_text` field are automatically passed through the ELSER model at index time. At query time, the search query is also passed through the model before matching.

## Comparison with Dense Vectors

| Feature | ELSER (Sparse) | Dense Vectors |
|---------|----------------|---------------|
| Hosting | Built-in ES | External API |
| Latency | Lower | Higher |
| Cost | Included | Per-token billing |
| Accuracy | Strong for English | Model-dependent |

## Relevance to [[Helios v2 Roadmap]]

For the Athena project, ELSER is ideal because it eliminates the need for an external embedding service. All semantic search happens within the [[API Refactoring]] layer, keeping the architecture simple. This aligns with the research on [[API Versioning Best Practices]] for maintaining clean service boundaries.

## Open Questions

- How does ELSER perform on mixed technical/natural language content?
- What's the reindexing cost when upgrading ELSER model versions?
- Can we combine ELSER with BM25 in a hybrid search for better recall?
