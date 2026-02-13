# ADR-002: Single Orchestrator Agent Over Sub-Agent Architecture

**Date:** 2026-02-13
**Status:** Accepted
**Context:** Athena has 19 tools (6 ES|QL + 13 MCP) across 4 domains — should we split into multiple specialized agents?

---

## Problem

Athena's tool surface spans four domains:
- **Vault** (3 MCP tools with 13 operations) — read/write/query Obsidian notes
- **Artemis** (7 MCP tools) — task management, daily plans, analytics, pomodoro
- **Knowledge** (1 MCP tool + 5 ES|QL tools) — search, memory, conversation history
- **Research** (2 MCP tools) — web search, URL fetching

Concern: giving one agent 19 tools and a 244-line system prompt could lead to poor tool selection, confused reasoning, or degraded response quality. Would a multi-agent architecture (orchestrator + specialized sub-agents) perform better?

## Options Evaluated

### Option A: Single Agent with All Tools (Selected)

One Athena agent on Elastic Agent Builder with all 19 tools and a comprehensive system prompt that includes tool routing logic, workflow patterns, and behavioral guardrails.

### Option B: Orchestrator + Sub-Agents — Rejected

An Athena orchestrator that delegates to specialized sub-agents:
- **Vault Agent** — handles all vault read/write/query operations
- **Task Agent** — manages Artemis tasks, daily plans, analytics
- **Research Agent** — web search, URL fetching, summarization
- **Knowledge Agent** — semantic search, conversation memory

## Analysis

### Tool count is within safe bounds

Modern LLMs (GPT-4o, Claude) handle 20-30 tools with reliable selection accuracy. Degradation is observed around 30-40+ tools. At 19 tools, Athena is comfortably within the safe range.

The 3-tool vault consolidation pattern (`vault_query`, `vault_read`, `vault_manage` with operation parameters) already reduces cognitive load — the LLM sees 3 vault tools instead of 13 separate endpoints. This is the pattern Anthropic recommends: fewer tools with more parameters.

### Cross-domain context is essential

Athena's core value proposition requires fluid cross-domain reasoning in a single conversation turn:

> "Read my sprint review notes, extract the action items, classify them by Eisenhower quadrant, and create them as tasks in Artemis."

This requires vault access → content understanding → classification reasoning → Artemis task creation — all in one coherent flow. With sub-agents, context would need to be serialized and passed between agents at each boundary, losing nuance and adding latency.

Other cross-domain flows:
- Daily planning: read vault notes (priorities) + query Artemis (pending tasks) + create plan
- Idea capture: understand user intent + create vault note + index to ES
- Productivity check-in: Artemis analytics + vault daily notes + conversation history

### Elastic Agent Builder is a single-agent platform

Agent Builder provides conversation management, tool routing, and LLM orchestration for one agent. It does not have native sub-agent support. Implementing multi-agent orchestration would require:

1. Building a custom routing layer outside Agent Builder
2. Managing conversation state across multiple agent instances
3. Handling agent-to-agent communication (likely via additional MCP tools or HTTP calls)
4. Losing Agent Builder's built-in conversation UI and memory

This is significant custom infrastructure — inappropriate for a hackathon with 14 days remaining.

### Latency compounds with sub-agents

Each agent hop adds an LLM inference round-trip:

| Architecture | Hops for "extract tasks from notes" |
|-------------|-------------------------------------|
| Single agent | User → Athena → vault tool → Athena → Artemis tool → User |
| Sub-agents | User → Orchestrator → Vault Agent → vault tool → Orchestrator → Task Agent → Artemis tool → Orchestrator → User |

Sub-agents add 2-4 extra LLM calls per complex request. At ~2-5 seconds per inference, that's 4-20 seconds of added latency. For a demo, responsiveness matters.

### More agents = more failure modes

Each agent-to-agent handoff is a point where:
- Context can be lost or poorly summarized
- Tool selection can fail (orchestrator picks wrong sub-agent)
- Errors need propagation across boundaries
- Conversation coherence degrades

For a recorded demo, reliability outweighs architectural elegance.

## Decision

**Use a single Athena agent with all 19 tools.** Manage complexity through:

1. **3-tool consolidation** — vault operations grouped into 3 tools with operation parameters
2. **System prompt routing** — tool selection decision matrix in the 244-line prompt
3. **Clear tool descriptions** — unambiguous descriptions in MCP `@tool()` decorators and ES|QL tool configs
4. **Domain grouping** — tools organized by group (vault, Artemis, knowledge, research) in the prompt

## Consequences

- Single conversation context — cross-domain reasoning works naturally
- No inter-agent communication overhead
- Simpler debugging (one agent, one prompt, one conversation)
- Relies on system prompt quality for tool routing accuracy
- If tool count grows beyond ~30 in future, revisit this decision

## When to Revisit

Sub-agents would make sense if Athena evolves to include:

| Trigger | Potential Sub-Agent |
|---------|-------------------|
| 30+ tools with degraded selection accuracy | Split by domain |
| Multi-step research with iterative search/fetch/summarize loops | Dedicated Research Agent with its own scratchpad |
| Complex multi-constraint scheduling (calendar + deadlines + energy levels) | Dedicated Planning Agent with specialized reasoning |
| Bulk vault operations (graph traversal, backlink analysis, bulk tagging) | Dedicated Vault Librarian Agent |
| Multi-user support with different permission levels | Per-user agent instances |

None of these are in MVP scope. Revisit post-hackathon based on actual usage patterns.
