# ADR-011: Vault-Based Runtime Skills Over Hardcoded Workflows

**Date:** 2026-02-16
**Status:** Accepted
**Context:** Athena needs reusable multi-step workflows (morning routine, meeting debrief, weekly review)

---

## Problem

Users repeat certain multi-step workflows regularly:
- "Run my morning routine" → check daily plan, review pending tasks, read recent changes, update daily note
- "Debrief this meeting" → read meeting note, extract action items, classify by quadrant, create tasks
- "Weekly review" → pull analytics, review completed tasks, check overdue items, write narrative

Hardcoding these as MCP tools means every new workflow requires a code change, Docker rebuild, and redeployment. The user can't create or modify workflows themselves.

## Options

### Option A: Hardcoded MCP Tools — Rejected

Each workflow as a separate MCP tool with fixed logic.

- **Pro:** Fast execution, no LLM interpretation needed
- **Con:** Rigid. Adding a workflow requires Python code + rebuild. User can't customize. Doesn't scale.

### Option B: Agent Builder Workflows — Rejected

Use Elastic's planned Workflow feature for multi-step automation.

- **Pro:** Platform-native
- **Con:** Not yet GA. Can't depend on it.

### Option C: Vault-Based Markdown Skills (Selected)

Skills are Markdown files in `Meta/Skills/` with YAML frontmatter (name, trigger phrases) and step-by-step instructions. The agent loads and follows them at runtime.

## Decision

Skills stored as vault notes with this structure:

```markdown
---
name: Morning Routine
triggers: ["morning routine", "start my day", "good morning"]
---

## Steps
1. Check today's daily plan using `artemis_get_daily_plan`
2. List pending tasks using `artemis_list_tasks`
...

## Expected Output
A morning briefing summary...
```

Single MCP tool (`skill_manager`) with 5 operations: `list_skills`, `load_skill`, `create_skill`, `edit_skill`, `delete_skill`.

The agent executes skills by loading the Markdown, interpreting the steps, and calling existing tools. No new execution engine — the LLM IS the execution engine.

## Consequences

- Users create/edit skills in Obsidian — no code changes, no rebuilds
- Agent can suggest and create skills from conversation ("save this as a skill")
- Skills compose existing tools — no new capabilities needed, just orchestration
- Skill names and triggers injected into system prompt via voice proxy for discoverability
- Execution depends on LLM interpretation — less deterministic than hardcoded tools
- Skills are part of the vault knowledge graph — searchable, taggable, linkable
- Shipped with 3 sample skills: morning routine, meeting debrief, weekly review
