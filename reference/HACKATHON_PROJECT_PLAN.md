# Athena: Second Brain Productivity Agent
## Elasticsearch Agent Builder Hackathon — Project Plan

**Developer:** Stratos Louvaris (solo)
**Hackathon:** Elasticsearch Agent Builder Hackathon (Devpost)
**Deadline:** February 27, 2026, 1:00 PM EST (20:00 Athens time)
**Prize Pool:** $20,000 ($10K / $5K / $3K + 4×$500 Creative Awards)
**Today:** February 10, 2026 — **17 days remaining**

---

## 1. Project Concept

### The Problem

Knowledge workers live in two disconnected worlds: **thinking** (notes, ideas, conversations, brainstorms scattered across tools) and **doing** (task managers, calendars, to-do lists). The gap between "I had a great idea" and "I'm actually working on it" is where productivity dies. People capture ideas in Obsidian, journals, docs, and Slack messages — but those ideas rarely become actionable tasks with clear priorities and deadlines.

### The Solution: Athena

**Athena** is an AI agent that bridges the gap between your **Second Brain** (knowledge base) and your **Execution System** (Artemis productivity app). It acts as an intelligent productivity assistant that can:

1. **Ingest & Index** your Obsidian vault (Markdown notes) into Elasticsearch for intelligent semantic search
2. **Converse** with you about your projects, ideas, and priorities — pulling relevant context from your knowledge base
3. **Extract & Classify** actionable tasks from conversations and notes, automatically categorizing them by urgency/importance (Eisenhower Matrix)
4. **Push to Artemis** via MCP — creating tasks, assigning them to daily plans (1-3-5 rule), and triggering Pomodoro sessions
5. **Brainstorm & Plan** — helping you break down large projects into actionable steps, stored back in your knowledge base
6. **Track & Report** — pulling analytics from Artemis to give you productivity insights in natural language

### One-Line Pitch

> "Athena turns your scattered notes and ideas into prioritized, actionable tasks — automatically."

### Why This Wins

- **Connects disconnected systems** (Obsidian ↔ Elasticsearch ↔ Artemis) — explicit hackathon track
- **Embeds where work happens** — lives inside your existing workflow — explicit track
- **Shows measurable impact** — "X ideas became Y completed tasks" — explicit track
- **Lets agents take reliable action** — creates real tasks, assigns plans — explicit track
- **Narrow domain agent** — productivity/personal knowledge management — explicit track
- **Multi-step reasoning** — reads notes → extracts tasks → classifies → pushes to Artemis
- **Tool-driven** — uses ES|QL, Elastic Workflows, MCP, search tools — not just prompts

---

## 2. Architecture

### High-Level Data Flow

```
┌─────────────┐     Index      ┌──────────────────────┐
│   Obsidian   │───────────────▶│    Elasticsearch     │
│  Vault (.md) │    (sync)     │   (Second Brain DB)   │
└─────────────┘                │                       │
                               │  • Notes index        │
                               │  • Ideas index        │
                               │  • Conversations idx  │
                               │  • Tasks index        │
                               └──────────┬───────────┘
                                          │
                                          │ ES|QL Tools
                                          │ Search Tools
                                          ▼
┌─────────────┐   Chat API    ┌──────────────────────┐
│    User      │◀────────────▶│   Elastic Agent       │
│  (Browser)   │              │   Builder             │
└─────────────┘              │                       │
                               │  • Reasoning (LLM)   │
                               │  • Built-in Search   │
                               │  • Custom ES|QL Tools│
                               │  • MCP Client        │
                               │  • Elastic Workflows │
                               └──────────┬───────────┘
                                          │
                                          │ MCP Protocol
                                          ▼
                               ┌──────────────────────┐
                               │   Artemis MCP Server  │
                               │   (FastAPI + Pydantic)│
                               │                       │
                               │  Tools:               │
                               │  • create_task        │
                               │  • list_tasks         │
                               │  • assign_daily_plan  │
                               │  • complete_task      │
                               │  • get_analytics      │
                               │  • start_pomodoro     │
                               └──────────────────────┘
                                          │
                                          │ REST API
                                          ▼
                               ┌──────────────────────┐
                               │   Artemis Backend     │
                               │   (Existing FastAPI)  │
                               │                       │
                               │   Supabase (Postgres) │
                               └──────────────────────┘
```

