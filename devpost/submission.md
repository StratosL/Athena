# Athena — Second Brain Orchestrator Agent

> Your notes contain buried tasks, scattered ideas, and forgotten commitments. Athena bridges your knowledge vault with your productivity system through intelligent, voice-enabled conversation — powered by Elastic Agent Builder.

[Featured Image: Athena logo on dark background with a glowing connection diagram showing Obsidian vault, Elasticsearch, and Artemis productivity app linked through the Agent Builder orchestrator]

---

## Inspiration

Every knowledge worker faces the same problem: thinking tools and doing tools don't talk to each other.

I capture everything in Obsidian — meeting notes, project plans, research, half-formed ideas. But turning those notes into *actual work* means manually reading through files, copy-pasting action items into a task manager, and deciding what matters today. That's cognitive overhead that compounds daily.

I wanted a single conversational interface — text or voice — that could search my notes semantically, extract tasks with intelligent priority classification, plan my day, and write new notes back into my vault. Not a generic chatbot. An agent that *lives* in my second brain.

When Elastic Agent Builder launched, the architecture clicked: Elasticsearch handles semantic search and analytics over my vault, MCP tools handle real-time reads and writes, and Agent Builder orchestrates the whole thing with a 280-line system prompt that defines Athena's persona, workflows, and guardrails.

## What It Does

Athena is a conversational AI agent that bridges an Obsidian vault (knowledge) with Artemis (productivity app) through 20 tools — 6 ES|QL queries and 14 MCP tools.

**Core capabilities:**

- **Semantic knowledge search** — Ask "what did I write about API versioning?" and Athena finds conceptually related notes using ELSER embeddings, then reads the full content directly from the vault filesystem
- **Task extraction with Eisenhower classification** — Athena reads a note, identifies buried action items, classifies each into an Eisenhower Matrix quadrant with reasoning, and waits for your confirmation before creating them
- **1-3-5 daily planning** — Analyzes pending tasks by priority and deadline, proposes a structured plan (1 major, 3 medium, 5 small tasks), and assigns on approval
- **Bidirectional vault access** — Creates new notes, appends to daily journals, edits existing content, and organizes your vault — all through conversation
- **Voice interaction** — Speak to Athena using Whisper STT, hear responses via OpenAI TTS. The agent never knows if input was typed or spoken — voice is a pure I/O layer
- **Persistent memory** — Conversation summaries are saved to Elasticsearch and daily notes. User profile and agent memory are injected into every session for continuity
- **Proactive heartbeat** — A background service periodically checks for overdue tasks and approaching deadlines, writing alerts to your daily note
- **Web research** — Search the web and save findings directly as vault notes
- **Reusable skills** — Save multi-step workflows (morning routine, weekly review) as vault-based skills that Athena can execute on trigger phrases

**Human-in-the-loop is non-negotiable.** Athena proposes, you approve, then it acts. No silent task creation, no unauthorized edits, no surprises.

[Screenshot: Athena chat conversation showing task extraction from a note — numbered list with Eisenhower quadrant classifications and user confirmation flow]

[Screenshot: Artemis dashboard with Eisenhower Matrix quadrants populated with tasks, daily plan sidebar, and productivity stats bar]

## How We Built It

**Architecture: Dual-path knowledge access.**

The fundamental design insight is that semantic search and direct filesystem access serve different needs — and you need both. Elasticsearch with ELSER handles meaning-based queries, aggregations, and cross-note analytics. Direct vault access via MCP tools handles real-time reads, writes, and structural operations with zero sync delay.

[Diagram: Architecture diagram showing User → Artemis Dashboard (React) → Voice Proxy (STT/TTS) → Agent Builder (Athena) with two paths: ES|QL → Elasticsearch and MCP → Athena MCP Server → Vault/Artemis/Web]

**The stack:**

