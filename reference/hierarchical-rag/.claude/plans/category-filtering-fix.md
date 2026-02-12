# Fix: Agent Not Using Category Filtering

## Problem Statement

The Hierarchical RAG Agent has a `list_categories` tool and `category_ids` parameter on `search_knowledge_base`, but the agent **never actually uses category filtering**. Despite calling `list_categories` in 7 out of 10 test queries, the agent never passed `category_ids` to filter any search.

This means the "categorical hierarchy" feature is effectively unused - the agent relies entirely on semantic similarity for retrieval.

### Evidence

All observed `search_knowledge_base` calls looked like:
```json
{"query": "SOC2 access control requirements", "top_k": 5}
```

None included `category_ids`:
```json
{"query": "SOC2 access control requirements", "category_ids": [20], "top_k": 5}
```

### Impact

- `list_categories` calls are wasted tokens/latency
- No search space reduction via category pre-filtering
- Categorical hierarchy feature provides no value
- Potential for irrelevant cross-category results in larger knowledge bases

---

## Root Cause Analysis

### 1. Escape Hatch in System Prompt

Current prompt (line 16 in `prompts.py`):
> "If unsure which category, search without filtering first."

This gives the LLM an easy out - it can always claim uncertainty and skip filtering.

### 2. No Concrete Example

The prompt tells the agent to use `category_ids` but never demonstrates HOW:
> "Use 'search_knowledge_base' with relevant category_ids to search within the right scope."

The LLM doesn't see what a filtered search call actually looks like.

### 3. Informational vs Actionable Output

`list_categories` returns:
```
Security (id: 19) - 0 documents
  |-- Compliance (id: 20) - 2 documents
```

The IDs are present but there's no instruction bridging "here's the ID" to "now use it in your next call."

### 4. No Incentive to Filter

Semantic search works well enough (0.83 similarity scores) that the agent gets good results without filtering. There's no penalty for skipping the category step.

---

## Potential Solutions

### Option A: Strengthen System Prompt (Low Effort)

Update the system prompt to:
1. Remove or weaken the escape hatch
2. Add explicit examples showing category filtering
3. Make filtering mandatory for clear topics

**Example revision:**
```
Your retrieval strategy:
1. Use 'list_categories' to see available topics and their IDs.
2. When the user's question maps to a clear category, use 'search_knowledge_base'
   WITH category_ids to scope the search. For example:
   - User asks about "GDPR compliance" → search with category_ids=[20] (Compliance)
   - User asks about "VPN setup" → search with category_ids=[14] (Networking)
   Only search without category_ids if the question truly spans multiple unrelated areas.
3. Use 'get_chunk_context' to expand relevant results.
```

**Pros:** Simple change, no code modifications
**Cons:** LLM may still ignore instructions

### Option B: Few-Shot Examples in System Prompt (Medium Effort)

Add 1-2 complete examples showing the full tool flow:

```
Example flow:
User: "What are the SOC2 access control requirements?"

1. Call list_categories() → See "Security > Compliance (id: 20)"
2. Call search_knowledge_base(query="SOC2 access control", category_ids=[20])
3. Call get_chunk_context(chunk_id=255) for more detail
4. Synthesize answer with citations
```

**Pros:** Demonstrates expected behavior explicitly
**Cons:** Increases prompt size/cost

### Option C: Auto-Suggest Categories in Search Results (Medium Effort)

Modify `search_knowledge_base` to return a suggestion when results come from a single category:

```
Found 5 results (all from Security > Compliance, id: 20).
TIP: For follow-up searches on this topic, use category_ids=[20] to focus results.
```

**Pros:** Teaches the LLM in-context
**Cons:** Doesn't help on first search

### Option D: Remove list_categories, Make Filtering Automatic (Higher Effort)

Remove explicit category filtering. Instead:
1. Use embeddings to auto-detect relevant categories from the query
2. Automatically filter to top 1-2 categories before vector search
3. Remove the cognitive load from the LLM

**Pros:** Guaranteed to work, simpler agent logic
**Cons:** More code changes, loses explicit category exploration

### Option E: Two-Stage Search Tool (Higher Effort)

Replace `search_knowledge_base` with a smarter tool that:
1. First identifies relevant categories from the query
2. Then performs filtered vector search
3. Returns results with category context

**Pros:** Single tool call, always filtered
**Cons:** More complex implementation

---

## Recommended Approach

**Start with Option A + B combined:**
1. Remove the escape hatch ("if unsure, search without filtering")
2. Add 1 concrete example showing category_ids usage
3. Test if behavior improves

If that doesn't work, escalate to Option D (automatic filtering).

---

## Files to Review/Update

### Primary Files

| File | Purpose | Changes Needed |
|------|---------|----------------|
| `src/agents/prompts.py` | System prompt | Remove escape hatch, add examples |
| `src/agents/tools.py` | Tool definitions | Possibly update docstrings to be more directive |

### Secondary Files (if deeper changes needed)

| File | Purpose | Potential Changes |
|------|---------|-------------------|
| `src/db/operations.py` | `search_chunks()` function | Auto-category detection logic |
| `src/agents/rag_agent.py` | Agent creation | Few-shot message injection |

### Reference Files

| File | Purpose |
|------|---------|
| `.claude/testing-results.md` | Documents the current behavior |
| `src/db/operations.py:345-425` | `search_chunks()` - already supports category_ids filtering |

---

## Validation Plan

After implementing changes:

1. Run the same 10 test queries from `testing-results.md`
2. Grep for `category_ids` in tool call arguments
3. Success criteria: At least 50% of searches should use category filtering when topic is clear
4. Document before/after comparison

---

## Notes

- The structural hierarchy (`get_chunk_context`) is working well - don't break this
- The `category_ids` filtering in `search_chunks()` SQL is already implemented and tested
- The issue is purely at the LLM instruction/prompting level
