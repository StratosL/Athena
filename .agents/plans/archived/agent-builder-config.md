# Feature: Agent Builder Configuration — System Prompt + ES|QL Tool Definitions

The following plan should be complete, but its important that you validate documentation and codebase patterns and task sanity before you start implementing.

Pay special attention to naming of existing utils types and models. Import from the right files etc.

## Feature Description

Write the Athena Agent Builder system prompt (`agent-config/system-prompt.md`) and define all 5 ES|QL tool specifications (`agent-config/tools/`) plus 1 index search tool. These are the configuration artifacts that the user pastes into Elastic Agent Builder's Kibana UI to make the Athena agent functional. Without these, the agent is a shell — it has an MCP server with 13 tools but no persona, no behavioral rules, and no ES|QL query tools.

The system prompt defines **who Athena is** and **how she behaves** — Eisenhower classification, 1-3-5 daily planning, human-in-the-loop confirmation, tool routing logic, and output formatting. The ES|QL tools give the agent read-only analytical access to the Elasticsearch indices (`athena-notes`, `athena-conversations`) for semantic search, tag filtering, and aggregations.

## User Story

As a developer configuring Athena in Elastic Agent Builder,
I want a production-ready system prompt and ES|QL tool definitions,
So that the agent has the correct persona, behavioral rules, and Elasticsearch query capabilities for the demo.

## Problem Statement

`agent-config/system-prompt.md` is a placeholder with HTML comments. `agent-config/tools/` contains only a `.gitkeep`. The MCP server is built (13 tools), the vault is indexed (17 notes in ES), but the agent has no brain — no instructions, no ES|QL tools, no search capability.

## Solution Statement

Create two deliverables:
1. A comprehensive system prompt (~300-400 lines) in markdown that defines Athena's persona, tool routing, Eisenhower classification, 1-3-5 planning workflow, human-in-the-loop rules, and output formatting.
2. Six JSON tool definition files (5 ES|QL + 1 index search) ready to paste into Agent Builder's tool creation UI or submit via the Kibana API.

## Feature Metadata

**Feature Type**: New Capability
**Estimated Complexity**: Medium
**Primary Systems Affected**: `agent-config/system-prompt.md`, `agent-config/tools/` (6 new JSON files), `agent-config/setup-guide.md` (update)
**Dependencies**: Elasticsearch indices must exist (`athena-notes`, `athena-conversations`), MCP server tools must be implemented (already done)

---

## CONTEXT REFERENCES

### Relevant Codebase Files — MUST READ BEFORE IMPLEMENTING

**Existing architecture context:**

- `PRD.md` (lines 1-30) — Executive summary, mission, core principles. Defines Athena's purpose and human-in-the-loop philosophy.
- `PRD.md` (lines 293-371) — Complete tool inventory: ES|QL tools (5), MCP vault tools (3 with 13 operations), MCP Artemis tools (7), MCP knowledge tools (1), MCP research tools (2). Critical for writing tool routing logic in the system prompt.
- `PRD.md` (lines 168-212) — Architecture: dual-path knowledge access (ES for semantic search, vault for real-time read/write). Defines when agent should use which path.
- `PRD.md` (lines 112-164) — User stories US-1 through US-10. Each maps to specific tool combinations the system prompt must encode as workflow patterns.

**Elasticsearch index mappings (defines what ES|QL tools can query):**

- `indexer/src/mappings.py` (lines 1-36) — Exact field names and types for `athena-notes` index: `title` (text+keyword), `content` (text), `content_semantic` (semantic_text/ELSER), `tags` (keyword[]), `note_type` (keyword), `path` (keyword), `vault_relative_path` (keyword), `word_count` (integer), `created_at` (date), `updated_at` (date), `indexed_at` (date), `checksum` (keyword). Also `athena-conversations`: `summary` (text), `summary_semantic` (semantic_text/ELSER), `topics` (keyword[]), `extracted_tasks` (text[]), `task_ids_created` (keyword[]), `timestamp` (date).

**MCP tools (the agent needs to know how to invoke these):**

- `mcp-server/src/tools/vault.py` (lines 36-88) — `vault_query` tool: operations `list_structure`, `search_content`, `search_by_metadata`, `recent_changes`. Parameters: `operation`, `query`, `folder`, `tags`, `date_range_days`, `limit`, `recursive`.
- `mcp-server/src/tools/vault.py` (lines 91-134) — `vault_read` tool: operations `read_note`, `read_multiple`, `daily_note`. Parameters: `operation`, `path`, `paths`, `date`.
- `mcp-server/src/tools/vault.py` (lines 137-228) — `vault_manage` tool: operations `create_note`, `append_note`, `edit_note`, `move_note`, `delete_note`, `create_folder`. Parameters include `confirm_destructive` for deletes.
- `mcp-server/src/tools/artemis.py` (lines 23-184) — 7 Artemis tools: `artemis_create_task` (title, quadrant, description, due_date), `artemis_list_tasks` (quadrant, status), `artemis_complete_task` (task_id), `artemis_get_daily_plan`, `artemis_assign_to_plan` (plan_id, task_id, slot), `artemis_get_analytics` (period), `artemis_start_pomodoro` (task_id).
- `mcp-server/src/tools/knowledge.py` (lines 19-54) — `save_conversation_summary` tool: summary, topics (CSV), extracted_tasks (CSV), task_ids_created (CSV).
- `mcp-server/src/tools/research.py` (lines 22-95) — `web_search` (query, max_results), `fetch_url` (url).

**Sample vault content (for understanding demo scenarios):**