### Component Breakdown

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Knowledge Base** | Obsidian (local .md files) | Source of truth for notes, ideas, projects |
| **Indexer** | Python script + `elasticsearch` client | Syncs Obsidian vault → Elasticsearch indices |
| **Search & Retrieval** | Elasticsearch (Serverless) | Semantic search, full-text search, vector embeddings |
| **Agent Brain** | Elastic Agent Builder | Reasoning, tool orchestration, conversation management |
| **Agent Tools** | ES|QL + MCP + Elastic Workflows | Custom tools for search, task extraction, Artemis integration |
| **Artemis Bridge** | MCP Server (FastAPI + Pydantic AI) | Exposes Artemis capabilities as MCP tools |
| **Execution Engine** | Artemis (existing app) | Task management, daily planning, Pomodoro timer |
| **Frontend** | Artemis frontend (extended) | Chat interface embedded in existing dashboard |

### Elasticsearch Indices

| Index | Purpose | Key Fields |
|-------|---------|------------|
| `second-brain-notes` | Obsidian notes indexed | `title`, `content`, `tags`, `path`, `created_at`, `updated_at`, `content_vector` |
| `second-brain-ideas` | Extracted ideas/insights | `idea`, `source_note`, `category`, `status`, `created_at` |
| `second-brain-conversations` | Agent conversation logs | `messages`, `extracted_tasks`, `topics`, `timestamp` |
| `second-brain-projects` | Project tracking | `name`, `description`, `status`, `related_notes`, `tasks` |

### Agent Builder Tools (ES|QL-based)

| Tool Name | Type | Description |
|-----------|------|-------------|
| `search_knowledge_base` | Built-in Search | Semantic search across all notes and ideas |
| `find_related_notes` | ES|QL | Find notes related to a topic using full-text + vector search |
| `extract_action_items` | ES|QL + LLM | Parse notes for actionable tasks |
| `store_idea` | ES|QL | Save a new idea/insight to the ideas index |
| `list_projects` | ES|QL | Get all active projects with status |
| `update_project` | ES|QL | Update project status or add notes |
| `get_productivity_summary` | ES|QL | Query conversation + task completion data |

### Artemis MCP Tools

| Tool Name | Maps To | Description |
|-----------|---------|-------------|
| `create_task` | `POST /tasks` | Create a task with title, quadrant, pomodoro_estimate |
| `list_tasks` | `GET /tasks` | List tasks, optionally filtered by quadrant or status |
| `complete_task` | `POST /tasks/{id}/complete` | Mark a task as done |
| `get_daily_plan` | `GET /daily-plans/today` | Get today's 1-3-5 plan |
| `assign_to_plan` | `POST /daily-plans/{id}/assign` | Assign a task to a plan slot (major/medium/small) |
| `get_analytics` | `GET /analytics/summary` | Get productivity metrics |
| `start_pomodoro` | `POST /pomodoro/sessions` | Start a Pomodoro session for a task |

### Elastic Workflows (Automation)

| Workflow | Trigger | Actions |
|----------|---------|---------|
| `daily_planning_assistant` | Scheduled (morning) | Scans unassigned tasks → suggests 1-3-5 plan → creates plan via MCP |
| `note_watcher` | New note indexed | Scans for action items → creates tasks in Artemis |
| `weekly_review` | Scheduled (Friday) | Generates productivity report from Artemis analytics + knowledge base activity |

---

## 3. Judging Criteria Alignment

### Technical Execution (30%)

- **Agent Builder**: Central orchestration layer with custom ES|QL tools + built-in search
- **Elasticsearch**: 4 indices with semantic search, vector embeddings, and full-text queries
- **MCP Protocol**: Bidirectional — Agent Builder connects to Artemis MCP server
- **Elastic Workflows**: Automated daily planning and note-watching
- **ES|QL**: Custom query tools for knowledge base operations
- **Code Quality**: Type-safe Python (Pydantic AI, FastAPI), existing Artemis test suite

### Potential Impact & Wow Factor (30%)

- **Real problem**: Everyone has notes that never become actions
- **Measurable**: "50 notes → 23 extracted tasks → 18 completed via Pomodoro"
- **Wow moment in demo**: Talk to the agent about a project idea → watch tasks appear in Artemis's Eisenhower Matrix in real-time
- **Novel**: No existing tool bridges Obsidian ↔ AI Agent ↔ Productivity System this way

### Demo (30%)

**Demo Script (~3 minutes):**

