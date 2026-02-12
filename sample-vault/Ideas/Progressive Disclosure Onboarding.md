---
title: Progressive Disclosure Onboarding
tags:
  - idea
  - onboarding
  - ux
  - helios
created: 2026-02-10
updated: 2026-02-10
---

# Progressive Disclosure Onboarding

## The Problem

New users in [[Helios v2 Roadmap]] are overwhelmed by the full feature set on first login. Current onboarding shows a 12-step tutorial that most users skip.

## The Idea

Instead of showing everything upfront, reveal features progressively as users demonstrate mastery of simpler ones:

1. **Day 1**: Task creation only — single input, no projects or tags
2. **Week 1**: Introduce projects and basic organization after user creates 5+ tasks
3. **Week 2**: Unlock tags, filters, and custom views after user completes 10+ tasks
4. **Month 1**: Show automations, integrations, and [[AI-Powered Task Prioritization]] after consistent usage

## Implementation Sketch

Track a `user.onboarding_stage` enum: `beginner → intermediate → advanced → power_user`. Each stage gates which UI elements and [[API Refactoring]] endpoints are exposed.

## Inspiration

Notion and Linear both use progressive disclosure effectively. Figma's approach of contextual tooltips (showing features when the user is in the right context) is particularly elegant.

## Open Questions

- How do we handle users who are power users from day one? Skip-ahead mechanism?
- Should we allow manual stage advancement in settings?
- What metrics define "mastery" for each stage?
