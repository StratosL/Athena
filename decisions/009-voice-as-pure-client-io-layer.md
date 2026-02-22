# ADR-009: Voice as Pure Client I/O Layer

**Date:** 2026-02-14
**Status:** Accepted
**Context:** Athena needs voice input/output — where should voice logic live?

---

## Problem

The agent should support spoken interaction: user speaks → agent responds with audio. The question is where to put the voice processing pipeline and whether the agent needs to know about voice.

## Options

### Option A: Agent-Aware Voice — Rejected

Add voice-specific tools to the agent (e.g., `speak_response`, `listen_for_input`). The agent decides when to use voice.

- **Pro:** Agent can control voice behavior (tone, pacing, emphasis)
- **Con:** Couples voice to the orchestrator. Every tool call now needs voice-awareness. System prompt complexity increases. Agent Builder doesn't natively support audio I/O.

### Option B: Backend Voice Service — Rejected

Build a voice service that wraps the agent — intercepts requests, handles STT/TTS, forwards text to the agent.

- **Pro:** Centralized voice handling
- **Con:** New service between user and agent. Adds latency. Must handle streaming. Duplicates conversation management.

### Option C: Client-Side Voice (Selected)

Voice processing lives entirely in the client layer (browser + thin proxy). The agent never knows if input was typed or spoken.

```
[Mic] → MediaRecorder → Whisper API → text → Agent → response text → TTS API → [Speaker]
```

## Decision

Voice is a **presentation concern**, not an agent concern:

- **Browser:** `MediaRecorder` API captures audio. React hooks (`useVoiceRecorder`, `useAthenaVoice`) manage the recording state.
- **Voice Proxy:** aiohttp server with 3 endpoints — `/api/transcribe` (Whisper STT), `/api/speak` (OpenAI TTS), `/api/chat` (forwards to Kibana converse API).
- **Agent:** Receives text, returns text. Zero voice awareness.

The same agent response renders as text in the chat sidebar and as audio when voice mode is on. Toggle is purely a client-side state.

## Consequences

- **Zero backend changes** for voice support — MCP server, indexer, agent prompt untouched
- Voice is additive — if voice breaks, text chat still works perfectly (P3 priority validated)
- Voice proxy is stateless — easy to scale, easy to debug
- Same conversation can switch between text and voice mid-stream
- Limitation: no prosody control (emphasis, pausing) — TTS reads flat text
- Limitation: no streaming TTS — full response must complete before audio starts (~2-5s delay)
- Future: OpenAI Realtime API could provide full-duplex voice, but requires its own model (can't use Agent Builder as the brain)
