---
title: Database Migration Plan
tags:
  - database
  - postgresql
  - migration
  - helios
created: 2026-01-28
updated: 2026-02-03
---

# Database Migration Plan

## Objective

Migrate the Helios database from the legacy schema (v1) to the new normalized schema required by [[Helios v2 Roadmap]]. This is a prerequisite for the [[API Refactoring]] and [[Authentication Module]] work.

## Current State

- PostgreSQL 15, single database, 47 tables
- Several denormalized tables from early prototyping
- No foreign key constraints on 12 tables (added organically)
- ~500K rows in the tasks table, ~2M in activity_log

## Migration Steps

### Phase 1: Schema Changes (Non-Breaking)
- Add new columns with defaults alongside old ones
- Create new junction tables for many-to-many relationships
- Add missing foreign key constraints with `NOT VALID` (validate later)

### Phase 2: Data Backfill
- Run backfill scripts to populate new columns from old data
- Validate data integrity with checksums per table
- Foreign key validation: `ALTER TABLE ... VALIDATE CONSTRAINT`

### Phase 3: Code Cutover
- Update ORM models to use new columns
- Deploy with feature flag to switch between old/new queries
- Monitor query performance via pg_stat_statements

### Phase 4: Cleanup
- Drop deprecated columns (after 2-week bake period)
- Remove feature flags and legacy query paths
- Update database documentation

## Rollback Strategy

Each phase is independently reversible. Phase 1 additions don't break existing queries. Phase 2 backfills can be re-run. Phase 3 feature flag allows instant rollback.

## Timeline

Discussed in [[Planning Session 2026-02-03]] — estimated 3 weeks total, starting after [[Sprint Review 2026-02-07]].

## Related

- [[API Refactoring]] — depends on this migration completing
- [[Helios v2 Roadmap]] — this is a P0 infrastructure task
- [[Authentication Module]] — needs the new user_roles table from this migration
