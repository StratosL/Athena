# Feature: Sample Vault + Indexer Pipeline Validation

## Context

The indexer pipeline is complete (parser, bulk indexer, CLI, watcher) but the sample vault is empty — just 5 folders with `.gitkeep` files. We need 15-20 realistic demo notes to validate the indexer end-to-end and prepare for all 10 PRD user stories. The `.env` also has a placeholder `VAULT_PATH` that needs updating.

## User Story

As a developer building the Athena demo,
I want a realistic sample vault indexed into Elasticsearch,
So that I can validate the indexer pipeline and have demo-ready content for all user stories.

## Solution

Create 17 markdown notes across the 5 vault folders, written from the perspective of "Stratos" — a solo developer building a SaaS product called "Helios." Update `.env`, run the indexer, and validate with parser dry-run, ES queries, and semantic search tests.

**Feature Type**: New Capability
**Estimated Complexity**: Medium
**Primary Systems Affected**: `sample-vault/`, `.env`, indexer (read-only validation)

---

## CONTEXT REFERENCES

### Critical Files to Read Before Implementing

- `indexer/src/parser.py` (lines 14-20) — `NOTE_TYPE_FOLDER_MAP` defines folder→type mapping
- `indexer/src/parser.py` (lines 91-155) — `parse_note()` shows exact frontmatter fields extracted: `title`, `tags`, `created`, `updated`/`modified`, `type`
- `indexer/src/mappings.py` — ES index schema (semantic_text, keyword fields, dates)
- `PRD.md` (Section 5, lines 112-164) — 10 user stories the notes must support

### Frontmatter Schema (from parser.py)

```yaml
---
title: string              # Falls back to filename stem
tags: [list, of, strings]  # Also accepts single string
created: 2026-02-12        # ISO date or datetime, falls back to filesystem ctime
updated: 2026-02-12        # Also accepts "modified" key, falls back to mtime
type: string               # Optional — inferred from folder if absent
---
```

### Folder → note_type Mapping

| Folder | Inferred `note_type` |
|--------|---------------------|
| `Projects/` | `project` |
| `Ideas/` | `idea` |
| `Meeting Notes/` | `meeting` |
| `Daily Notes/` | `daily` |
| `Research/` | `research` |

---

## IMPLEMENTATION PLAN

### Phase 1: Create 17 Sample Notes

Write all notes with valid YAML frontmatter, realistic content, embedded tasks for extraction demos, and `[[wikilinks]]` for cross-referencing. Content is anchored around Feb 2026 with a "Helios" SaaS product narrative.

### Phase 2: Update Configuration

Update `.env` VAULT_PATH to point to the sample vault.

### Phase 3: Run Indexer + Validate

Run the indexer CLI, verify all 17 notes index successfully, test checksum dedup, query ES for document counts, tag distributions, and semantic search relevance.

---

## STEP-BY-STEP TASKS

### Task 1: CREATE `Research/Elasticsearch Semantic Search.md`

~250 words. Tags: `research`, `elasticsearch`, `semantic-search`, `elser`, `ai`. Created: 2026-02-04.
Content: ELSER overview, sparse vs dense embeddings comparison, why ELSER for Athena, `semantic_text` field benefits. Wikilink to `[[Helios v2 Roadmap]]`.

### Task 2: CREATE `Research/API Versioning Best Practices.md`

**Demo-critical for US-7 (research partner).** ~400 words. Tags: `research`, `api`, `versioning`, `best-practices`. Created: 2026-02-05.
Content: URL-based vs header-based vs query param versioning. Decision: URL-based. Migration strategy (v1+v2 simultaneous, 3-month sunset). Key sources: Stripe, Microsoft, Zalando guidelines. Wikilinks to `[[API Refactoring]]`, `[[Sprint Review 2026-02-07]]`.

### Task 3: CREATE `Research/JWT Authentication Patterns.md`

~300 words. Tags: `research`, `jwt`, `auth`, `security`. Created: 2026-02-06.
Content: Access token (15min, RS256) + refresh token (7 days, httpOnly cookie) architecture. Token family rotation for theft detection. Security: no localStorage, Redis blacklist. Libraries: PyJWT chosen over python-jose and authlib. Wikilinks to `[[Authentication Module]]`, `[[Sprint Review 2026-02-07]]`.

### Task 4: CREATE `Ideas/Progressive Disclosure Onboarding.md`