1. **(0:00-0:30) Problem Statement** — Show scattered Obsidian notes with buried action items. Show Artemis with an empty task board. "These two worlds don't talk to each other."

2. **(0:30-1:15) Knowledge Ingestion** — Show the Obsidian vault being indexed into Elasticsearch. Show semantic search working: "Find my notes about the API refactoring project."

3. **(1:15-2:15) The Agent in Action** — Chat with Athena: "I need to finish the API refactoring this week. What did I note about it?" → Agent searches knowledge base → finds relevant notes → "I found 3 related notes. I can identify 5 actionable tasks. Shall I create them?" → "Yes, prioritize them" → Agent creates tasks in Artemis with Eisenhower classification → Shows tasks appearing in Artemis dashboard in real-time

4. **(2:15-2:45) Daily Planning** — "Plan my day" → Agent checks existing tasks → suggests 1-3-5 plan based on priorities → assigns tasks → starts first Pomodoro

5. **(2:45-3:00) Architecture Slide** — Show Mermaid diagram. Highlight: Elasticsearch (search + storage), Agent Builder (reasoning + tools), MCP (Artemis bridge), Obsidian (source of truth). "Everything stays in your local vault. Elasticsearch powers the intelligence."

### Social (10%)

- Post progress updates on X tagging @elastic_devs and @elastic
- Share architectural diagram
- Post demo video link
- Mention the Obsidian → Elasticsearch → AI Agent pipeline (resonates with PKM community)

---

## 4. Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Agent** | Elastic Agent Builder | GA (Jan 2026) |
| **Search/Storage** | Elasticsearch Serverless | Latest |
| **Agent Framework** | Pydantic AI | Latest |
| **MCP Server** | FastAPI + `mcp` library | Latest |
| **Indexer** | Python + `elasticsearch[async]` | 9.3.0 |
| **Existing Backend** | Artemis (FastAPI + Supabase) | v0.6.0 |
| **Existing Frontend** | Artemis (React + Vite + TS) | v0.6.0 |
| **LLM Provider** | OpenAI (GPT-4o) or Anthropic (Claude) | Latest |
| **Automation** | Elastic Workflows | Tech Preview |
| **Embeddings** | Elasticsearch inference API (ELSER or e5) | Built-in |

### Python Dependencies (New)

```
elasticsearch[async]>=9.3.0
pydantic-ai[mcp]
mcp
fastapi
uvicorn
python-frontmatter      # Parse Obsidian YAML frontmatter
watchdog                 # File system watcher for vault sync
```

---

## 5. Implementation Plan — 17 Days

### Critical Path

```
Week 1 (Feb 11-16):  Infrastructure + Core Agent
Week 2 (Feb 17-23):  Integration + Features + Polish
Week 3 (Feb 24-27):  Demo + Documentation + Submit
```

> ⚠️ **Elastic Cloud Trial**: 14-day trial, no extensions. Sign up on **Feb 11** — expires Feb 25. This gives 2 days buffer before the deadline. The demo video should be recorded by Feb 24-25 while the trial is still active.

---

### WEEK 1: Foundation (Feb 11-16)

#### Day 1 (Feb 11): Elasticsearch Setup + Obsidian Indexer

**Morning — Elasticsearch:**
- [ ] Sign up for Elastic Cloud Serverless trial at cloud.elastic.co/registration
- [ ] Complete the "Your First Elastic Agent" tutorial end-to-end
- [ ] Verify Agent Builder is accessible in Kibana
- [ ] Configure an LLM connector (OpenAI or Anthropic)
- [ ] Test the built-in conversational agent

**Afternoon — Obsidian Indexer:**
- [ ] Create the `indexer/` Python project with `uv`
- [ ] Write the Obsidian vault parser (read .md files, parse YAML frontmatter, extract content)
- [ ] Create the `second-brain-notes` index mapping in Elasticsearch (with vector field)
- [ ] Implement bulk indexing of Markdown files into Elasticsearch
- [ ] Test: index a sample Obsidian vault (10-20 notes) and verify search works
- [ ] Set up ELSER or e5 model for embeddings via Elasticsearch inference API

**Deliverable:** Obsidian vault indexed and searchable in Elasticsearch.

#### Day 2 (Feb 12): Agent Builder — Custom Tools

**Morning — ES|QL Tools:**
- [ ] Create `search_knowledge_base` tool in Agent Builder (full-text + semantic search)
- [ ] Create `find_related_notes` tool (ES|QL query for related content)
- [ ] Create `store_idea` tool (index a new idea document)
- [ ] Create `list_projects` tool

