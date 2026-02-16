---
title: "Weekly Review"
tags: [skill, productivity, review]
created: 2026-02-16
trigger_phrases:
  - "weekly review"
  - "review my week"
  - "week in review"
---

# Weekly Review

Comprehensive end-of-week review: analyze task completion, vault activity, and productivity trends to plan the next week.

## Steps

1. **Pull weekly analytics**
   - Tool: `artemis_get_analytics` with period=week
   - Note completion rate, focus time, quadrant distribution

2. **Review completed tasks**
   - Tool: `artemis_list_tasks` with status=completed
   - Identify wins and significant completions

3. **Check pending/overdue tasks**
   - Tool: `artemis_list_tasks` with status=pending
   - Flag tasks that have been pending too long or are overdue

4. **Scan vault activity**
   - Tool: `vault_query` with operation=recent_changes, date_range_days=7
   - Summarize which areas of the vault saw the most activity

5. **Present weekly narrative**
   - Summarize wins, completion rate, and productivity trends
   - Highlight any stalled tasks or areas needing attention
   - Suggest priorities for next week based on pending Q1/Q2 items

6. **Offer to save review note**
   - Propose creating a vault note with the review summary
   - Tool: `vault_manage` with operation=create_note if approved

## Expected Output

A narrative weekly review covering:
- Tasks completed vs planned (completion rate)
- Key wins and accomplishments
- Stalled or overdue items needing attention
- Vault activity summary
- Suggested focus areas for next week