- `sample-vault/Projects/API Refactoring.md` — 7 extractable tasks (5 checkboxes, 1 TODO, 1 action item). Primary demo note for US-3 (task extraction).
- `sample-vault/Daily Notes/2026-02-12.md` — Today's priorities with P0/P1/P2 classification. Demo note for US-5 (daily planning).
- `sample-vault/Meeting Notes/Sprint Review 2026-02-07.md` — 5 numbered action items. Demo note for meeting follow-up.

**Reference system prompts (patterns to follow):**

- `reference/obsidian-ai-agent/app/core/agents/base.py` (lines 32-217) — Paddy's system prompt. **Key patterns**: structured tool selection matrix ("Discover → query_tool, Read → context_tool, Write → manager_tool"), workflow patterns (Search→Modify, Content Creation, Research), Action-Response Parity Rule, destructive operation guardrails, token-aware guidance. This is our primary blueprint for structure.
- `reference/obsidian-productivity-agent/backend_agent_api/prompt.py` — Simpler prompt: Goal → Tool Instructions → Output Format → Misc. Memory-first approach, tag-based navigation, Obsidian link formatting.

### New Files to Create

| File | Purpose |
|------|---------|
| `agent-config/system-prompt.md` | Complete Athena system prompt for Agent Builder `configuration.instructions` |
| `agent-config/tools/search-notes.json` | ES\|QL tool: semantic + full-text search across notes |
| `agent-config/tools/get-recent-notes.json` | ES\|QL tool: recently modified notes |
| `agent-config/tools/get-notes-by-tag.json` | ES\|QL tool: filter notes by tag |
| `agent-config/tools/count-notes-by-tag.json` | ES\|QL tool: tag distribution statistics |
| `agent-config/tools/get-conversation-history.json` | ES\|QL tool: search past conversation summaries |
| `agent-config/tools/notes-semantic-search.json` | Index search tool: dynamic natural-language search on athena-notes |

### Files to Update

| File | Change |
|------|--------|
| `agent-config/setup-guide.md` | Replace placeholder comments with actual step-by-step setup instructions |

### Relevant Documentation — READ BEFORE IMPLEMENTING

- [Agent Builder Prompt Engineering](https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/prompt-engineering)
  - Recommended structure: `# Goal / # Steps / # Guardrails`
  - Decision framework: global behavior → instructions, trigger criteria → tool descriptions
  - Start light, iterate; keep static for prompt caching

- [ES|QL Tools in Agent Builder](https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/tools/esql-tools)
  - Tool JSON schema: `{id, type: "esql", description, tags, configuration: {query, params}}`
  - Parameter syntax: `?param_name` in ES|QL queries
  - Params: `{name: {type, description}}`

- [Index Search Tools in Agent Builder](https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/tools/index-search-tools)
  - Tool JSON: `{id, type: "index_search", description, tags, configuration: {pattern, row_limit, custom_instructions}}`
  - Dynamically generates ES|QL from natural language

