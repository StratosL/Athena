# Athena — Second Brain Orchestrator Agent

> Your notes contain buried tasks, scattered ideas, and forgotten commitments. Athena bridges your knowledge vault with your productivity system through intelligent, voice-enabled conversation — powered by Elastic Agent Builder.

---

## Inspiration

Every knowledge worker faces the same problem: thinking tools and doing tools don't talk to each other.

I capture everything in Obsidian — meeting notes, project plans, research, half-formed ideas. But turning those notes into actual work means manually reading through files, copy-pasting action items into a task manager, and deciding what matters today. That's cognitive overhead that compounds daily.

I wanted a single conversational interface — text or voice — that could search my notes semantically, extract tasks with intelligent priority classification, plan my day, and write new notes back into my vault. Not a generic chatbot. An agent that lives in my second brain.

When Elastic Agent Builder launched, the architecture clicked: Elasticsearch handles semantic search and analytics over my vault, MCP tools handle real-time reads and writes, and Agent Builder orchestrates the whole thing with a 280-line system prompt that defines Athena's persona, workflows, and guardrails.

## What it does

Athena is a conversational AI agent that bridges an Obsidian vault (knowledge) with Artemis (productivity app) through 20 tools — 6 ES|QL queries and 14 MCP tools.

**Semantic knowledge search** — Ask "what did I write about API versioning?" and Athena finds conceptually related notes using ELSER embeddings, then reads the full content directly from the vault filesystem.

**Task extraction with Eisenhower classification** — Athena reads a note, identifies buried action items, classifies each into an Eisenhower Matrix quadrant with reasoning, and waits for your confirmation before creating them.

**1-3-5 daily planning** — Analyzes pending tasks by priority and deadline, proposes a structured plan (1 major, 3 medium, 5 small tasks), and assigns on approval.

**Bidirectional vault access** — Creates new notes, appends to daily journals, edits existing content, and organizes your vault — all through conversation.

**Voice interaction** — Speak to Athena using Whisper STT, hear responses via OpenAI TTS. The agent never knows if input was typed or spoken — voice is a pure I/O layer.

**Persistent memory** — Conversation summaries saved to Elasticsearch and daily notes. User profile and agent memory injected into every session for continuity.

**Proactive heartbeat** — A background service periodically checks for overdue tasks and approaching deadlines, writing alerts to your daily note.

**Reusable skills** — Multi-step workflows (morning routine, weekly review) stored as vault Markdown files that Athena loads and executes on trigger phrases.

Human-in-the-loop is non-negotiable. Athena proposes, you approve, then it acts. No silent task creation, no unauthorized edits, no surprises.

## How we built it

The fundamental design insight is dual-path knowledge access: semantic search and direct filesystem access serve different needs, and you need both. Elasticsearch with ELSER handles meaning-based queries, aggregations, and cross-note analytics. Direct vault access via MCP tools handles real-time reads, writes, and structural operations with zero sync delay.

The stack:

- **Elastic Agent Builder** — Orchestrator with a 280-line system prompt defining persona, tool routing, 9 workflow patterns, Eisenhower classification rules, and guardrails
- **Elasticsearch Serverless** — Two indices (notes + conversations) with ELSER semantic embeddings. Six ES|QL tools for search, filtering, and aggregation
- **Athena MCP Server** — FastMCP with Streamable HTTP transport, 14 tools across 5 domains (vault, Artemis, knowledge, research, skills). Three consolidated vault tools using the "fewer tools, more parameters" pattern
- **Indexer** — Python CLI that syncs Obsidian markdown + YAML frontmatter into Elasticsearch with checksum-based deduplication and a live filesystem watcher
- **Artemis** — FastAPI backend + React 18/TypeScript/TailwindCSS frontend. Task management, daily planning, pomodoro timers, analytics, embedded Athena chat sidebar with voice
- **Voice Client** — Browser MediaRecorder → Whisper API → text → Agent Builder → response → OpenAI TTS
- **Heartbeat Service** — APScheduler calling the Kibana converse API during active hours, delivering alerts to daily notes
- **Docker Compose** — Six services orchestrated with volume-mounted vault access and ngrok tunnel for MCP connectivity

## Challenges we ran into

**MCP transport.** The MCP spec moved from SSE to Streamable HTTP during development. The key lesson was mounting at `/` rather than a sub-path — not obvious from the docs.

**Agent Builder API.** The Kibana API uses different field names than the documentation suggests in places (`instructions` not `system_prompt`, `serverUrl` not `url`). Tool registration and connector configuration required careful API exploration.

**Dual-path consistency.** When Elasticsearch and the vault filesystem can both answer "what notes do I have?", keeping them in sync required a checksum-based dedup strategy in the indexer and clear tool selection guidance in the system prompt.

**System prompt engineering.** Getting Agent Builder to reliably follow the human-in-the-loop pattern — always present before executing — required explicit guardrails, workflow patterns, and classification examples. The prompt went through dozens of iterations to reach 280 lines.

## Accomplishments that we're proud of

- **20 tools working end-to-end** — 6 ES|QL + 14 MCP tools, all registered in Agent Builder and responding correctly
- **3-tool vault consolidation** — Instead of 12 single-purpose tools, three tools with operation parameters keep the agent's tool selection clean and accurate
- **Voice as a pure I/O layer** — Zero backend changes for voice support. The agent is modality-agnostic by design
- **280-line system prompt** — Persona, tool selection matrix, 9 workflow patterns, Eisenhower classification, 1-3-5 planning, memory management, and guardrails in one coherent document
- **Proactive heartbeat** — Athena doesn't just respond. It periodically checks on you and writes alerts to your daily note when deadlines approach
- **Full productivity suite** — Dashboard, tasks, daily planning, pomodoro timers, analytics, and a dedicated Athena chat page with a polished glassmorphism UI

## What we learned

**Context engineering is the real skill.** Building an agent isn't about the LLM — it's about designing the right tools, writing precise system prompts, and giving the model enough context to make good decisions. The 280-line system prompt matters more than which model you choose.

**Elasticsearch as a memory layer is powerful.** Storing conversation summaries with semantic embeddings means Athena can recall past discussions by meaning, not just keywords. Combined with vault-injected user profiles, this creates genuine session continuity.

**The "fewer tools, more parameters" pattern scales.** Consolidating 12 vault operations into 3 tools with operation parameters reduced Agent Builder's decision space and improved tool selection accuracy dramatically.

**Human-in-the-loop requires explicit design.** Agents want to be helpful and act immediately. Making them reliably stop, present, and wait for confirmation requires explicit workflow patterns and guardrails in the system prompt — not just a single instruction.

## What's next for Athena - Second Brain Orchestrator Agent

- **Elastic Workflows** — Automate the vault watcher and daily planning assistant using Elastic's rules engine
- **Streaming TTS** — Progressive audio playback for sub-second voice response feel
- **Wake word detection** — "Hey Athena" for hands-free activation via Picovoice Porcupine
- **Backlink analysis** — Traverse Obsidian wikilink graphs via Elasticsearch to surface hidden connections between notes
- **Community skill marketplace** — Share reusable multi-step workflows (weekly reviews, project planning templates) across users

## Built With

- Elastic Agent Builder
- Elasticsearch Serverless (ELSER)
- ES|QL
- Model Context Protocol (MCP)
- Python
- FastAPI
- FastMCP
- React
- TypeScript
- TailwindCSS
- Docker
- OpenAI Whisper API
- OpenAI TTS API
- Obsidian
- ngrok