**Afternoon — Test the Agent:**
- [ ] Configure Agent Builder system prompt for "Athena" persona
- [ ] Test conversational flow: ask about notes → agent searches → returns relevant context
- [ ] Test idea storage: tell agent an idea → it stores it in Elasticsearch
- [ ] Iterate on tool definitions and system prompt

**Deliverable:** Working Agent Builder agent that can search and write to the knowledge base.

#### Day 3 (Feb 13): Artemis MCP Server

**Morning — MCP Server Core:**
- [ ] Create `artemis-mcp/` project directory
- [ ] Implement MCP server using the `mcp` Python library + FastAPI
- [ ] Implement `create_task` tool (maps to `POST /tasks`)
- [ ] Implement `list_tasks` tool (maps to `GET /tasks`)
- [ ] Implement `complete_task` tool (maps to `POST /tasks/{id}/complete`)

**Afternoon — Plan & Timer Tools:**
- [ ] Implement `get_daily_plan` tool (maps to `GET /daily-plans/today`)
- [ ] Implement `assign_to_plan` tool (maps to `POST /daily-plans/{id}/assign`)
- [ ] Implement `get_analytics` tool (maps to `GET /analytics/summary`)
- [ ] Implement `start_pomodoro` tool (maps to `POST /pomodoro/sessions`)
- [ ] Test MCP server independently (curl / MCP inspector)
- [ ] Deploy MCP server alongside Artemis (Docker Compose update)

**Deliverable:** Artemis MCP server with all tools functional.

#### Day 4 (Feb 14): Connect Agent Builder ↔ Artemis MCP

**Morning — MCP Integration:**
- [ ] Register the Artemis MCP server in Agent Builder
- [ ] Test: ask agent to create a task → verify it appears in Artemis
- [ ] Test: ask agent to plan my day → verify 1-3-5 assignment in Artemis
- [ ] Test: ask agent to check analytics → verify it returns real data

**Afternoon — End-to-End Flow:**
- [ ] Test the complete flow: "I have notes about project X, extract tasks and plan my day"
- [ ] Agent searches knowledge base → finds notes → extracts tasks → creates in Artemis → assigns to plan
- [ ] Debug and fix any issues in the tool chain
- [ ] Refine the agent's system prompt for better task extraction and classification

**Deliverable:** End-to-end flow working: Knowledge Base → Agent → Artemis.

#### Day 5 (Feb 15): Task Extraction Intelligence

**Morning — Smart Extraction:**
- [ ] Build the task extraction logic: agent reads a note and identifies actionable items
- [ ] Implement Eisenhower classification: agent assigns urgency/importance based on context
- [ ] Implement 1-3-5 suggestion: agent recommends which slot a task fits
- [ ] Add pomodoro estimation: agent estimates effort (1-4 pomodoros) based on task complexity

**Afternoon — Brainstorming Mode:**
- [ ] Create "brainstorm" tool/workflow: user describes a project → agent breaks it down into tasks
- [ ] Agent stores the brainstorm session in `second-brain-conversations` index
- [ ] Agent can reference previous brainstorm sessions in future conversations
- [ ] Test with a real project brainstorm

**Deliverable:** Intelligent task extraction with priority classification.

#### Day 6 (Feb 16): Elastic Workflows + Buffer

**Morning — Workflows:**
- [ ] Set up `note_watcher` workflow: when new notes are indexed → scan for action items
- [ ] Set up `daily_planning_assistant` workflow (if time): suggest morning plan
- [ ] Test automated workflows end-to-end

**Afternoon — Buffer / Catch-up:**
- [ ] Address any issues from Days 1-5
- [ ] Improve agent system prompt based on testing
- [ ] Add error handling and edge cases
- [ ] Document architecture decisions

**Deliverable:** Automated workflows running. Week 1 complete.

---

### WEEK 2: Integration & Polish (Feb 17-23)

#### Day 7 (Feb 17): Frontend — Chat Interface in Artemis

- [ ] Add a chat panel/page to the Artemis frontend (new route: `/agent` or sidebar panel)
- [ ] Use the Agent Builder chat API or embed the Agent Builder chat widget
- [ ] Style with the Deep Cozy Luxury design system (GlassCard, luxury colors)
- [ ] Show real-time task creation: when agent creates a task, the dashboard updates

