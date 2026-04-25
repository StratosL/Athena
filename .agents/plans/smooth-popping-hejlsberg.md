# Plan: Add Skills System to Athena

## Context

Athena currently has 19 tools across 4 groups, but no way for users to define reusable multi-step workflows. Repetitive sequences (morning check-in, meeting debrief, weekly review) require the user to manually guide the agent through the same steps each time.

Inspired by NanoClaw's skill system, we're adding two complementary layers:

### Layer 1: Vault Runtime Skills (Agent-Native — No Claude Code Required)
- Stored as markdown files in `Meta/Skills/` in the Obsidian vault
- The **Athena agent itself** creates, edits, loads, and executes skills via a new `skill_manager` MCP tool
- User says "save this as a skill" → agent drafts it → user approves → agent writes to vault
- User says "run my morning routine" → agent loads skill → follows steps using existing tools
- Fully autonomous: works through Agent Builder chat, voice client, or any interface
- Human-in-the-loop: agent always confirms before creating/modifying skills

### Layer 2: Claude Code Developer Skills
- Stored in `.claude/skills/` (standard Claude Code skill format)
- For developers extending Athena's codebase (adding new integrations, MCP tools, etc.)
- Invoked as `/customize` or `/add-integration` in Claude Code CLI

## Files to Create

| # | Path | Purpose |
|---|------|---------|
| 1 | `mcp-server/src/tools/skills.py` | New MCP tool: `skill_manager` (list, load, create, edit, delete) |
| 2 | `sample-vault/Meta/Skills/morning-routine.md` | Sample skill: morning briefing workflow |
| 3 | `sample-vault/Meta/Skills/meeting-debrief.md` | Sample skill: extract tasks from meeting notes |
| 4 | `sample-vault/Meta/Skills/weekly-review.md` | Sample skill: weekly productivity review |
| 5 | `.claude/skills/customize/SKILL.md` | Meta-skill: teaches Claude Code how to extend Athena |
| 6 | `.claude/skills/add-integration/SKILL.md` | Template skill: adding new service integrations |

## Files to Modify

| # | Path | Change |
|---|------|--------|
| 7 | `mcp-server/src/server.py` | Add `import src.tools.skills` (line 56) |
| 8 | `agent-config/system-prompt.md` | Add Skills tool docs, Pattern 8/9, tool selection row |
| 9 | `voice-client/serve.py` | Inject available skill names into `systemPromptAddition` |
| 10 | `voice-client/pyproject.toml` | Add `python-frontmatter` dependency (for skill name extraction) |

## Implementation Details

### 1. Vault Skill Markdown Format

Each skill is a `.md` file in `Meta/Skills/` with frontmatter and structured steps:

```markdown
---
title: "Morning Routine"
tags: [skill, productivity]
created: 2026-02-16
trigger_phrases:
  - "morning routine"
  - "start my day"
---

# Morning Routine

Brief description.

## Steps

1. **Check daily plan**
   - Tool: `artemis_get_daily_plan`

2. **Review urgent tasks**
   - Tool: `artemis_list_tasks` with status=pending

3. **Present briefing**
   - Summarize findings to user

## Expected Output

What the user should see when the skill completes.
```

### 2. MCP Tool: `skill_manager`

Single tool with operation-based dispatch, following `vault_query`/`vault_read`/`vault_manage` pattern.

**File:** `mcp-server/src/tools/skills.py`
**Imports from:** `src.server` (mcp, vault_manager) — same as `tools/vault.py`

| Operation | Parameters | What it does |
|-----------|-----------|--------------|
| `list_skills` | — | Scans `Meta/Skills/*.md`, returns name + title + trigger_phrases from frontmatter |
| `load_skill` | `name` | Reads full content of `Meta/Skills/{name}.md` via `vault_manager.read_note()` |
| `create_skill` | `name`, `content`, `trigger_phrases`, `description` | Creates `Meta/Skills/{name}.md` with frontmatter via `vault_manager.write_note()` |
| `edit_skill` | `name`, `content` | Reads existing frontmatter, deletes old file, creates new with updated content |
| `delete_skill` | `name`, `confirm_destructive` | Deletes via `vault_manager.delete_note()` |

Key: `list_skills` does its own frontmatter parsing (via `python-frontmatter`) to extract `trigger_phrases` — this is richer than what `vault_manager.list_notes()` returns.

