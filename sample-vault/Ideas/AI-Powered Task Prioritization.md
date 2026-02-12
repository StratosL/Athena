---
title: AI-Powered Task Prioritization
tags:
  - idea
  - ai
  - productivity
  - helios
created: 2026-02-08
updated: 2026-02-08
---

# AI-Powered Task Prioritization

## Concept

Use machine learning to automatically suggest task priorities in [[Helios v2 Roadmap]] based on:

- Due date proximity
- Task dependencies and blocking relationships
- Historical completion patterns (user tends to do quick tasks in morning)
- Context from [[Elasticsearch Semantic Search]] on related notes and meetings

## Proposed UX

A "Smart Priority" toggle in the task list view. When enabled, tasks reorder based on AI scoring. Users can override any suggestion, and overrides feed back into the model.

## Technical Approach

Lightweight scoring function, not a full ML model initially. Weighted combination of urgency, importance, and user behavior signals. Can evolve into a trained model later with enough data.

## Related

- [[Progressive Disclosure Onboarding]] — only show this to advanced users
- [[Voice Commands for Task Management]] — "What should I work on next?"
- [[Sprint Review 2026-02-07]] — team discussed AI features
