---
title: JWT Authentication Patterns
tags:
  - research
  - jwt
  - auth
  - security
created: 2026-02-06
updated: 2026-02-06
---

# JWT Authentication Patterns

## Overview

Research on JSON Web Token patterns for the [[Authentication Module]] in [[Helios v2 Roadmap]]. JWTs are stateless tokens that encode claims as a signed JSON payload, eliminating the need for server-side session storage.

## Token Structure

A JWT consists of three Base64URL-encoded parts separated by dots:

```
header.payload.signature
```

- **Header**: Algorithm and token type (`{"alg": "RS256", "typ": "JWT"}`)
- **Payload**: Claims (user ID, roles, expiration)
- **Signature**: Cryptographic verification of header + payload

## Access + Refresh Token Pattern

The recommended approach for Helios:

1. **Access Token** — Short-lived (15 minutes), sent in `Authorization: Bearer` header
2. **Refresh Token** — Long-lived (7 days), stored in HTTP-only cookie, used to obtain new access tokens

### Flow

```
1. User logs in → receives access_token + refresh_token
2. API requests include access_token in Authorization header
3. On 401 → client sends refresh_token to /auth/refresh
4. Server validates refresh_token → issues new access_token
5. On refresh_token expiry → user must re-authenticate
```

## Security Considerations

### Token Storage
- **Access token**: In-memory only (JavaScript variable). Never localStorage.
- **Refresh token**: HTTP-only, Secure, SameSite=Strict cookie.

### Key Rotation
Use RS256 (asymmetric) instead of HS256 (symmetric) so that:
- Only the auth service holds the private key
- All other services verify with the public key
- Key rotation doesn't require redeploying all services

### Revocation
JWTs are stateless, so revocation requires one of:
- Short expiration times (our approach: 15 min access tokens)
- Token blacklist in Redis (check on each request)
- Token versioning in user record (increment on password change)

## Implementation Notes for [[Authentication Module]]

```python
# Token creation (auth service)
payload = {
    "sub": user.id,
    "roles": user.roles,
    "iat": datetime.utcnow(),
    "exp": datetime.utcnow() + timedelta(minutes=15),
}
token = jwt.encode(payload, private_key, algorithm="RS256")
```

The [[API Refactoring]] will add a middleware layer that validates the JWT on every request and injects the decoded claims into the request context.

## Related Notes

- [[Authentication Module]] — implementation of these patterns
- [[API Versioning Best Practices]] — how auth changes across API versions
- [[Planning Session 2026-02-03]] — team discussion on auth approach