#### Day 8 (Feb 18): Frontend — Knowledge Base View

- [ ] Add a "Knowledge Base" page to Artemis (`/knowledge`)
- [ ] Show indexed notes from Elasticsearch with search
- [ ] Show extracted ideas and their status
- [ ] Link notes to related tasks in Artemis

#### Day 9 (Feb 19): Vault Sync & File Watcher

- [ ] Implement `watchdog`-based file watcher for Obsidian vault changes
- [ ] Auto-re-index when files are created, modified, or deleted
- [ ] Add a "Sync Status" indicator in the frontend
- [ ] Handle edge cases: large files, binary files, special characters

#### Day 10 (Feb 20): Advanced Agent Features

- [ ] Add context-aware task suggestions: "Based on your notes and current tasks, I suggest..."
- [ ] Add weekly review capability: agent summarizes the week's productivity
- [ ] Add project progress tracking: agent can tell you how a project is going based on related tasks
- [ ] Improve conversation memory within Agent Builder

#### Day 11 (Feb 21): Testing & Error Handling

- [ ] Test all agent tools with edge cases
- [ ] Add proper error messages when Artemis is unreachable
- [ ] Add proper error messages when Elasticsearch queries fail
- [ ] Test with a realistic Obsidian vault (50+ notes)
- [ ] Run Artemis's existing test suite to ensure no regressions

#### Day 12 (Feb 22): Architecture Diagram + Documentation

- [ ] Create a Mermaid architecture diagram for the demo
- [ ] Write the ~400 word project description for Devpost
- [ ] Prepare the GitHub README with setup instructions
- [ ] Add an OSI license (MIT) to the repository
- [ ] Document the Agent Builder configuration (system prompt, tools, workflows)

#### Day 13 (Feb 23): Demo Prep + Social Post

- [ ] Prepare demo dataset: create a realistic Obsidian vault with project notes
- [ ] Script the 3-minute demo flow (see Demo Script in Section 3)
- [ ] Do a practice run of the demo
- [ ] Post on X about the project, tagging @elastic_devs and @elastic
- [ ] Take screenshots for the Devpost submission

---

### WEEK 3: Final Sprint (Feb 24-27)

#### Day 14 (Feb 24): Record Demo Video

- [ ] Set up screen recording (OBS or similar)
- [ ] Record the ~3-minute demo following the script
- [ ] Edit if needed (trim dead time, add captions)
- [ ] Upload to YouTube (unlisted)

#### Day 15 (Feb 25): Final Polish

- [ ] Review and polish the GitHub repository
- [ ] Ensure Docker Compose brings up the entire stack
- [ ] Final code cleanup and documentation pass
- [ ] Verify the demo video is clear and compelling
- [ ] ⚠️ **Last day of Elastic Cloud trial** — ensure everything is captured

#### Day 16 (Feb 26): Submit to Devpost

- [ ] Write the final Devpost submission:
  - ~400 word description (problem, solution, features, challenges)
  - Link to demo video
  - Link to public GitHub repo
  - Link to social media post
  - Screenshots
  - Technologies used (tag: Elasticsearch, Agent Builder, MCP, Pydantic AI, FastAPI)
- [ ] Review submission against judging criteria
- [ ] Submit!

#### Day 17 (Feb 27): Buffer Day

- [ ] Address any last-minute issues
- [ ] Final submission edits if needed
- [ ] **Deadline: 1:00 PM EST / 20:00 Athens time**

---

## 6. Project Name: "Athena"

**Why Athena?**
- Greek goddess of wisdom and strategic warfare — fits the "second brain" + "strategic productivity" theme
- Companion to **Artemis** (your existing app) — both are Greek goddesses, creating a cohesive brand
- Symbolizes the bridge between knowledge (wisdom) and action (strategy)

**Tagline options:**
- "From scattered thoughts to focused action"
- "Your second brain meets your first priority"
- "Think in Obsidian. Act in Artemis. Athena bridges the gap."

---

## 7. Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Elastic trial expires before demo recorded | Medium | Critical | Sign up Feb 11, record demo by Feb 24 |
| MCP server integration issues with Agent Builder | Medium | High | Start MCP work Day 3, have 2 days buffer |
| Agent Builder limitations for custom workflows | Low | Medium | Fall back to Pydantic AI as orchestrator with Agent Builder as tool provider |
| Obsidian indexing performance | Low | Low | Limit to 100-200 notes for demo; add pagination |
| Demo video quality | Medium | High | Script and practice Day 13, record Day 14, buffer Day 15 |
| Frontend chat integration complexity | Medium | Medium | Fall back to Agent Builder's built-in chat UI + screenshots |