- **Elastic Agent Builder** — Orchestrator with a 280-line system prompt defining persona, tool routing, 9 workflow patterns, Eisenhower classification rules, and guardrails
- **Elasticsearch Serverless** — Two indices (notes + conversations) with ELSER semantic embeddings. Six ES|QL tools for search, filtering, and aggregation
- **Athena MCP Server** — FastMCP with Streamable HTTP transport, hosting 14 tools across 5 domains (vault, Artemis, knowledge, research, skills). Three consolidated vault tools using the "fewer tools, more parameters" pattern
- **Indexer** — Python CLI that syncs Obsidian markdown + YAML frontmatter into Elasticsearch with checksum-based deduplication and a filesystem watcher for live updates
- **Artemis Backend** — FastAPI REST API for task management, daily planning (1-3-5 rule), pomodoro timers, and productivity analytics
- **Artemis Frontend** — React 18 + TypeScript + TailwindCSS dashboard with 10 pages, glassmorphism design, embedded Athena chat sidebar with voice support
- **Voice Client** — Browser MediaRecorder → Whisper API → text → Agent Builder → response → OpenAI TTS. Zero backend changes — voice is a presentation concern
- **Heartbeat Service** — APScheduler running during active hours, reads a vault checklist, calls the Kibana converse API, and delivers alerts to daily notes
- **Docker Compose** — Six services orchestrated with volume-mounted vault access and ngrok tunnel for MCP connectivity

[Screenshot: MCP server tool registration showing the 14 tools organized by domain — vault, artemis, knowledge, research, skills]

## Challenges We Ran Into

**MCP transport evolution.** The MCP spec moved from SSE to Streamable HTTP during development. We had to adapt our server mounting strategy — the key lesson was mounting at `/` rather than a sub-path, which wasn't obvious from the docs.

**Agent Builder field naming.** The Kibana API uses different field names than the documentation suggests in some places. Debugging tool registration and connector configuration required careful API exploration and several iterations.

**Dual-path consistency.** When Elasticsearch and the vault filesystem can both answer "what notes do I have?", making them agree required the checksum-based dedup strategy in the indexer and clear tool selection guidance in the system prompt.

**System prompt engineering.** Getting Agent Builder to reliably follow the human-in-the-loop pattern — always present before executing — required explicit guardrails, workflow patterns, and classification examples. The prompt went through dozens of iterations to reach 280 lines of precise instructions.

## Accomplishments That We're Proud Of

- **20 tools working end-to-end** — 6 ES|QL + 14 MCP tools, all registered in Agent Builder and responding correctly
- **The 3-tool vault consolidation** — Instead of 12 single-purpose vault tools, three tools (`vault_query`, `vault_read`, `vault_manage`) with operation parameters keep the agent's tool selection clean
- **Voice as a pure I/O layer** — Zero backend changes for voice support. The agent is modality-agnostic by design
- **280-line system prompt** — Covers persona, tool selection matrix, 9 workflow patterns, Eisenhower classification rules, 1-3-5 planning, memory management, and guardrails — all in one coherent document
- **Proactive heartbeat** — Athena doesn't just respond. It periodically checks on you and writes alerts to your daily note when deadlines approach
- **Full productivity suite** — Dashboard, task management, daily planning, pomodoro timers, analytics, and a dedicated Athena chat page — all with a polished glassmorphism UI

[Screenshot: Voice interaction — user speaking to Athena with audio waveform visualization, showing the transcription and Athena's spoken response]

[Screenshot: Daily planning conversation — Athena proposing a 1-3-5 plan with task assignments and user confirming]

## What We Learned

**Context engineering is the real skill.** Building an agent isn't about the LLM — it's about designing the right tools, writing precise system prompts, and giving the model enough context to make good decisions. The 280-line system prompt matters more than which model you choose.

**Elasticsearch as a memory layer is powerful.** Storing conversation summaries with semantic embeddings means Athena can recall past discussions by meaning, not just keywords. Combined with vault-injected user profiles, this creates genuine session continuity.

**The "fewer tools, more parameters" pattern scales.** Consolidating 12 vault operations into 3 tools with operation parameters reduced Agent Builder's decision space and improved tool selection accuracy dramatically.

**Human-in-the-loop requires explicit design.** Agents *want* to be helpful and act immediately. Making them reliably stop, present, and wait for confirmation requires explicit workflow patterns and guardrails in the system prompt — not just a single instruction.

## What's Next

- **Elastic Workflows** — Automate the vault watcher and daily planning assistant using Elastic's new YAML-based rules engine
- **Wake word detection** — "Hey Athena" for hands-free activation
- **Streaming TTS** — Progressive audio playback for faster voice responses
- **Backlink analysis** — Use Elasticsearch to traverse wikilink graphs and surface hidden connections between notes
- **Multi-user support** — Authentication and per-user vault isolation

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
