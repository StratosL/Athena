# Agent Builder Setup Guide

Complete step-by-step instructions for configuring Athena in Elastic Agent Builder (Kibana).

## Prerequisites

- Elastic Cloud Serverless account with active trial
- `athena-notes` and `athena-conversations` indices created and populated (run the indexer first)
- MCP server running (locally or deployed) with a public URL (e.g., via ngrok)
- Artemis backend running on port 8000

## Step 1: Configure LLM Connector

1. Go to **Kibana → Stack Management → Connectors**
2. Click **Create Connector → OpenAI** (or Anthropic)
3. Set the API key and model (recommended: GPT-4o or Claude Sonnet 4)
4. Test the connection to verify it works

## Step 2: Create ES|QL Tools

For each JSON file in `agent-config/tools/` with `"type": "esql"`:

### Option A: Via Kibana UI

1. Go to **Agent Builder → Tools → New Tool**
2. Select type: **ES|QL**
3. Fill in the fields from the JSON file:
   - **ID**: the `id` field (e.g., `notes.search_notes`)
   - **Description**: the `description` field
   - **Tags**: the `tags` array
   - **Query**: the `configuration.query` field
   - **Parameters**: the `configuration.params` object
4. Save the tool
5. Repeat for all 5 ES|QL tool files:
   - `search-notes.json`
   - `get-recent-notes.json`
   - `get-notes-by-tag.json`
   - `count-notes-by-tag.json`
   - `get-conversation-history.json`

### Option B: Via API

```bash
# For each tool JSON file:
curl -X POST "https://<your-kibana-url>/api/agent_builder/tools" \
  -H "Authorization: ApiKey <your-api-key>" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d @agent-config/tools/search-notes.json
```

Repeat for each JSON file.

## Step 3: Create Index Search Tool

For `agent-config/tools/notes-semantic-search.json` (type: `index_search`):

### Option A: Via Kibana UI

1. Go to **Agent Builder → Tools → New Tool**
2. Select type: **Index Search**
3. Fill in:
   - **ID**: `notes.semantic_search`
   - **Description**: from the JSON file
   - **Index pattern**: `athena-notes`
   - **Row limit**: `10`
   - **Custom instructions**: from the JSON file
4. Save

### Option B: Via API

```bash
curl -X POST "https://<your-kibana-url>/api/agent_builder/tools" \
  -H "Authorization: ApiKey <your-api-key>" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d @agent-config/tools/notes-semantic-search.json
```

## Step 4: Register MCP Server

1. Go to **Kibana → Stack Management → Connectors → Create Connector → MCP**
2. Set **Server URL** to your MCP server endpoint (e.g., `https://your-ngrok-url.ngrok.io`)
3. Test the connection — it should discover 13 tools
4. Go to **Agent Builder → Tools → New Tool → MCP**
5. Select the MCP connector you just created
6. Import all tools with namespace prefix `athena`
7. This creates tools named: `athena.vault_query`, `athena.vault_read`, `athena.vault_manage`, `athena.artemis_create_task`, etc.

## Step 5: Create the Athena Agent

1. Go to **Agent Builder → Agents → Create Agent**
2. Fill in:
   - **Name**: `Athena`
   - **Description**: `Second brain orchestrator — bridges your Obsidian vault with Artemis productivity`
3. **System prompt**: Copy the full contents of `agent-config/system-prompt.md`
4. **Add all tools**:
   - ES|QL tools: `notes.search_notes`, `notes.get_recent_notes`, `notes.get_notes_by_tag`, `notes.count_notes_by_tag`, `conversations.get_history`
   - Index search: `notes.semantic_search`
   - MCP tools (athena.*): `vault_query`, `vault_read`, `vault_manage`, `artemis_create_task`, `artemis_list_tasks`, `artemis_complete_task`, `artemis_get_daily_plan`, `artemis_assign_to_plan`, `artemis_get_analytics`, `artemis_start_pomodoro`, `save_conversation_summary`, `web_search`, `fetch_url`
5. Save the agent

## Step 6: Verify End-to-End

Test these queries in the Agent Builder chat:

1. **Knowledge search**: "What are my notes about the API refactoring?"
   - Expected: Returns search results from `search_notes` ES|QL tool
2. **Direct reading**: "Read my daily note for today"
   - Expected: Returns full note content via `vault_read`
3. **Task extraction**: "Extract tasks from the API Refactoring note"
   - Expected: Lists action items with Eisenhower classification, waits for confirmation
4. **Daily planning**: "Plan my day"
   - Expected: Proposes 1-3-5 assignment from pending tasks
5. **Productivity check**: "How was my week?"
   - Expected: Returns analytics narrative from Artemis

## Troubleshooting

| Problem | Solution |
|---------|----------|
| MCP connection timeout | Check ngrok is running and the server is healthy (`/health` endpoint) |
| ES|QL query errors | Verify the index exists and has data: `GET athena-notes/_count` in Dev Tools |
| No search results | Re-run the indexer to ensure notes are indexed |
| Agent ignores tools | Check tool IDs match what's registered; verify tools are added to the agent |
| ELSER not working | Verify `.elser-2-elastic` inference endpoint is deployed in your Elastic Cloud project |
| Artemis tools fail | Check Artemis is running on port 8000 and MCP server can reach it |