---

## 8. Repository Structure

```
athena/
├── README.md                    # Project overview + setup
├── LICENSE                      # MIT License
├── docker-compose.yml           # Full stack orchestration
├── .env.example                 # Environment template
│
├── indexer/                     # Obsidian → Elasticsearch sync
│   ├── pyproject.toml
│   ├── src/
│   │   ├── parser.py           # Markdown + frontmatter parsing
│   │   ├── indexer.py           # Elasticsearch bulk indexing
│   │   ├── watcher.py           # File system watcher
│   │   └── embeddings.py        # Vector embedding generation
│   └── tests/
│
├── artemis-mcp/                 # MCP Server for Artemis
│   ├── pyproject.toml
│   ├── src/
│   │   ├── server.py            # MCP server implementation
│   │   ├── tools.py             # Tool definitions
│   │   └── artemis_client.py    # HTTP client for Artemis API
│   └── tests/
│
├── agent-config/                # Agent Builder configuration
│   ├── system-prompt.md         # Agent persona and instructions
│   ├── tools/                   # ES|QL tool definitions
│   ├── workflows/               # Elastic Workflow definitions
│   └── setup-guide.md           # How to configure in Kibana
│
├── artemis/                     # Existing Artemis app (submodule or copy)
│   ├── backend/
│   └── frontend/
│
├── sample-vault/                # Demo Obsidian vault
│   ├── Projects/
│   ├── Ideas/
│   ├── Meeting Notes/
│   └── Daily Notes/
│
├── docs/
│   ├── architecture.md          # Detailed architecture
│   ├── architecture.mermaid     # Mermaid diagram
│   └── demo-script.md           # Demo walkthrough
│
└── devpost/
    ├── description.md           # ~400 word submission
    ├── screenshots/             # UI screenshots
    └── social-post.md           # X post draft
```

---

## 9. Key Resources

### Official Hackathon

- **Devpost**: https://elasticsearch.devpost.com/
- **Slack**: #hackathon-agent-builder on Elastic Stack Slack
- **Trial**: https://cloud.elastic.co/registration?cta=hackathon

### Agent Builder Documentation

- **Docs**: https://www.elastic.co/docs/explore-analyze/ai-features/elastic-agent-builder
- **Kibana API**: https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/kibana-api
- **MCP Server**: https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/mcp-server
- **A2A Server**: https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/a2a-server

### Tutorials & Examples

- **First Elastic Agent**: https://www.elastic.co/search-labs/blog/ai-agent-builder-elasticsearch
- **Augmented Infrastructure Example**: https://www.elastic.co/search-labs/blog/agent-builder-augmented-infrastructure
- **Voice Agent Example**: https://www.elastic.co/search-labs/blog/voice-agents-elastic-agent-builder
- **MCP Server Integration**: https://www.elastic.co/search-labs/blog/elastic-mcp-server-agent-builder-tools
- **Agentic Workflows**: https://www.elastic.co/search-labs/blog/ai-agentic-workflows-elastic-ai-agent-builder
- **FastAPI + Elasticsearch**: https://www.elastic.co/search-labs/blog/elasticsearch-fastapi

### Code Repositories

- **Elasticsearch Labs**: https://github.com/elastic/elasticsearch-labs
- **Elastic Workflows**: https://github.com/elastic/workflows/
- **Elasticsearch Python Client**: https://pypi.org/project/elasticsearch/
- **FastAPI Agents**: https://github.com/blairhudson/fastapi-agents

---

## 10. Submission Checklist

- [ ] ~400 word project description on Devpost
  - [ ] Problem solved
  - [ ] Features used (Agent Builder, ES|QL, MCP, Elastic Workflows, Search)
  - [ ] 2-3 features liked or challenges faced
- [ ] ~3 minute demo video uploaded (YouTube unlisted)
- [ ] Public GitHub repository with MIT license
- [ ] Social media post on X tagging @elastic_devs or @elastic (link included in submission)
- [ ] Architecture diagram (Mermaid) in repo and shown in demo
- [ ] Docker Compose for full stack deployment
- [ ] README with clear setup instructions

---

*Created: February 10, 2026*
*Let's build this. 🏛️*
