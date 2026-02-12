---
title: API Refactoring
tags:
  - api
  - refactoring
  - backend
  - helios
created: 2026-02-03
updated: 2026-02-10
---

# API Refactoring

## Objective

Refactor the Helios API from v1 (monolithic, session-based) to v2 (modular, JWT-based) as defined in [[Helios v2 Roadmap]]. This is the largest backend workstream for Q1 2026.

## Scope

### Endpoints to Migrate

| Group | v1 Endpoints | v2 Changes |
|-------|-------------|------------|
| Tasks | 8 endpoints | Add filtering, pagination, bulk operations |
| Projects | 5 endpoints | New nested resource structure |
| Users | 4 endpoints | JWT auth, profile settings |
| Search | 2 endpoints | Replace SQL LIKE with [[Elasticsearch Semantic Search]] |
| Webhooks | 0 | New: 3 endpoints for webhook CRUD |
| Reports | 3 endpoints | New aggregation engine |

### Dependencies

- [[Database Migration Plan]] must complete Phase 2 before v2 endpoints go live
- [[Authentication Module]] JWT middleware must be deployed first
- [[API Versioning Best Practices]] defines our `/api/v2/` prefix strategy

## Task Breakdown

- [ ] Define OpenAPI 3.1 spec for all v2 endpoints
- [ ] Implement task CRUD with new schema and pagination
- [ ] Implement project endpoints with nested task resources
- [ ] Migrate search endpoints to Elasticsearch
- [ ] Add webhook registration and delivery system
- TODO: Set up API integration test suite with pytest + httpx
- Action item: Review rate limiting strategy before launch

## Design Decisions

### Pagination
Cursor-based pagination for all list endpoints. Offset-based pagination breaks when items are inserted/deleted during traversal. Cursor approach:

```json
{
  "data": [...],
  "cursor": {
    "next": "eyJpZCI6MTAwfQ==",
    "has_more": true
  }
}
```

### Error Format
Standardized error response across all v2 endpoints:

```json
{
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task with ID 42 does not exist",
    "details": {}
  }
}
```

### Rate Limiting
Per-user rate limits using Redis sliding window. Default: 100 requests/minute for authenticated users, 20/minute for unauthenticated. Heavy endpoints (search, reports) have lower individual limits.

## Progress Tracking

Sprint work tracked in [[Sprint Review 2026-02-07]] and daily status in [[Standup 2026-02-10]].

### Current Sprint (Feb 3-14)
- Nikos: Task CRUD endpoints (in progress)
- Elena: Middleware + error handling (in progress)
- Stardust: Elasticsearch integration (not started)

## Risks

1. **Schema dependency**: Any delay in [[Database Migration Plan]] blocks v2 endpoint testing
2. **ELSER inference latency**: Need to benchmark [[Elasticsearch Semantic Search]] under load
3. **Client migration**: Frontend team needs 2 weeks after API freeze to update

## Related

- [[Helios v2 Roadmap]] — parent epic
- [[API Versioning Best Practices]] — versioning research
- [[Database Migration Plan]] — schema dependency
- [[Authentication Module]] — auth middleware
- [[Planning Session 2026-02-03]] — initial scope discussion
- [[Sprint Review 2026-02-07]] — progress review
