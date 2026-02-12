---
title: API Versioning Best Practices
tags:
  - research
  - api
  - versioning
  - best-practices
created: 2026-02-05
updated: 2026-02-05
---

# API Versioning Best Practices

## Context

As part of the [[API Refactoring]] effort for [[Helios v2 Roadmap]], we need a clear versioning strategy. This research covers the major approaches, trade-offs, and our recommended path forward.

## Versioning Strategies

### 1. URI Path Versioning

```
GET /api/v1/tasks
GET /api/v2/tasks
```

**Pros:** Explicit, easy to understand, simple routing. Most common in public APIs.
**Cons:** Pollutes URL space, harder to deprecate, clients hardcode version in URLs.

### 2. Header-Based Versioning

```
GET /api/tasks
Accept: application/vnd.helios.v2+json
```

**Pros:** Clean URLs, version is metadata not resource identity.
**Cons:** Harder to test in browser, less discoverable, proxy/cache complications.

### 3. Query Parameter Versioning

```
GET /api/tasks?version=2
```

**Pros:** Easy to add, optional (can default to latest).
**Cons:** Caching issues, easy to forget, not RESTful purists' choice.

### 4. Content Negotiation

Use `Accept` headers with media types to negotiate format and version simultaneously. Most flexible but most complex to implement.

## Recommendation for Helios

**URI path versioning** (`/api/v2/`) for the following reasons:

1. Team familiarity — all backend developers have used this pattern before
2. Infrastructure compatibility — our reverse proxy and API gateway handle path-based routing natively
3. Testing simplicity — endpoints are testable via browser and curl without header manipulation
4. Documentation clarity — [[Helios v2 Roadmap]] requires clear separation between v1 (legacy) and v2 (new) endpoints

## Migration Strategy

### Phase 1: Dual Running (Weeks 1-4)
- Deploy v2 endpoints alongside v1
- Both versions hit the same [[Database Migration Plan]] schema
- Add deprecation headers to v1 responses: `Sunset: 2026-06-01`

### Phase 2: Client Migration (Weeks 5-8)
- Update frontend and mobile clients to v2
- Monitor v1 traffic metrics
- Send deprecation notices to external consumers

### Phase 3: Sunset v1 (Weeks 9-12)
- Redirect v1 → v2 with 301 where possible
- Return 410 Gone for incompatible endpoints
- Remove v1 route handlers from codebase

## Versioning Lessons from Industry

Netflix uses URI path versioning for public APIs but header-based for internal microservice communication. Stripe uses date-based versioning (`2026-01-15`) which gives them finer granularity — worth considering if our API surface grows significantly.

GitHub uses a hybrid: URI versioning for major versions and `Accept` header media types for format variations within a version.

## Related Notes

- [[API Refactoring]] — implementation plan for the v1→v2 migration
- [[Database Migration Plan]] — schema changes required by v2
- [[Authentication Module]] — auth changes in v2 (JWT standardization)
- [[JWT Authentication Patterns]] — token format research
