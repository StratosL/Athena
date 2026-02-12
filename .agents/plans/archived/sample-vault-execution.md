# Execute: Sample Vault + Indexer Pipeline Validation

## Context

The indexer pipeline (parser, bulk indexer, CLI, watcher) is built but unvalidated — the sample vault has only empty folders with `.gitkeep` files. We need 17 realistic demo notes to validate end-to-end indexing and prepare demo content for all PRD user stories. Source plan: `.agents/plans/sample-vault-and-indexer-validation.md`.

## Implementation Steps

### Phase 1: Create 17 Sample Notes (Tasks 1-17)

Create markdown files with valid YAML frontmatter across 5 folders. All notes use the "Stratos/Helios" narrative. Key constraints from parser.py:
- Frontmatter fields: `title`, `tags` (list), `created`, `updated`, optional `type`
- Titles with colons must be YAML-quoted
- Tags can be list or string (parser handles both)
- Dates: ISO format (YYYY-MM-DD), parsed as midnight UTC

**Files to create:**

| # | Path | Words | Tags | Created |
|---|------|-------|------|---------|
| 1 | `Research/Elasticsearch Semantic Search.md` | ~250 | research, elasticsearch, semantic-search, elser, ai | 2026-02-04 |
| 2 | `Research/API Versioning Best Practices.md` | ~400 | research, api, versioning, best-practices | 2026-02-05 |
| 3 | `Research/JWT Authentication Patterns.md` | ~300 | research, jwt, auth, security | 2026-02-06 |
| 4 | `Ideas/Progressive Disclosure Onboarding.md` | ~150 | idea, onboarding, ux, helios | 2026-02-10 |
| 5 | `Ideas/AI-Powered Task Prioritization.md` | ~120 | idea, ai, productivity, helios | 2026-02-08 |
| 6 | `Ideas/Voice Commands for Task Management.md` | ~100 | idea, voice, ux, helios | 2026-02-11 |
| 7 | `Projects/Database Migration Plan.md` | ~200 | database, postgresql, migration, helios | 2026-01-28 |
| 8 | `Projects/Authentication Module.md` | ~250 | auth, security, backend, helios | 2026-02-01 |
| 9 | `Projects/Helios v2 Roadmap.md` | ~300 | roadmap, helios, planning, q1-2026 | 2026-01-15 |
| 10 | `Projects/API Refactoring.md` | ~350 | api, refactoring, backend, helios | 2026-02-03 |
| 11 | `Meeting Notes/Planning Session 2026-02-03.md` | ~200 | planning, helios, roadmap | 2026-02-03 |
| 12 | `Meeting Notes/Sprint Review 2026-02-07.md` | ~400 | sprint-review, helios, planning | 2026-02-07 |
| 13 | `Meeting Notes/Standup 2026-02-10.md` | ~120 | standup, helios, daily | 2026-02-10 |
| 14 | `Daily Notes/2026-02-07.md` | ~150 | daily, journal | 2026-02-07 |
| 15 | `Daily Notes/2026-02-09.md` | ~180 | daily, journal | 2026-02-09 |
| 16 | `Daily Notes/2026-02-11.md` | ~250 | daily, journal | 2026-02-11 |
| 17 | `Daily Notes/2026-02-12.md` | ~200 | daily, journal | 2026-02-12 |

**Critical content requirements:**
- API Refactoring note: exactly 7 extractable tasks (5 `- [ ]`, 1 `TODO:`, 1 `Action item:`)
- Sprint Review note: 5 numbered action items
- 14+ notes contain `[[wikilinks]]` for cross-referencing
- Daily 2026-02-11: 5 pomodoro entries with times (for US-8 productivity)
- Daily 2026-02-12: Today's note with priorities (for US-5 daily planning)

### Phase 2: Update Configuration (Task 18)

**File:** `/home/stardust/Athena/.env`
**Change:** `VAULT_PATH=/path/to/your/obsidian/vault` → `VAULT_PATH=/home/stardust/Athena/sample-vault`

### Phase 3: Validate (Tasks 19-23)

1. **Parser dry-run** — Parse vault, expect 17 notes / 0 errors, correct type distribution
2. **Index setup** — `athena-index setup-indices` (indices should already exist)
3. **Bulk index** — `athena-index index` → 17 indexed, 0 skipped, 0 errors
4. **Checksum dedup** — Re-run `athena-index index` → 0 indexed, 17 skipped
5. **ES aggregation** — Query document count (17) and type distribution (4/3/3/4/3)
6. **Semantic search** — 3 test queries, verify top results match expected notes

## Verification

- Parser: 17 parsed, 0 errors
- Index: 17 indexed first run, 17 skipped second run
- ES count: 17 documents
- ES types: project=4, idea=3, meeting=3, daily=4, research=3
- Semantic: "API refactoring plan" → API Refactoring at top