- [Create Tool API](https://www.elastic.co/docs/api/doc/kibana/operation/operation-post-agent-builder-tools)
  - `POST /api/agent_builder/tools` with headers: `Authorization: ApiKey`, `kbn-xsrf: true`, `Content-Type: application/json`

- [Create Agent API](https://www.elastic.co/docs/api/doc/kibana/operation/operation-post-agent-builder-agents)
  - `POST /api/agent_builder/agents` — `configuration.instructions` = system prompt, `configuration.tools[0].tool_ids` = array of tool IDs

- [MCP Tools in Agent Builder](https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/tools/mcp-tools)
  - Create MCP Connector in Stack Management → Connectors
  - Import tools from MCP server with namespace prefix (e.g., `athena.vault_query`)
  - Tools auto-populate from MCP server metadata

- [ES|QL Reference — Search Functions](https://www.elastic.co/docs/reference/query-languages/esql/functions-operators/search-functions)
  - `MATCH(field, query)` for full-text search, `MATCH(field, query, {"boost": N})` for boosted
  - `METADATA _score` after FROM for relevance scoring
  - `content_semantic` (semantic_text) works with MATCH for ELSER-powered semantic search

- [ES|QL Reference — Multivalue Functions](https://www.elastic.co/docs/reference/query-languages/esql/functions-operators/mv-functions)
  - `MV_EXPAND tags` to explode keyword arrays for filtering/aggregation
  - Required before `WHERE tags == ?tag` or `STATS ... BY tags`

- [ES|QL Reference — Date-Time Functions](https://www.elastic.co/docs/reference/query-languages/esql/functions-operators/date-time-functions)
  - `NOW() - 7 day` for relative date ranges
  - `TO_TIMEDURATION(?param)` for parameterized time ranges (since time span literals can't contain `?params`)

### Patterns to Follow

**System prompt structure** (from Elastic Agent Builder best practices):
```
# Goal
[High-level objective — who Athena is, what she does]

# Steps
[Preferred reasoning sequence — how to approach queries]

# Guardrails
[Constraints, prohibited actions, safety rules]
```

**Tool routing** (from Paddy's system prompt):
```
## Tool Selection
- **Discover/Search** → Use ES|QL search_notes or vault_query
- **Read Full Content** → Use vault_read (MCP)
- **Create/Edit Notes** → Use vault_manage (MCP)
- **Task Management** → Use artemis_* tools (MCP)
- **Web Research** → Use web_search + fetch_url (MCP)
```

**Workflow patterns** (from Paddy):
```
### Search → Extract → Create Pattern
1. Search notes with ES|QL or vault_query
2. Read full note content with vault_read
3. Identify tasks through conversation
4. Present tasks with Eisenhower classification
5. Wait for user confirmation
6. Create confirmed tasks with artemis_create_task
```

**ES|QL tool JSON format** (from Agent Builder docs):
```json
{
  "id": "notes.search_by_content",
  "type": "esql",
  "description": "Description for LLM to decide when to use this tool",
  "tags": ["notes", "search"],
  "configuration": {
    "query": "FROM athena-notes METADATA _score | WHERE MATCH(content, ?query) | SORT _score DESC | LIMIT ?limit",
    "params": {
      "query": {
        "type": "string",
        "description": "Natural language or keyword search query"
      },
      "limit": {
        "type": "integer",
        "description": "Maximum number of results"
      }
    }
  }
}
```

**Eisenhower Matrix classification** (from PRD):
```
Q1 (Do First): Urgent + Important — deadlines, crises, blocking issues
Q2 (Schedule): Not Urgent + Important — planning, learning, relationship-building (DEFAULT when uncertain)
Q3 (Delegate): Urgent + Not Important — interruptions, some meetings, some emails
Q4 (Eliminate): Not Urgent + Not Important — busywork, time-wasters
```

**1-3-5 Rule** (from PRD):
```
Daily plan slots:
- 1 Major task (most important, requires deep focus)
- 3 Medium tasks (significant but bounded)
- 5 Small tasks (quick wins, admin, follow-ups)
```

---

## IMPLEMENTATION PLAN

### Phase 1: System Prompt

Write `agent-config/system-prompt.md` — the complete Athena persona and behavioral rules. This is the longest artifact. Structure follows Agent Builder best practices: Goal → available tools → tool selection → workflows → classification rules → guardrails → output formatting.

### Phase 2: ES|QL Tool Definitions

Create 5 JSON files in `agent-config/tools/`, each defining an ES|QL tool with query template and parameter schemas. Plus 1 index search tool for dynamic semantic search.

### Phase 3: Setup Guide

Replace the placeholder `agent-config/setup-guide.md` with actual step-by-step instructions for configuring everything in Kibana.

### Phase 4: Validation

Verify all JSON is valid, ES|QL queries are syntactically correct, and the system prompt references the correct tool names.

---

## STEP-BY-STEP TASKS

### Task 1: CREATE `agent-config/system-prompt.md`

Write the complete Athena system prompt. This is plain text/markdown that goes into Agent Builder's `configuration.instructions` field.

**Structure** (follow this exact outline):

```markdown
# Athena — Second Brain Orchestrator

## Identity

[Who Athena is — persona, tone, purpose. Conversational, knowledgeable, proactive but respectful of user authority. References the Obsidian vault as "your vault" or "your notes".]

## Goal

[High-level objective: bridge knowledge (Obsidian vault) with action (Artemis productivity app). Help users find information, extract tasks, plan their day, capture ideas, and research topics.]

## Available Tools

### Elasticsearch Tools (ES|QL — Read-Only Analytics)
[List all 5 ES|QL tools + 1 index search tool with brief descriptions]

### MCP Tools — Vault (Direct Filesystem Access)
[List vault_query, vault_read, vault_manage with operations]

### MCP Tools — Artemis (Task Management)
[List all 7 Artemis tools]

### MCP Tools — Knowledge (Memory)
[List save_conversation_summary]

### MCP Tools — Research (Web)
[List web_search, fetch_url]

## Tool Selection Guide

[Decision matrix — when to use which tool. Key routing decisions:]
- **Semantic search (by meaning)** → ES|QL `search_notes` or index search tool
- **Keyword/metadata search** → MCP `vault_query` (search_content, search_by_metadata)
- **Read note content** → MCP `vault_read` (read_note, read_multiple, daily_note)
- **Browse vault structure** → MCP `vault_query` (list_structure)
- **Create/edit/delete notes** → MCP `vault_manage` (with confirmation)
- **Task operations** → MCP `artemis_*` tools
- **Analytics/trends** → ES|QL count/aggregate tools OR MCP `artemis_get_analytics`
- **Past conversations** → ES|QL `get_conversation_history`
- **Web research** → MCP `web_search` + `fetch_url`

[Key principle: Use ES|QL for analytical/semantic queries. Use vault MCP tools for real-time reads and writes.]

## Workflow Patterns

### Pattern 1: Knowledge Search
[User asks about a topic → search_notes (ES|QL) for semantic results → vault_read to get full content → present with citations]

### Pattern 2: Task Extraction
[User asks to extract tasks from a note → vault_read the note → identify action items → classify each with Eisenhower quadrant → present numbered list → wait for user confirmation → create approved tasks with artemis_create_task]

### Pattern 3: Daily Planning
[User says "plan my day" → artemis_list_tasks (status=pending) → artemis_get_daily_plan → suggest 1-3-5 assignment → wait for confirmation → assign via artemis_assign_to_plan]

### Pattern 4: Idea Capture
[User shares an idea → propose vault note structure → wait for confirmation → vault_manage create_note with tags]

### Pattern 5: Research & Save
[User asks to research a topic → web_search → fetch_url for detailed content → summarize → offer to save as vault note]

### Pattern 6: Productivity Check-in
[User asks "how's my week?" → artemis_get_analytics → interpret numbers → provide narrative insight]

### Pattern 7: Conversation Memory
[After productive conversation → save_conversation_summary with topics and any task IDs created]

## Eisenhower Matrix Classification

[Detailed classification rules for task proposals:]

When classifying tasks into Eisenhower quadrants, apply these criteria:

**Q1 — Do First (Urgent + Important)**
- Has a deadline within 48 hours
- Blocks other people or workstreams
- Explicitly marked as urgent/critical/P0 in the note
- Bug fixes, outages, or customer-facing issues

**Q2 — Schedule (Not Urgent + Important)** ← DEFAULT
- Strategic work: planning, architecture, learning, skill development
- Important but no immediate deadline
- Relationship-building, reviews, process improvements
- When uncertain, default to Q2 — most knowledge work is important but not urgent

**Q3 — Delegate (Urgent + Not Important)**
- Time-sensitive but low strategic value
- Routine meetings that could be emails
- Requests from others that don't align with user's goals
- Admin tasks with soft deadlines

**Q4 — Eliminate (Not Urgent + Not Important)**
- Busywork with no clear outcome
- "Nice to have" that nobody asked for
- Duplicate efforts or already-resolved items

**Classification examples from the vault:**
- "Finish API search endpoint — must be code-complete today" → Q1 (deadline today, blocks sprint demo)
- "Review rate limiting strategy before launch" → Q2 (important design decision, no immediate deadline)
- "Set up API integration test suite" → Q2 (important infrastructure, no urgent deadline)
- "Sketch voice commands architecture diagram for next week" → Q2 (future-oriented planning)

## 1-3-5 Daily Planning Rule

When helping with daily planning:
- **1 Major task**: The single most important thing to accomplish today. Requires deep focus. Choose from Q1 or top Q2 items.
- **3 Medium tasks**: Significant but bounded work. Can be completed in 1-2 hours each.
- **5 Small tasks**: Quick wins, admin, follow-ups. Under 30 minutes each.

Steps:
1. List all pending tasks from Artemis (artemis_list_tasks with status=pending)
2. Get today's plan (artemis_get_daily_plan)
3. If plan already has tasks, show what's assigned and ask if changes are needed
4. If plan is empty, analyze pending tasks by quadrant and deadline
5. Propose a 1-3-5 assignment with reasoning for each choice
6. Wait for user to confirm or adjust
7. Assign confirmed tasks via artemis_assign_to_plan

## Guardrails

### Human-in-the-Loop (CRITICAL)
- **NEVER** create tasks in Artemis without presenting them to the user first and getting explicit approval
- **NEVER** create, edit, or delete vault notes without describing the action and getting confirmation
- **NEVER** auto-assign tasks to the daily plan without presenting the proposed plan first
- When proposing tasks, ALWAYS present as a numbered list with title, suggested quadrant, and reasoning
- If user says "skip", "remove", or "change" any item — adjust accordingly before proceeding

### Destructive Operations
- Delete operations require `confirm_destructive=true` — always explain what will be deleted and ask for explicit "yes" before proceeding
- Move operations: confirm the destination before moving
- Edit operations: show the old text and new text before applying

### Search Strategy
- For broad or conceptual questions → start with ES|QL semantic search (search_notes)
- For specific note lookup → use vault_read with the note path
- For vault structure/browsing → use vault_query (list_structure)
- If ES|QL search returns no results → fall back to vault_query (search_content) for keyword search
- Never claim notes don't exist without checking both search paths

### Error Recovery
- If a tool returns an error, explain the error to the user and suggest alternatives
- If Artemis is unreachable, inform the user and offer to help with vault-only operations
- If Elasticsearch is unavailable, fall back to vault_query for direct filesystem search
- Never claim an action succeeded without checking the tool result

### Memory & Context
- After productive conversations that involve decisions, task creation, or significant discussion, use save_conversation_summary to preserve context
- Include topic keywords, any task descriptions extracted, and Artemis task IDs created
- This enables future conversations to reference past decisions

## Output Formatting

- Use numbered lists when presenting task proposals or search results
- Use markdown formatting (bold, headers, bullet points) for structure
- When citing notes, include the vault path: e.g., "From **Projects/API Refactoring.md**:"
- When presenting Eisenhower classification, use the format: `[Q1 — Do First]` or `[Q2 — Schedule]`
- Keep responses concise — summarize notes rather than dumping full content unless user asks for it
- For daily plan proposals, use a clear table or structured format showing major/medium/small slots
- When interpreting analytics, provide narrative insight, not just raw numbers ("Your completion rate improved 15% this week — the daily planning seems to be working")
```

**Key behavioral rules to encode** (from PRD Section 2 + orchestrator plan):
1. Always confirm before acting on Artemis
2. Search first — check knowledge base before responding from memory
3. Eisenhower-literate — correctly classify Q1-Q4, default to Q2 when uncertain
4. 1-3-5 aware — understand daily plan slot limits and types
5. Save insights — after productive conversations, save summaries
6. Concise and structured — numbered lists for proposals, narrative for analytics

**PATTERN**: Follow Paddy's prompt structure (reference/obsidian-ai-agent base.py lines 32-217) for tool listing, selection matrix, workflow patterns, and safety guidelines. Follow Elastic's recommended `# Goal / # Steps / # Guardrails` structure.

**GOTCHA**: The system prompt is a plain text string in `configuration.instructions`. Markdown formatting is fine — the LLM interprets it. But don't include code blocks with `---` YAML frontmatter (it's not a note, it's a prompt).

**GOTCHA**: Tool names in the system prompt must match exactly what's registered in Agent Builder. ES|QL tools will have IDs like `notes.search_notes`. MCP tools will be namespaced like `athena.vault_query`. Use descriptive names without worrying about exact IDs — the tool descriptions in Agent Builder handle routing. The system prompt should use human-readable names.

**GOTCHA**: Don't make the prompt too long. Agent Builder has a base system prompt layer. Our instructions add on top. Keep under 400 lines. Prioritize clarity over completeness.

**VALIDATE**: Read through the prompt and verify every tool mentioned exists in the MCP server or ES|QL tool definitions. Verify Eisenhower examples match sample vault content. Verify 1-3-5 rules match PRD.

---

### Task 2: CREATE `agent-config/tools/search-notes.json`

The primary search tool. Uses hybrid semantic (ELSER) + full-text (BM25) scoring.

```json
{
  "id": "notes.search_notes",
  "type": "esql",
  "description": "Search Obsidian vault notes by meaning using semantic search (ELSER) combined with keyword matching. Use this when the user asks about a topic, wants to find notes related to a concept, or asks 'what did I write about X?'. Returns note titles, paths, tags, and relevance scores. Prefer this over vault_query for broad or conceptual searches.",
  "tags": ["notes", "search", "semantic"],
  "configuration": {
    "query": "FROM athena-notes METADATA _score | WHERE MATCH(content_semantic, ?query, {\"boost\": 0.7}) OR MATCH(content, ?query, {\"boost\": 0.3}) | KEEP title, vault_relative_path, tags, note_type, word_count, updated_at, _score | SORT _score DESC | LIMIT ?limit",
    "params": {
      "query": {
        "type": "string",
        "description": "Natural language search query describing what the user is looking for. Can be a question, topic, or keywords."
      },
      "limit": {
        "type": "integer",
        "description": "Maximum number of results to return. Default 5 for focused searches, up to 10 for broad exploration."
      }
    }
  }
}
```

**GOTCHA**: `content_semantic` is a `semantic_text` field — ELSER inference happens at query time automatically when using MATCH. The `{"boost": 0.7}` weights semantic results higher than keyword matches.

**GOTCHA**: `KEEP` clause limits returned fields to prevent context window overflow. Don't return `content` or `content_semantic` (too large) — the agent can use `vault_read` to get full content after finding relevant notes.

**GOTCHA**: `vault_relative_path` (not `path`) is the correct field name for the vault-relative file path in the index mapping.

**VALIDATE**: Verify the field names match `indexer/src/mappings.py` exactly. Verify ES|QL syntax is valid (FROM → WHERE → KEEP → SORT → LIMIT pipeline).

---

### Task 3: CREATE `agent-config/tools/get-recent-notes.json`

Temporal query — recently modified notes.

```json
{
  "id": "notes.get_recent_notes",
  "type": "esql",
  "description": "Get the most recently modified notes from the Obsidian vault. Use this when the user asks 'what have I been working on?', 'show me recent notes', or wants to see what changed in the last few days. Returns notes sorted by modification date.",
  "tags": ["notes", "recent", "temporal"],
  "configuration": {
    "query": "FROM athena-notes | WHERE updated_at >= NOW() - TO_TIMEDURATION(?time_range) | KEEP title, vault_relative_path, tags, note_type, word_count, updated_at | SORT updated_at DESC | LIMIT ?limit",
    "params": {
      "time_range": {
        "type": "string",
        "description": "How far back to look. Format: 'N hours'. Examples: '168 hours' for 7 days, '72 hours' for 3 days, '24 hours' for today. Default: '168 hours' (7 days)."
      },
      "limit": {
        "type": "integer",
        "description": "Maximum number of notes to return. Default 10."
      }
    }
  }
}
```

**GOTCHA**: Time span literals like `7 day` cannot contain `?params`, so we use `TO_TIMEDURATION(?time_range)` where the agent passes a string like `"168 hours"`. This is a documented pattern from the ES|QL docs.

**GOTCHA**: The agent needs to know the format in the param description — "168 hours" not "7 days" — because `TO_TIMEDURATION` requires specific unit strings.

**VALIDATE**: Verify `TO_TIMEDURATION` accepts the "N hours" format. Verify `updated_at` field exists in mappings.

---

### Task 4: CREATE `agent-config/tools/get-notes-by-tag.json`

Filter notes by tag — uses `MV_EXPAND` for keyword array handling.

```json
{
  "id": "notes.get_notes_by_tag",
  "type": "esql",
  "description": "Find all notes with a specific tag from the Obsidian vault. Use this when the user asks about notes tagged with a topic (e.g., 'show me all notes tagged api' or 'what notes are about productivity?'). Tags are lowercase keywords extracted from note frontmatter.",
  "tags": ["notes", "tags", "filter"],
  "configuration": {
    "query": "FROM athena-notes | MV_EXPAND tags | WHERE tags == ?tag | KEEP title, vault_relative_path, tags, note_type, word_count, updated_at | SORT updated_at DESC | LIMIT 20",
    "params": {
      "tag": {
        "type": "keyword",
        "description": "The exact tag to filter by, lowercase. Examples: 'api', 'productivity', 'helios', 'meeting', 'idea'. Use count_notes_by_tag first if unsure which tags exist."
      }
    }
  }
}
```

**GOTCHA**: `tags` is a keyword array field. Must use `MV_EXPAND tags` to explode into rows before filtering with `WHERE tags == ?tag`. Without `MV_EXPAND`, the equality check won't work on multivalue fields.

**GOTCHA**: No `?limit` param here — hardcoded to 20. Tag queries are typically bounded and the agent doesn't need to control the limit for this simple filter.

**VALIDATE**: Verify `MV_EXPAND` → `WHERE ==` pattern works for keyword arrays in ES|QL.

---

### Task 5: CREATE `agent-config/tools/count-notes-by-tag.json`

Tag distribution statistics — no parameters needed.

```json
{
  "id": "notes.count_notes_by_tag",
  "type": "esql",
  "description": "Get the distribution of tags across all notes in the Obsidian vault. Returns each tag and how many notes use it, sorted by count. Use this to understand the vault's topic coverage, discover what tags exist, or answer 'what topics do I write about most?'. No parameters needed.",
  "tags": ["notes", "tags", "analytics"],
  "configuration": {
    "query": "FROM athena-notes | MV_EXPAND tags | STATS note_count = COUNT(*) BY tags | SORT note_count DESC | LIMIT 30",
    "params": {}
  }
}
```

**GOTCHA**: This is a static query with no parameters. The tool definition still needs an empty `params` object. The agent simply calls this tool to get the tag distribution.

**GOTCHA**: `MV_EXPAND tags` is required before `STATS ... BY tags` to count each tag occurrence correctly across multivalue fields.

**VALIDATE**: Verify `STATS COUNT(*) BY tags` produces the expected tag → count mapping.

---

### Task 6: CREATE `agent-config/tools/get-conversation-history.json`

Search past conversation summaries in the `athena-conversations` index.

```json
{
  "id": "conversations.get_history",
  "type": "esql",
  "description": "Search past conversation summaries stored in Elasticsearch. Use this when the user asks 'what did we discuss about X?', 'do you remember when we talked about Y?', or wants to recall decisions from previous sessions. Searches semantically across conversation summaries.",
  "tags": ["conversations", "memory", "search"],
  "configuration": {
    "query": "FROM athena-conversations METADATA _score | WHERE MATCH(summary_semantic, ?topic) | KEEP summary, topics, extracted_tasks, task_ids_created, timestamp, _score | SORT _score DESC | LIMIT ?limit",
    "params": {
      "topic": {
        "type": "string",
        "description": "Topic or subject to search past conversations for. Can be natural language."
      },
      "limit": {
        "type": "integer",
        "description": "Maximum conversation summaries to return. Default 5."
      }
    }
  }
}
```

**GOTCHA**: This queries `athena-conversations`, not `athena-notes`. Different index, different fields.

**GOTCHA**: `summary_semantic` is the ELSER-powered semantic_text field for conversation summaries.

**VALIDATE**: Verify field names match `indexer/src/mappings.py` CONVERSATIONS_INDEX_MAPPING.

---

### Task 7: CREATE `agent-config/tools/notes-semantic-search.json`

An index search tool for dynamic natural-language search. This complements the ES|QL tools by giving the agent a flexible search capability that can handle queries the predefined ES|QL templates don't cover.

```json
{
  "id": "notes.semantic_search",
  "type": "index_search",
  "description": "Perform intelligent natural language search over the Obsidian vault notes index. Use this for complex or nuanced searches that go beyond simple keyword matching. This tool dynamically generates search queries and can combine multiple search criteria. For simple topic searches, prefer the search_notes ES|QL tool instead.",
  "tags": ["notes", "search", "semantic", "dynamic"],
  "configuration": {
    "pattern": "athena-notes",
    "row_limit": 10,
    "custom_instructions": "This index contains Obsidian vault notes with these key fields: title (note title), content (full markdown body), content_semantic (ELSER semantic embeddings of content), tags (keyword array of topic tags), note_type (project/idea/meeting/daily/research/note), vault_relative_path (file path like 'Projects/API Refactoring.md'), word_count (integer), created_at and updated_at (dates). Always include title, vault_relative_path, tags, and note_type in results. For semantic queries, prefer the content_semantic field."
  }
}
```

**GOTCHA**: Index search tools don't have `params` — they dynamically generate queries based on the agent's natural language understanding. The `custom_instructions` field guides query generation.

**GOTCHA**: `row_limit` caps results at 10 to prevent context window overflow.

**VALIDATE**: Verify `pattern: "athena-notes"` matches the actual index name.

---

### Task 8: UPDATE `agent-config/setup-guide.md`

Replace the HTML comment placeholder with actual step-by-step instructions.

**Content outline:**

```markdown
# Agent Builder Setup Guide

## Prerequisites
- Elastic Cloud Serverless account with active trial
- `athena-notes` and `athena-conversations` indices created and populated
- MCP server running (locally or deployed) with ngrok/public URL
- Artemis backend running on port 8000

## Step 1: Configure LLM Connector
1. Go to Kibana → Stack Management → Connectors
2. Create Connector → OpenAI (or Anthropic)
3. Set API key and model (recommend GPT-4o or Claude Sonnet 4)
4. Test connection

## Step 2: Create ES|QL Tools
1. Go to Agent Builder → Tools → New Tool
2. For each JSON file in `agent-config/tools/`:
   a. Select type: ES|QL (or Index Search for notes-semantic-search.json)
   b. Paste the configuration
   c. Save
3. Or use the API: POST /api/agent_builder/tools with the JSON body

## Step 3: Register MCP Server
1. Go to Stack Management → Connectors → Create Connector → MCP
2. Set Server URL to your MCP server endpoint (e.g., https://your-ngrok-url.ngrok.io)
3. Test connection (should list 13 tools)
4. Go to Agent Builder → Tools → New Tool → MCP
5. Select the MCP connector
6. Import all tools with namespace prefix "athena"
7. This creates: athena.vault_query, athena.vault_read, athena.vault_manage, etc.

## Step 4: Create the Athena Agent
1. Go to Agent Builder → Agents → Create Agent
2. Name: "Athena"
3. Description: "Second brain orchestrator — bridges your Obsidian vault with Artemis productivity"
4. System prompt: Copy contents of `agent-config/system-prompt.md`
5. Add all tools:
   - ES|QL: notes.search_notes, notes.get_recent_notes, notes.get_notes_by_tag, notes.count_notes_by_tag, conversations.get_history
   - Index search: notes.semantic_search
   - MCP (athena.*): vault_query, vault_read, vault_manage, artemis_create_task, artemis_list_tasks, artemis_complete_task, artemis_get_daily_plan, artemis_assign_to_plan, artemis_get_analytics, artemis_start_pomodoro, save_conversation_summary, web_search, fetch_url
   - Built-in: platform.core.search (optional — for index discovery)
6. Save and test

## Step 5: Verify End-to-End
Test these queries in the Agent Builder chat:
1. "What are my notes about the API refactoring?" → should return search results
2. "Read my daily note for today" → should return full note content
3. "Extract tasks from the API Refactoring note" → should list action items with Eisenhower classification
4. "Plan my day" → should propose 1-3-5 assignment
5. "How was my week?" → should return analytics narrative

## Troubleshooting
- MCP connection timeout: Check ngrok is running, server is healthy
- ES|QL query errors: Verify index exists and has data
- No search results: Re-run indexer to ensure notes are indexed
- Agent ignores tools: Check tool IDs match what's registered
```

**PATTERN**: Follow the placeholder comments already in setup-guide.md for the section structure.

**VALIDATE**: Read through and verify all API endpoints and UI paths are consistent with the research findings.

---

## TESTING STRATEGY

### Manual Validation (Primary — no automated tests for config files)

**System prompt review:**
1. Read through the entire prompt and check for internal consistency
2. Verify every tool mentioned exists in the MCP server or ES|QL definitions
3. Verify Eisenhower classification examples match sample vault content
4. Verify 1-3-5 rules match PRD Section 4
5. Verify human-in-the-loop rules cover all destructive/write operations
6. Check that tool selection guide correctly routes queries to the right tool

**ES|QL tool validation:**
1. Verify JSON syntax: `python -m json.tool < file.json`
2. Verify field names match `indexer/src/mappings.py`
3. Verify ES|QL pipeline order (FROM → WHERE → KEEP → SORT → LIMIT)
4. Verify parameter types are appropriate (string for text, integer for numbers, keyword for exact match)
5. Cross-reference tool descriptions with system prompt tool selection guide

### ES|QL Query Testing (in Kibana Dev Tools)

After setup, test each query manually by substituting parameters:

```
# search_notes
FROM athena-notes METADATA _score | WHERE MATCH(content_semantic, "API refactoring", {"boost": 0.7}) OR MATCH(content, "API refactoring", {"boost": 0.3}) | KEEP title, vault_relative_path, tags, note_type, word_count, updated_at, _score | SORT _score DESC | LIMIT 5

# get_recent_notes
FROM athena-notes | WHERE updated_at >= NOW() - TO_TIMEDURATION("168 hours") | KEEP title, vault_relative_path, tags, note_type, word_count, updated_at | SORT updated_at DESC | LIMIT 10

# get_notes_by_tag
FROM athena-notes | MV_EXPAND tags | WHERE tags == "api" | KEEP title, vault_relative_path, tags, note_type, word_count, updated_at | SORT updated_at DESC | LIMIT 20

# count_notes_by_tag
FROM athena-notes | MV_EXPAND tags | STATS note_count = COUNT(*) BY tags | SORT note_count DESC | LIMIT 30

# get_conversation_history (requires at least 1 saved conversation)
FROM athena-conversations METADATA _score | WHERE MATCH(summary_semantic, "daily planning") | KEEP summary, topics, extracted_tasks, task_ids_created, timestamp, _score | SORT _score DESC | LIMIT 5
```

### Integration Testing (in Agent Builder chat)

Test the 5 demo scenarios from PRD user stories:
1. US-1 (Knowledge Search): "What did I write about the API refactoring project?"
2. US-2 (Direct Note Reading): "Read my note on the authentication module"
3. US-3 (Task Extraction): "Extract tasks from my sprint review notes"
4. US-5 (Daily Planning): "Plan my day"
5. US-8 (Productivity Check-in): "How was my week?"

---

## VALIDATION COMMANDS

### Level 1: JSON Syntax

```bash
for f in /home/stardust/Athena/agent-config/tools/*.json; do python3 -m json.tool "$f" > /dev/null && echo "OK: $f" || echo "FAIL: $f"; done
```

### Level 2: Field Name Cross-Reference

```bash
# Verify all field names in ES|QL queries exist in the mappings
cd /home/stardust/Athena && python3 -c "
import json, re
from pathlib import Path

# Load mappings
mappings_file = Path('indexer/src/mappings.py').read_text()
# Extract field names from NOTES mapping
notes_fields = {'title', 'content', 'content_semantic', 'tags', 'note_type', 'path', 'vault_relative_path', 'word_count', 'created_at', 'updated_at', 'indexed_at', 'checksum'}
# ES metadata fields
meta_fields = {'_score', '_id', '_index'}
# Conversations fields
conv_fields = {'summary', 'summary_semantic', 'topics', 'extracted_tasks', 'task_ids_created', 'timestamp'}

all_valid = notes_fields | meta_fields | conv_fields | {'note_count'}  # note_count is computed

tools_dir = Path('agent-config/tools')
for f in tools_dir.glob('*.json'):
    tool = json.loads(f.read_text())
    if tool.get('type') != 'esql':
        continue
    query = tool['configuration']['query']
    # Extract field references (words after KEEP, SORT, WHERE, BY, MATCH()
    fields = set(re.findall(r'\b([a-z_]+)\b', query.lower()))
    # Filter to likely field names (ignore SQL keywords)
    keywords = {'from', 'where', 'keep', 'sort', 'limit', 'stats', 'by', 'or', 'and', 'desc', 'asc', 'metadata', 'match', 'mv_expand', 'count', 'now', 'to_timeduration'}
    field_candidates = fields - keywords
    # Check if all referenced fields exist
    for field in field_candidates:
        if field not in all_valid and not field.startswith('?') and field not in {'athena', 'notes', 'conversations', 'boost', 'esql'}:
            print(f'WARNING: {f.name} references unknown field: {field}')
print('Field cross-reference complete')
"
```

### Level 3: Tool-Prompt Consistency Check

```bash
# Verify system prompt references tools that exist
cd /home/stardust/Athena && python3 -c "
from pathlib import Path

prompt = Path('agent-config/system-prompt.md').read_text()

# Check ES|QL tool names are mentioned
esql_tools = ['search_notes', 'get_recent_notes', 'get_notes_by_tag', 'count_notes_by_tag', 'get_conversation_history']
for tool in esql_tools:
    if tool not in prompt:
        print(f'WARNING: ES|QL tool {tool} not mentioned in system prompt')
    else:
        print(f'OK: {tool} referenced in prompt')

# Check MCP tool names
mcp_tools = ['vault_query', 'vault_read', 'vault_manage', 'artemis_create_task', 'artemis_list_tasks', 'artemis_complete_task', 'artemis_get_daily_plan', 'artemis_assign_to_plan', 'artemis_get_analytics', 'artemis_start_pomodoro', 'save_conversation_summary', 'web_search', 'fetch_url']
for tool in mcp_tools:
    if tool not in prompt:
        print(f'WARNING: MCP tool {tool} not mentioned in system prompt')
    else:
        print(f'OK: {tool} referenced in prompt')

print('Tool-prompt consistency check complete')
"
```

### Level 4: Lint Markdown

```bash
# Check system prompt isn't excessively long (target: <400 lines)
wc -l /home/stardust/Athena/agent-config/system-prompt.md
```

---

## ACCEPTANCE CRITERIA

- [ ] `agent-config/system-prompt.md` contains a complete Athena persona with identity, goal, tool listing, selection guide, workflow patterns, Eisenhower classification, 1-3-5 planning, guardrails, and output formatting
- [ ] System prompt explicitly encodes human-in-the-loop rules for all write/create/delete operations
- [ ] System prompt includes Eisenhower classification rules with concrete examples from the sample vault
- [ ] System prompt includes 1-3-5 daily planning workflow with step-by-step process
- [ ] System prompt includes tool selection decision matrix that correctly routes queries
- [ ] System prompt includes error recovery guidance
- [ ] 5 ES|QL tool JSON files have valid JSON syntax
- [ ] ES|QL queries use correct field names from `indexer/src/mappings.py`
- [ ] ES|QL queries follow valid pipeline syntax (FROM → WHERE → KEEP → SORT → LIMIT)
- [ ] `search_notes` uses hybrid semantic + full-text scoring with ELSER
- [ ] `get_notes_by_tag` uses `MV_EXPAND tags` before filtering
- [ ] `count_notes_by_tag` uses `MV_EXPAND tags` before `STATS ... BY tags`
- [ ] `get_recent_notes` uses `TO_TIMEDURATION(?time_range)` for parameterized date ranges
- [ ] `get_conversation_history` queries `athena-conversations` index (not `athena-notes`)
- [ ] Index search tool is scoped to `athena-notes` with appropriate `custom_instructions`
- [ ] `setup-guide.md` has complete step-by-step instructions for Kibana configuration
- [ ] All tool descriptions are clear enough for an LLM to decide when to use each tool
- [ ] No secrets, credentials, or environment-specific values in any config file

---

## COMPLETION CHECKLIST

- [ ] Task 1 (system-prompt.md) completed — full prompt written
- [ ] Task 2-6 (ES|QL tools) completed — 5 JSON files created
- [ ] Task 7 (index search tool) completed — 1 JSON file created
- [ ] Task 8 (setup-guide.md) completed — instructions written
- [ ] Level 1 validation passed (JSON syntax)
- [ ] Level 2 validation passed (field name cross-reference)
- [ ] Level 3 validation passed (tool-prompt consistency)
- [ ] Level 4 validation passed (prompt length <400 lines)
- [ ] All acceptance criteria met

---

## NOTES

- **System prompt iteration**: The prompt will need tuning after testing in Agent Builder. The first version is a starting point — expect 2-3 iterations based on observed agent behavior (e.g., wrong tool selection, poor Eisenhower classification, not confirming before acting). Track prompt versions in git.

- **ES|QL MATCH on semantic_text**: The `MATCH(content_semantic, ?query)` pattern works because `semantic_text` fields support MATCH queries that trigger ELSER inference at query time. No client-side embedding needed.

- **MCP tool import in Agent Builder**: When registering MCP tools, Agent Builder auto-discovers tool names and descriptions from the MCP server's `listTools` response. The tool descriptions in `server.py` and `tools/*.py` docstrings become the tool descriptions in Agent Builder. The system prompt provides additional routing guidance on top of these built-in descriptions.

- **Index search vs ES|QL search**: The index search tool (`notes.semantic_search`) is a dynamic search that generates its own queries. ES|QL tools are predefined query templates with parameter substitution. Both are useful: ES|QL for predictable, well-defined queries; index search for complex/ad-hoc queries the predefined templates don't cover.

- **TO_TIMEDURATION gotcha**: The agent must pass time ranges as strings like `"168 hours"`, not `"7 days"`. The parameter description must make this format clear. If this proves error-prone, consider switching to a simpler `days` integer parameter and using `EVAL cutoff = NOW() - ?days * 86400000` instead (though this is less clean).

- **count_notes_by_tag has no parameters**: This is intentional. Some ES|QL tools are static queries that don't need runtime input. The Agent Builder docs confirm `params: {}` is valid.

- **Prompt caching**: Agent Builder benefits from static instruction blocks. Avoid inserting volatile data (timestamps, session IDs) into the system prompt. All dynamic data should come through tool results, not prompt injection.
