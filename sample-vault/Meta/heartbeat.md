---
title: "Heartbeat Checklist"
tags:
  - meta
  - heartbeat
created: 2026-02-16
updated: 2026-02-16
---

# Heartbeat Checklist

Instructions for proactive checks. Evaluate each section based on the current time, then respond with exactly `HEARTBEAT_OK` if nothing needs the user's attention. If something does need attention, describe it clearly and suggest an action.

## Morning (before 10:00)

- Check if today's daily plan exists using `artemis_get_daily_plan`. If the plan has no tasks assigned, remind Stratos to plan his day.
- Look for any Q1 (urgent + important) tasks with deadlines today or tomorrow. Alert if found.

## Throughout Day

- Check for Q1 tasks that are still pending. If any have been pending for more than 3 days, alert with a nudge to address or reclassify them.
- Review today's daily plan — if any assigned tasks are still pending and it's after 16:00, suggest wrapping them up or carrying them to tomorrow.

## Evening (after 18:00)

- Summarize today's completed tasks (use `artemis_get_analytics` with period=day).
- If the daily plan has incomplete tasks, suggest carrying them to tomorrow.
- If no conversation summary has been saved today, offer to summarize the day.
