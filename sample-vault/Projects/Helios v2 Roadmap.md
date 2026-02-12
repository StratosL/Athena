---
title: "Helios v2 Roadmap"
tags:
  - roadmap
  - helios
  - planning
  - q1-2026
created: 2026-01-15
updated: 2026-02-10
---

# Helios v2 Roadmap

## Vision

Helios v2 transforms the productivity app from a simple task manager into an intelligent work orchestrator. The core theme is **"less managing, more doing"** — using AI and automation to reduce the overhead of organizing work.

## Q1 2026 Milestones

### M1: Foundation (January)
- [x] [[Database Migration Plan]] — schema redesign complete
- [x] [[API Versioning Best Practices]] — versioning strategy decided
- [x] Development environment standardization

### M2: Core Backend (February)
- [ ] [[Authentication Module]] — JWT + RBAC implementation
- [ ] [[API Refactoring]] — v2 endpoints with new schema
- [ ] [[Elasticsearch Semantic Search]] integration for knowledge base
- [ ] Webhook system for external integrations

### M3: Intelligence Layer (March)
- [ ] [[AI-Powered Task Prioritization]] — smart task ordering
- [ ] Natural language task creation
- [ ] [[Voice Commands for Task Management]] — voice interface
- [ ] [[Progressive Disclosure Onboarding]] — adaptive UX

## Architecture Principles

1. **API-first**: Every feature is an API endpoint before it's a UI
2. **Stateless**: No server-side sessions; JWT for auth, ES for search
3. **Event-driven**: Actions emit events; integrations subscribe
4. **Progressive**: Features unlock as users grow; no overwhelming dashboards

## Team

| Role | Person | Focus |
|------|--------|-------|
| Tech Lead | Stardust | Architecture, ES integration |
| Backend | Nikos | Auth, API, database |
| Backend | Elena | Middleware, webhooks |
| Frontend | Mara | UI, onboarding |
| ML/AI | Alex | Prioritization, NLP |

## Key Metrics

- API response time: p95 < 200ms
- Auth flow completion: > 95%
- Onboarding completion: > 70% (up from 35%)
- Daily active users: 2x by end of Q1

## Meeting Cadence

- Weekly [[Planning Session 2026-02-03]] (Mondays)
- Bi-weekly [[Sprint Review 2026-02-07]] (Fridays)
- Daily [[Standup 2026-02-10]] (async in Slack)

## Related Notes

- [[Database Migration Plan]] — P0 infrastructure
- [[Authentication Module]] — P0 security
- [[API Refactoring]] — P0 backend
- [[Elasticsearch Semantic Search]] — search infrastructure