**Supports US-6 (idea capture).** ~150 words. Tags: `idea`, `onboarding`, `ux`, `helios`. Created: 2026-02-10.
Content: Conversational tone ("Just thought of a way to improve..."). Current wizard has 40% drop-off at step 3. Progressive disclosure: simplest view first, actions unlock features. References Notion/Linear. Wikilink to `[[Helios v2 Roadmap]]`.

### Task 5: CREATE `Ideas/AI-Powered Task Prioritization.md`

~120 words. Tags: `idea`, `ai`, `productivity`, `helios`. Created: 2026-02-08.
Content: Scoring model for task priority (urgency, importance, effort, history). Start rule-based, upgrade to ML. Post-v2 feature. Differentiator from Todoist/TickTick.

### Task 6: CREATE `Ideas/Voice Commands for Task Management.md`

~100 words. Tags: `idea`, `voice`, `ux`, `helios`. Created: 2026-02-11.
Content: Voice assistant for Helios — create tasks, check plan, start pomodoros hands-free. Whisper STT + conversational agent. "This is basically what I'm building with Athena." Wikilink to `[[AI-Powered Task Prioritization]]`.

### Task 7: CREATE `Projects/Database Migration Plan.md`

~200 words. Tags: `database`, `postgresql`, `migration`, `helios`. Created: 2026-01-28.
Content: SQLite → PostgreSQL before v2. Migration steps: Railway setup, Alembic scripts, data transfer, connection pooling. Two tasks: `- [ ] Write Alembic migration scripts for all 12 tables`, `- [ ] Test data integrity after migration with checksums`. Wikilink to `[[Helios v2 Roadmap]]`.

### Task 8: CREATE `Projects/Authentication Module.md`

~250 words. Tags: `auth`, `security`, `backend`, `helios`. Created: 2026-02-01.
Content: Session cookies → JWT migration for mobile app + API. Current issues (sessions don't scale, no revocation, fragile password reset). Planned: JWT access/refresh, Redis blacklist, OAuth2 Google/GitHub. Three tasks: `- [ ] Implement JWT token generation and validation middleware`, `- [ ] Build refresh token rotation logic`, `- [ ] Add rate limiting to login endpoint`. Wikilinks to `[[API Refactoring]]`, `[[Sprint Review 2026-02-07]]`.

### Task 9: CREATE `Projects/Helios v2 Roadmap.md`

**Supports US-2 (direct reading: "read my note on the roadmap").** ~300 words. Tags: `roadmap`, `helios`, `planning`, `q1-2026`. Created: 2026-01-15.
Content: Launch target March 15, 2026. Q1 milestones: API refactoring (Feb), onboarding (Feb-Mar), billing Stripe (Mar), load testing + launch (Mar 15). Risks: API migration breaking clients, solo dev bottleneck, Stripe complexity. Success metrics: 50 paying customers, <200ms p95, zero critical bugs. Two tasks: `- [ ] Finalize v2 feature freeze list by Feb 20`, `- [ ] Schedule load testing window for March 5-10`. Wikilinks to `[[API Refactoring]]`, `[[Progressive Disclosure Onboarding]]`.

### Task 10: CREATE `Projects/API Refactoring.md`

**Demo-critical for US-1 (semantic search) and US-3/US-4 (task extraction).** ~350 words. Tags: `api`, `refactoring`, `backend`, `helios`. Created: 2026-02-03.
Content: Helios REST API grown organically — inconsistent naming, varied error responses. Goals: consistent naming, unified error format, OpenAPI generation. **Must contain 7 extractable tasks:**
1. `- [ ] Audit all 47 endpoints and document current inconsistencies`
2. `- [ ] Design unified error response schema with error codes`
3. `- [ ] Migrate authentication endpoints to new naming convention`
4. `- [ ] Write integration tests for the 12 most-used endpoints`
5. `- [ ] Set up automated OpenAPI spec generation in CI pipeline`
6. `TODO: Update the SDK generator config once naming is finalized`
7. `Action item: Notify beta users about breaking changes at least 2 weeks before v2`

Target completion Feb 28. Wikilinks to `[[API Versioning Best Practices]]`, `[[Sprint Review 2026-02-07]]`.

### Task 11: CREATE `Meeting Notes/Planning Session 2026-02-03.md`

~200 words. Tags: `planning`, `helios`, `roadmap`. Created: 2026-02-03.
Content: Q1 planning. Key dates: feature freeze Feb 20, beta Feb 20-Mar 5, load test Mar 5-10, launch Mar 15. Priority stack: 1) API refactoring, 2) Auth, 3) Database, 4) Onboarding, 5) Billing. Risk: solo dev bottleneck. Decision: use Eisenhower Matrix in Artemis. Wikilinks to `[[Helios v2 Roadmap]]`, `[[API Refactoring]]`.