### 3. System Prompt Additions

Add to `agent-config/system-prompt.md`:

**After the Research tools section (~line 76):**
```markdown
### MCP Tools — Skills (Runtime Workflows)

- **skill_manager** — Discover, load, and manage reusable multi-step workflows:
  - `list_skills` — List all available skills with names and trigger phrases
  - `load_skill` — Load a skill's full steps and instructions
  - `create_skill` — Create a new skill from conversation (requires confirmation)
  - `edit_skill` — Update an existing skill's content
  - `delete_skill` — Delete a skill (requires `confirm_destructive=true`)
```

**New row in Tool Selection Guide table:**
```
| Run a multi-step workflow | MCP `skill_manager` → `list_skills` then `load_skill` | Load steps, execute each using existing tools |
```

**New workflow patterns (after Pattern 7):**

**Pattern 8: Skill Execution**
1. If user's request matches a known workflow, check skills with `skill_manager` → `list_skills`
2. Load the matching skill with `skill_manager` → `load_skill`
3. Follow the skill's steps sequentially, using the tools specified in each step
4. Present results as described in the skill's Expected Output section

**Pattern 9: Skill Creation (Agent-Autonomous)**
1. When the user completes a multi-step workflow and says "save this as a skill" (or agent recognizes a repeatable pattern and suggests it)
2. Draft the skill markdown with: title, trigger phrases, steps referencing existing tools, expected output
3. Present the draft to the user for review — show the full content
4. On approval, call `skill_manager` → `create_skill` to save to the vault
5. Confirm creation and tell the user the trigger phrases they can use next time

**Addition to Memory & Context section:**
- Note that skill names and triggers are injected into context for fast matching
- Agent should proactively suggest creating a skill when it notices a user repeating a multi-step workflow

### 4. Voice Proxy Skill Injection

Extend `_read_memory_context()` in `serve.py` to scan `Meta/Skills/` and append a lightweight "Available Skills" section listing just names and trigger phrases. Add `python-frontmatter` to voice-client deps.

```python
# After existing memory loop, add:
skills_dir = vault / "Meta" / "Skills"
if skills_dir.is_dir():
    skill_lines = []
    for skill_file in sorted(skills_dir.glob("*.md")):
        post = frontmatter.loads(skill_file.read_text(encoding="utf-8"))
        title = post.metadata.get("title", skill_file.stem)
        triggers = post.metadata.get("trigger_phrases", [])
        skill_lines.append(f"- **{title}**: {', '.join(triggers[:3])}")
    if skill_lines:
        sections.append("## Available Skills\n\n" + "\n".join(skill_lines))
```

### 5. Claude Code Skills

**`.claude/skills/customize/SKILL.md`** — Documents:
- Two skill layers (Claude Code vs vault runtime)
- How to create each type
- How to add MCP tools (`mcp-server/src/tools/` → `server.py` import)
- How to add integrations (client adapter → tool module → config → registration)
- Key files table

**`.claude/skills/add-integration/SKILL.md`** — Step-by-step for adding a new service:
1. Create client adapter (`mcp-server/src/{service}_client.py`)
2. Create tool module (`mcp-server/src/tools/{service}.py`)
3. Update config (`mcp-server/src/config.py`)
4. Register in server (`mcp-server/src/server.py`)
5. Update system prompt
6. Sync to Agent Builder

## Implementation Order

1. **`mcp-server/src/tools/skills.py`** + server.py import (core tool)
2. **3 sample skills** in `sample-vault/Meta/Skills/`
3. **System prompt update** (agent awareness)
4. **Voice proxy update** (skill name injection)
5. **Claude Code skills** (customize + add-integration)
6. **Verify** — lint, MCP tool list, manual test

## Verification

1. `ruff check mcp-server/src/tools/skills.py` — no lint errors
2. Start MCP server → verify 14 tools in tools/list (was 13)
3. Call `skill_manager` `list_skills` → 3 skills returned
4. Call `skill_manager` `load_skill` name=morning-routine → full content
5. Call `skill_manager` `create_skill` → new file in Meta/Skills/
6. Call `skill_manager` `delete_skill` confirm_destructive=true → file removed
7. Voice proxy starts, `systemPromptAddition` includes "Available Skills" section
8. `/customize` and `/add-integration` recognized by Claude Code
