---
title: Voice Commands for Task Management
tags:
  - idea
  - voice
  - ux
  - helios
created: 2026-02-11
updated: 2026-02-11
---

# Voice Commands for Task Management

## Concept

Extend [[Helios v2 Roadmap]] with voice-first task management. Users speak natural language commands that get transcribed and interpreted:

- "Add a task to review the [[API Refactoring]] pull requests by Friday"
- "What are my top priorities today?" (leverages [[AI-Powered Task Prioritization]])
- "Mark the database migration task as complete"

## Technical Stack

- **Whisper API** for speech-to-text transcription
- **Intent parser** to extract action, entity, and parameters from transcribed text
- **TTS response** using OpenAI TTS for confirmation and status readback

## Why This Matters

Hands-free task management during commutes, cooking, or exercise. Reduces friction for quick capture — the biggest barrier to consistent task tracking.

## Related

- [[AI-Powered Task Prioritization]] — voice query "what should I do next?"
- [[Progressive Disclosure Onboarding]] — voice features for power users only