### Task 12: CREATE `Meeting Notes/Sprint Review 2026-02-07.md`

**Demo-critical for US-3/US-4 (task extraction from meeting).** ~400 words. Tags: `sprint-review`, `helios`, `planning`. Created: 2026-02-07.
Content: Attendees: Stratos + Nikos (designer, advisory). Completed: endpoint audit, error schema draft, PostgreSQL Railway setup, 3 bug fixes. Decisions: JWT over sessions, semantic versioning, delay billing 1 week. **5 numbered action items:**
1. Finalize error schema and share with beta testers by Feb 12
2. Start JWT implementation — target completion Feb 14
3. Write migration scripts for the 5 most critical tables first
4. Update project README with new API conventions
5. Schedule call with Nikos to review onboarding wireframes

Next sprint: Auth module + first 5 Alembic migrations. Wikilinks to `[[API Refactoring]]`, `[[Authentication Module]]`, `[[Database Migration Plan]]`, `[[API Versioning Best Practices]]`.

### Task 13: CREATE `Meeting Notes/Standup 2026-02-10.md`

~120 words. Tags: `standup`, `helios`, `daily`. Created: 2026-02-10.
Content: Yesterday/Today/Blockers format. Finished error schema v1, sent to 3 beta testers. Today: JWT middleware + Redis setup. Blocker: waiting on beta feedback. Wikilink to `[[API Versioning Best Practices]]`.

### Task 14: CREATE `Daily Notes/2026-02-07.md`

~150 words. Tags: `daily`, `journal`. Created: 2026-02-07.
Content: Sprint review day. Priorities: prep summary, call with Nikos, fix task completion bug. 3 pomodoros (75 min). Bug: task completion returned 500 when task had no pomodoros. Wikilink to `[[Sprint Review 2026-02-07]]`.

### Task 15: CREATE `Daily Notes/2026-02-09.md`

~180 words. Tags: `daily`, `journal`. Created: 2026-02-09.
Content: Sunday half-day. Designed unified error response schema. Researched RFC 7807. Drafted JSON structure with `code`, `message`, `details`, `trace_id`. Created error code taxonomy. 3 pomodoros (75 min).

### Task 16: CREATE `Daily Notes/2026-02-11.md`

**Supports US-8 (productivity check-in with pomodoro data).** ~250 words. Tags: `daily`, `journal`. Created: 2026-02-11.
Content: 5 pomodoros logged with times and descriptions (JWT middleware, Redis setup, onboarding wireframes). Total: 125 min. 3/3 priorities done + bonus wireframes. Reflection: JWT 80% done, refresh token rotation tomorrow. Wikilinks to `[[Progressive Disclosure Onboarding]]`.

### Task 17: CREATE `Daily Notes/2026-02-12.md`

**Demo-critical for US-5 (daily planning).** ~200 words. Tags: `daily`, `journal`. Created: 2026-02-12.
Content: Today's note. Energy 8/10. Priorities: finish JWT validation middleware, write auth integration tests, review beta tester feedback on error schema. Deadline: error schema feedback due today. Reference to `[[Sprint Review 2026-02-07]]` action items due this week. Pomodoro target: 4. End-of-day section left as placeholder.

### Task 18: UPDATE `.env` — set VAULT_PATH

**File:** `/home/stardust/Athena/.env`
**Change:** Replace `VAULT_PATH=/path/to/your/obsidian/vault` with `VAULT_PATH=/home/stardust/Athena/sample-vault`

### Task 19: VALIDATE — Parser dry run

```bash
cd /home/stardust/Athena/indexer && uv run python -c "
from pathlib import Path
from src.parser import parse_vault
results = parse_vault(Path('/home/stardust/Athena/sample-vault'))
notes = [n for n, e in results if n]
errors = [e for n, e in results if e]
print(f'Parsed: {len(notes)} notes, Errors: {len(errors)}')
for n in notes:
    print(f'  {n.note_type:10s} | {n.word_count:4d} words | {len(n.tags):2d} tags | {n.vault_relative_path}')
if errors:
    for e in errors: print(f'  ERROR: {e}')
"
```
**Expected:** 17 notes, 0 errors. Types: 4 project, 3 idea, 3 meeting, 4 daily, 3 research.

### Task 20: VALIDATE — Index into Elasticsearch

