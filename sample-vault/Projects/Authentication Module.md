---
title: Authentication Module
tags:
  - auth
  - security
  - backend
  - helios
created: 2026-02-01
updated: 2026-02-06
---

# Authentication Module

## Overview

Redesign the Helios authentication system for v2, replacing the current session-based auth with JWT tokens. This implements the patterns documented in [[JWT Authentication Patterns]].

## Goals

1. Stateless authentication via JWT (access + refresh tokens)
2. Role-based access control (RBAC) with granular permissions
3. OAuth2 provider support (Google, GitHub) for social login
4. API key authentication for programmatic access
5. Audit logging of all auth events

## Architecture

```
Client → API Gateway → JWT Middleware → Route Handler
                           ↓
                     Token Validation
                     (RS256 public key)
                           ↓
                     Claims Injection
                     (user_id, roles)
```

The JWT middleware validates tokens on every request and injects decoded claims into the request context. Failed validation returns 401 with a machine-readable error code.

## Dependencies

- [[Database Migration Plan]] — needs `user_roles` and `api_keys` tables
- [[API Versioning Best Practices]] — auth headers change between v1 and v2
- [[API Refactoring]] — middleware integration point

## Implementation Status

| Component | Status | Owner |
|-----------|--------|-------|
| JWT signing/verification | Done | Nikos |
| Refresh token rotation | In Progress | Nikos |
| RBAC middleware | Not Started | Elena |
| OAuth2 providers | Not Started | — |
| API key management | Not Started | — |
| Audit logging | Not Started | — |

## Security Review

Scheduled for after the [[Sprint Review 2026-02-07]]. Key areas:
- Token storage in frontend (must be in-memory only)
- Refresh token reuse detection
- Rate limiting on auth endpoints
- CORS configuration for token endpoints

## Related

- [[JWT Authentication Patterns]] — research backing these decisions
- [[Helios v2 Roadmap]] — P0 deliverable
- [[Planning Session 2026-02-03]] — auth design finalized
