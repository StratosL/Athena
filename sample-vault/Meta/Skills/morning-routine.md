---
title: "Morning Routine"
tags: [skill, productivity]
created: 2026-02-16
trigger_phrases:
  - "morning routine"
  - "start my day"
  - "morning briefing"
---

# Morning Routine

Start the day with a structured briefing: check today's plan, review urgent tasks, scan recent vault activity, and present a concise summary.

## Steps

1. **Get today's daily plan**
   - Tool: `artemis_get_daily_plan`
   - If no plan exists yet, note that planning is needed

2. **List pending tasks**
   - Tool: `artemis_list_tasks` with status=pending
   - Highlight any Q1 (urgent+important) items

3. **Check recent vault changes**
   - Tool: `vault_query` with operation=recent_changes, limit=5
   - Mention any notes modified since yesterday

4. **Read today's daily note** (if it exists)
   - Tool: `vault_read` with operation=daily_note
   - Pull any carry-over items or reminders

5. **Present morning briefing**
   - Summarize: plan status, urgent tasks, recent activity
   - If daily plan is empty, offer to run the daily planning workflow

## Expected Output

A concise briefing with:
- Today's plan overview (or prompt to create one)
- Urgent/overdue tasks requiring attention
- Recent vault activity highlights
- Suggested first action for the day