```bash
cd /home/stardust/Athena/indexer && uv run athena-index setup-indices
```
**Expected:** Both indices "Already exists."

```bash
cd /home/stardust/Athena/indexer && uv run athena-index index
```
**Expected:** Total files: 17, Indexed: 17, Skipped: 0, Errors: 0.

### Task 21: VALIDATE — Checksum dedup

```bash
cd /home/stardust/Athena/indexer && uv run athena-index index
```
**Expected:** Total files: 17, Indexed: 0, Skipped: 17, Errors: 0.

### Task 22: VALIDATE — ES document count + aggregations

```bash
cd /home/stardust/Athena/indexer && uv run python -c "
import asyncio
from src.config import get_settings
from elasticsearch import AsyncElasticsearch

async def check():
    s = get_settings()
    es = AsyncElasticsearch(hosts=[s.elastic_url], api_key=s.elastic_api_key)
    count = await es.count(index=s.notes_index)
    print(f'Documents: {count[\"count\"]}')
    agg = await es.search(index=s.notes_index, body={
        'size': 0,
        'aggs': {'types': {'terms': {'field': 'note_type'}}}
    })
    print('Types:', {b['key']: b['doc_count'] for b in agg['aggregations']['types']['buckets']})
    await es.close()

asyncio.run(check())
"
```
**Expected:** 17 documents. Types: project=4, idea=3, meeting=3, daily=4, research=3.

### Task 23: VALIDATE — Semantic search relevance

```bash
cd /home/stardust/Athena/indexer && uv run python -c "
import asyncio
from src.config import get_settings
from elasticsearch import AsyncElasticsearch

async def search(es, query):
    r = await es.search(index=get_settings().notes_index, body={
        'size': 3, 'query': {'semantic': {'field': 'content_semantic', 'query': query}},
        '_source': ['title', 'note_type']
    })
    hits = [(h['_source']['title'], h['_score']) for h in r['hits']['hits']]
    print(f'  \"{query}\" -> {hits}')

async def main():
    s = get_settings()
    es = AsyncElasticsearch(hosts=[s.elastic_url], api_key=s.elastic_api_key)
    await search(es, 'API refactoring plan')
    await search(es, 'JWT token security')
    await search(es, 'improving user onboarding')
    await es.close()

asyncio.run(main())
"
```
**Expected:** "API refactoring" → API Refactoring Plan at top. "JWT token security" → JWT Authentication Patterns. "onboarding" → Progressive Disclosure Onboarding.

---

## USER STORY COVERAGE MATRIX

| User Story | Primary Notes | Demo Query |
|---|---|---|
| US-1 Semantic Search | API Refactoring, API Versioning Best Practices | "What did I write about API refactoring?" |
| US-2 Direct Reading | Helios v2 Roadmap | "Read my note on the roadmap" |
| US-3 Task Extraction | API Refactoring (7 tasks), Sprint Review (5 items) | "Extract tasks from my API refactoring notes" |
| US-5 Daily Planning | 2026-02-12 (today's daily note) | "Plan my day" |
| US-6 Idea Capture | Progressive Disclosure Onboarding | Shows what voice-captured idea looks like |
| US-7 Research Partner | API Versioning Best Practices | "What did I research about API versioning?" |
| US-8 Productivity | 2026-02-11 (5 pom), 2026-02-09 (3), 2026-02-07 (3) | "How was my week?" |

---

## ACCEPTANCE CRITERIA

- [ ] 17 markdown files created across 5 folders
- [ ] All notes have valid YAML frontmatter (title, tags, created, updated)
- [ ] Parser dry-run: 17 notes, 0 errors, correct note_type per folder
- [ ] `athena-index index`: 17 indexed, 0 errors
- [ ] Re-run index: 17 skipped (checksum dedup works)
- [ ] ES aggregation: correct type distribution (4/3/3/4/3)
- [ ] Semantic search: top results match expected notes for 3 test queries
- [ ] API Refactoring note has 7 extractable task items
- [ ] Sprint Review note has 5 numbered action items
- [ ] 14+ notes contain `[[wikilinks]]` for cross-referencing
- [ ] Word counts vary from ~100 to ~400

---

## NOTES

- YAML titles with colons must be quoted: `title: "Daily Note: February 12, 2026"`
- `.gitkeep` files can stay — parser only processes `.md` files
- ELSER inference runs at index time; first index of 17 docs may take 30-60s on Serverless
- If ELSER endpoint isn't ready, indexing will fail — check Kibana ML > Trained Models
- Dates without times are parsed as midnight UTC by `_parse_datetime()`
