# ADR-010: Proactive Heartbeat with APScheduler and HEARTBEAT_OK Suppression

**Date:** 2026-02-16
**Status:** Accepted
**Context:** Athena should proactively check on the user's tasks and deadlines, not just respond reactively

---

## Problem

A purely reactive agent waits for the user to ask questions. But overdue tasks, missed daily plans, and approaching deadlines should trigger nudges. The agent needs a way to "wake up" periodically and evaluate whether the user needs attention.

Inspired by OpenClaw's heartbeat pattern (ADR-003): a cron job that calls the agent with a system prompt asking it to evaluate a checklist.

## Options

### Option A: Elastic Workflows — Rejected

Use Elastic's built-in workflow automation to trigger agent evaluations.

- **Pro:** Native platform feature, no custom service
- **Con:** Elastic Workflows don't exist yet as a GA feature. Can't rely on unreleased functionality for a hackathon.

### Option B: Simple Cron Script — Rejected

A bash script on cron that calls the converse API.

- **Pro:** Minimal code
- **Con:** No state management (conversation ID persistence), no graceful shutdown, no active-hours logic, harder to Dockerize.

### Option C: APScheduler Service (Selected)

A dedicated Python service using APScheduler 3.x with `CronTrigger` for periodic check-ins.

## Decision

Heartbeat service (`heartbeat/`) runs as an opt-in Docker Compose service:

1. **Scheduler:** `CronTrigger(minute="*/30", hour="8-21")` — every 30 min during active hours only
2. **Tick:** Reads `Meta/heartbeat.md` from the vault (user-editable checklist), injects user profile + agent memory, calls Kibana converse API
3. **Suppression:** If the agent finds nothing to report, it returns `HEARTBEAT_OK` — silently discarded (debug log only, no user notification)
4. **Alert delivery:** Real alerts appended as `## Heartbeat Alert (HH:MM UTC)` blocks to the daily note in the vault
5. **Conversation continuity:** Conversation ID persisted to file, reused across ticks

### HEARTBEAT_OK Pattern

The key insight is that most heartbeat ticks will find nothing actionable. Without suppression, the user would get 20+ "everything is fine" notifications per day. The agent is instructed (via the heartbeat prompt) to respond with exactly `HEARTBEAT_OK` when there's nothing to report. The service checks for this string and discards the response.

## Consequences

- Agent becomes proactive — nudges about overdue Q1 tasks, missing daily plans, approaching deadlines
- Opt-in via Docker Compose profile (`--profile heartbeat`) — avoids accidental LLM costs (~$0.50-2/day)
- APScheduler v3 (stable) chosen over v4 (alpha) for hackathon reliability
- Active hours prevent 3 AM notifications
- Alerts land in the daily note — visible in Obsidian, part of the vault record
- `HEARTBEAT_OK` suppression keeps noise near zero
- Each tick costs one LLM inference call — cost scales with interval frequency
- Heartbeat checklist is user-editable (`Meta/heartbeat.md`) — user controls what gets checked
