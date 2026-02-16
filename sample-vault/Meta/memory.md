---
title: "Agent Memory"
tags:
  - meta
  - memory
created: 2026-02-01
updated: 2026-02-16
---

# Agent Memory

Long-term facts and decisions learned across conversations. Athena appends here when discovering durable information.

## Key Decisions
- **Cursor pagination** chosen over offset pagination for all new API endpoints (decided 2026-02-03)
- **JWT auth** with refresh tokens — Elena's RBAC middleware handles role checks
- **Database migration order:** Schema changes first, then backfill, then index creation (learned from Phase 1 incident)
- **Elasticsearch ELSER** for semantic search — no custom embeddings needed

## Project Relationships
- [[API Refactoring]] depends on [[Database Migration Plan]] (schema) + [[Authentication Module]] (JWT middleware)
- [[AI-Powered Task Prioritization]] depends on [[API Refactoring]] (needs new task endpoints)
- [[Progressive Disclosure Onboarding]] is independent — Mara can ship anytime

## Preferences Discovered
- Stratos prefers afternoon PR reviews — don't suggest morning review blocks
- When task deadlines are ambiguous, default to Q2 (current quarter) unless context says otherwise
- Sprint demos happen Fridays — anything tagged "demo-ready" is implicitly due Thursday EOD
- Prefers `uv` over `pip` for all Python projects
