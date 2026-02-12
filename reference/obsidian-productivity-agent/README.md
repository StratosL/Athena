# Obsidian AI Productivity Agent

An AI agent for productivity designed specifically for Obsidian - based on the Dynamous AI Agent Mastery course agent. Includes RAG for knowledge management, automated video transcription, and a seamless vault integration since Obsidian vaults are just markdown. This agent turns your Obsidian vault into a dynamic knowledge base with advanced RAG capabilities, smart tagging, and multi-modal content processing.

## 🚀 Key Features

### Intelligent Knowledge Management
- **Advanced RAG System**: Query your entire Obsidian vault with context-aware AI that understands your notes' relationships and content
- **Smart Tag Navigation**: Automatically extracts and indexes Obsidian hashtags, enabling efficient document filtering and retrieval
- **Long-term Memory (Mem0)**: Agent remembers important information across conversations for personalized assistance

### Content Processing & Automation
- **Video Transcription Service**: Automatically transcribe video files dropped into a watch folder, with output formatted as Obsidian-compatible markdown
- **Multi-format Support**: Process MP4, MKV, AVI, MOV, and other video formats with Whisper-based transcription
- **Vault Integration**: Transcriptions and processed content automatically integrate with your RAG pipeline

### Obsidian-Native Integration
- **OpenAI API Compatibility**: Works with the "copilot" Obsidian plugin that supports using any OpenAI API compatible endpoint
- **Multi-LLM Support**: Choose between OpenAI, Anthropic (via OpenRouter), or local Ollama models in the agent

## 🎯 Perfect For

- **Knowledge Workers**: Transform meeting recordings into searchable notes instantly
- **Researchers**: Query across all your research notes and sources with AI assistance
- **Content Creators**: Convert video content into written documentation automatically
- **Students**: Build an AI-powered second brain that understands your entire knowledge base
- **Teams**: Share a centralized knowledge base with intelligent search and retrieval

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/ultimate-productivity-agent.git
cd ultimate-productivity-agent
cp .env.example .env

# 2. Configure your .env
# - Add your API keys
# - Set OBSIDIAN_VAULT_PATH to your vault location
# 3. Setup database (run SQL in Supabase)
# 4. Start everything
docker compose up -d --build

# 5. Connect Obsidian plugin
# API Endpoint: http://localhost:8001/v1/chat/completions
# API Key: Your OPENAI_COMPATIBLE_API_KEY from .env
```

## How It Works

### The Obsidian Workflow

1. **Your Vault as Knowledge Base**: Point the RAG pipeline to your Obsidian vault folder - all markdown files are automatically indexed
2. **Automatic Tag Extraction**: The system recognizes and indexes all `#hashtags` in your notes for intelligent filtering
3. **Video to Knowledge**: Drop video files into the watch folder → automatic transcription → formatted markdown in your vault
4. **AI-Powered Queries**: Ask questions through Obsidian plugins or the web interface, get answers based on your entire knowledge base

### System Architecture

```
ultimate-productivity-agent/
├── backend_agent_api/       # AI agent with Obsidian-compatible endpoints
├── backend_rag_pipeline/    # Vault indexing and document processing
├── video_processor/         # Video transcription service
├── frontend/               # Web interface (optional, for non-Obsidian access)
└── sql/                    # Database schemas for knowledge persistence
```

### Key Components

- **Agent API**: Provides OpenAI-compatible endpoints that Obsidian plugins can connect to
- **RAG Pipeline**: Continuously watches your vault, indexes new notes, and maintains vector embeddings
- **Video Processor**: Uses Whisper AI to transcribe videos into markdown format
- **Tag System**: Extracts and indexes Obsidian hashtags for document organization and retrieval

## Prerequisites

- Docker/Docker Desktop (recommended) OR Python 3.11+ and Node.js 18+ with npm
- Supabase account (or self-hosted instance)
- LLM provider account (OpenAI, OpenRouter, or local Ollama)
- Optional: Brave API key for web search (or local SearXNG)
- Optional: Google Drive API credentials for Google Drive RAG

## Database Setup

The database is the foundation for all components. Set it up first:

1. **Create a Supabase project:**
   - **Cloud**: Create a project at [https://supabase.com](https://supabase.com)
   - **Local**: Navigate to http://localhost:8000 (default Supabase dashboard)

2. **Navigate to the SQL Editor** in your Supabase dashboard

3. **Run the complete database setup:**
   ```sql
   -- Copy and paste the contents of sql/0-all-tables.sql
   -- This creates all tables, functions, triggers, and security policies
   ```
   
   **⚠️ Important**: The `0-all-tables.sql` script will DROP and recreate the agent tables (user_profiles, conversations, messages, documents, etc.). This resets the agent data to a blank slate - existing agent data will be lost, but other tables in your Supabase project remain untouched.

**Alternative**: You can run the individual scripts (`1-user_profiles_requests.sql` through `9-rag_pipeline_state.sql`) if you prefer granular control.

**Ollama Configuration**: For local Ollama implementations using models like nomic-embed-text, modify the vector dimensions from 1536 to 768 in `0-all-tables.sql` (lines 133 and 149).

## Deployment Methods

### Method 1: Development Mode (Manual Components)

For development without Docker or to run individual containers separately, see the component-specific READMEs:

- [Backend Agent API](./backend_agent_api/README.md) - Python agent with FastAPI
- [Backend RAG Pipeline](./backend_rag_pipeline/README.md) - Document processing pipeline  
- [Frontend](./frontend/README.md) - React application

### Method 2: Smart Deployment Script (Recommended)

The easiest way to deploy the stack is using the included Python deployment script, which automatically handles both local and cloud deployment scenarios.

#### Configure Environment Variables

First, configure your environment variables:

```bash
# Copy the example environment file
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Obsidian Integration (REQUIRED)
OPENAI_COMPATIBLE_API_KEY=sk-your-custom-api-key-here  # Use this key in Obsidian plugins

# LLM Configuration
LLM_PROVIDER=openai
LLM_API_KEY=your_openai_api_key_here
LLM_CHOICE=gpt-4o-mini

# Embedding Configuration
EMBEDDING_API_KEY=your_openai_api_key_here
EMBEDDING_MODEL_CHOICE=text-embedding-3-small

# Database Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_supabase_service_key_here

# Frontend Configuration (Optional - for web interface)
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key_here
VITE_AGENT_ENDPOINT=http://localhost:8001/api/pydantic-agent

# Obsidian Vault Configuration
OBSIDIAN_VAULT_PATH=./obsidian-vault  # Path to your Obsidian vault on the host
RAG_PIPELINE_TYPE=local              # Use 'local' for Obsidian vaults
RUN_MODE=continuous                  # Continuously watch for changes

# Video Processing Configuration
VIDEO_WATCH_DIR=./video-input      # Drop videos here for transcription
VIDEO_OUTPUT_DIR=./obsidian-vault  # Transcriptions output to your vault

# Optional: Google Drive Integration
GOOGLE_DRIVE_CREDENTIALS_JSON=  # For syncing with Google Drive
RAG_WATCH_FOLDER_ID=            # Specific Google Drive folder ID

# Optional Langfuse agent monitoring configuration
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=https://cloud.langfuse.com

# Hostnames for Caddy reverse proxy routes
# Leave these commented if you aren't deploying to production
AGENT_API_HOSTNAME=agent.yourdomain.com
FRONTEND_HOSTNAME=chat.yourdomain.com
```

#### Deploy with Script

##### Cloud Deployment (Standalone with Caddy)
Deploy as a self-contained stack with built-in reverse proxy:

```bash
# Deploy to cloud (includes Caddy reverse proxy)
python deploy.py --type cloud

# Stop cloud deployment
python deploy.py --down --type cloud
```

##### Local Deployment (Integrate with the Local AI Package)
Deploy to work alongside your existing Local AI Package with shared Caddy:

```bash
# Deploy alongside the Local AI Package (uses existing Caddy)
python deploy.py --type local --project localai

# Stop local deployment
python deploy.py --down --type local --project localai
```

**To enable reverse proxy routes in your Local AI Package**:

1. **Copy and configure** the addon file:
   ```bash
   # Copy caddy-addon.conf to your Local AI Package's caddy-addon folder
   cp caddy-addon.conf /path/to/local-ai-package/caddy-addon/
   
   # Edit lines 2 and 21 to set your desired subdomains:
   # Line 2: subdomain.yourdomain.com (for agent API)
   # Line 21: subdomain2.yourdomain.com (for frontend)
   ```

2. **Restart Caddy in the Local AI Package** to load the new configuration:
   ```bash
   docker compose -p localai restart caddy
   ```


### Connect Your Obsidian Vault

Set your vault path in the `.env` file:
```bash
# Set the path to your existing Obsidian vault
OBSIDIAN_VAULT_PATH=/path/to/your/ObsidianVault

# For video transcriptions, drop videos into the watch folder
cp your-video.mp4 ./video-input/
# Transcriptions will appear in your vault as markdown files
```

## 🔮 Obsidian Integration

### Quick Setup

1. **Connect Your Vault**: Set `OBSIDIAN_VAULT_PATH` in your `.env` file to point to your Obsidian vault

2. **Install an OpenAI-compatible plugin** in Obsidian - Copilot:

3. **Configure the plugin:**
   - **API Endpoint**: `http://localhost:8001/v1/chat/completions`
   - **API Key**: Your `OPENAI_COMPATIBLE_API_KEY` from `.env`

4. **Start Using AI Features:**
   - Query your entire vault through the agent
   - Use hashtags to filter responses (e.g., "What are my notes about #project-alpha?")
   - Process videos and have transcriptions automatically appear in your vault

### Advanced Features

#### Tag-Based Document Filtering
The agent automatically recognizes Obsidian hashtags in your notes:
- Query specific topics: "Summarize all notes tagged with #meeting-notes"
- List available tags: "What tags do I use in my vault?"
- Cross-reference tags: "Find connections between #python and #machine-learning"

#### Video to Vault Pipeline
1. Drop video files into `./video-input/`
2. Whisper AI transcribes the content
3. Formatted markdown appears in your vault
4. RAG pipeline automatically indexes the new content
5. Query the transcription through Obsidian immediately


#### Docker Compose Management Commands

**For Cloud Deployment:**
```bash
# View logs for specific service
docker compose -p dynamous-agent logs -f agent-api
docker compose -p dynamous-agent logs -f rag-pipeline
docker compose -p dynamous-agent logs -f video-processor
docker compose -p dynamous-agent logs -f frontend
docker compose -p dynamous-agent logs -f caddy

# Rebuild specific service
docker compose -p dynamous-agent build agent-api
docker compose -p dynamous-agent up -d agent-api

# Check service health
docker compose -p dynamous-agent ps
```

**For Local Deployment:**
```bash
# View logs for specific service
docker compose -p localai logs -f agent-api
docker compose -p localai logs -f rag-pipeline
docker compose -p localai logs -f video-processor
docker compose -p localai logs -f frontend

# Rebuild specific service
docker compose -p localai build agent-api
docker compose -p localai up -d agent-api

# Check service health
docker compose -p localai ps
```

**For Base Services Only:**
```bash
# View logs for specific service
docker compose -p dynamous-agent logs -f agent-api
docker compose -p dynamous-agent logs -f rag-pipeline
docker compose -p dynamous-agent logs -f video-processor
docker compose -p dynamous-agent logs -f frontend

# Rebuild and restart services
docker compose up -d --build

# Scale RAG pipeline (if using single-run mode)
docker compose up -d --scale rag-pipeline=0  # Stop for scheduled runs

# Check service health
docker compose ps
```

## Development Mode

For development with live reloading, run each component separately. You'll need 4-5 terminal windows:

### Quick Setup for Each Component

1. **Terminal 1 - Agent API:**
   ```bash
   cd backend_agent_api
   python -m venv venv
   venv\Scripts\activate  # or source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env  # Then edit with your config
   uvicorn agent_api:app --reload --port 8001
   ```

2. **Terminal 2 - RAG Pipeline (Obsidian Vault Watcher):**
   ```bash
   cd backend_rag_pipeline
   python -m venv venv
   venv\Scripts\activate  # or source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env  # Then edit with your config
   python docker_entrypoint.py --pipeline local --mode continuous
   ```

3. **Terminal 3 - Video Processor:**
   ```bash
   cd video_processor
   python -m venv venv
   venv\Scripts\activate  # or source venv/bin/activate
   pip install -r requirements.txt
   WATCH_DIR=./video-input OUTPUT_DIR=./obsidian-vault python watcher.py
   ```

4. **Terminal 4 - Frontend (Optional):**
   ```bash
   cd frontend
   npm install
   cp .env.example .env  # Then edit with your config
   npm run dev
   ```

**Note:** Don't forget to run the SQL scripts first (see Database Setup above) and configure each `.env` file with your credentials.

## Deployment Options

We provide three deployment strategies, from simple to enterprise-grade:

### Option 1: DigitalOcean with Docker Compose (Simplest)
Deploy the entire stack on a single DigitalOcean Droplet using Docker Compose:
- **Pros**: Simple setup, everything in one place, easy to manage
- **Cons**: All components scale together, single point of failure
- **Best for**: Small teams, prototypes, and getting started quickly
- **Setup**: Use the provided `docker compose.yml` to deploy all services together

### Option 2: Render Platform (Recommended)
Deploy each component separately on Render for better scalability:
- **Agent API**: Deploy as a Docker container with autoscaling
- **RAG Pipeline**: Set up as a scheduled job (cron)
- **Frontend**: Deploy as a static site from the build output
- **Pros**: Automatic scaling, managed infrastructure, good free tier
- **Cons**: Requires configuring each service separately
- **Best for**: Production applications with moderate traffic

### Option 3: Google Cloud Platform (Enterprise)
For enterprise deployments with maximum flexibility:
- **Agent API**: Cloud Run for serverless, auto-scaling containers
- **RAG Pipeline**: Cloud Scheduler + Cloud Run for scheduled processing
- **Frontend**: Cloud Storage + Cloud CDN for global static hosting
- **Database**: Consider Cloud SQL for Postgres instead of Supabase
- **Pros**: Enterprise features, global scale, fine-grained control
- **Cons**: More complex setup, requires GCP knowledge
- **Best for**: Large-scale production deployments

### Deployment Decision Matrix

| Feature | DigitalOcean | Render | Google Cloud |
|---------|--------------|---------|--------------|
| Setup Complexity | ⭐ (Easiest) | ⭐⭐ (Still Pretty Easy) | ⭐⭐⭐ (Moderate) |
| Cost for Small Apps | $$ | $ (Free tier) | $ (Free tier) |
| Scalability | Manual | Automatic | Automatic |
| Geographic Distribution | Single region | Multi-region | Global |
| Best For | Quick start or Local AI | Most cloud based projects | Enterprise |

## Environment Variables Reference

### Core Configuration
```env
# Obsidian Integration
OPENAI_COMPATIBLE_API_KEY=sk-your-key   # API key for Obsidian plugins

# LLM Configuration
LLM_PROVIDER=openai
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your_api_key
LLM_CHOICE=gpt-4o-mini
VISION_LLM_CHOICE=gpt-4o-mini

# Embedding Configuration
EMBEDDING_PROVIDER=openai
EMBEDDING_BASE_URL=https://api.openai.com/v1
EMBEDDING_API_KEY=your_api_key
EMBEDDING_MODEL_CHOICE=text-embedding-3-small

# Database
DATABASE_URL=postgresql://user:pass@host:port/db
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_key
```

### Obsidian Vault & RAG Configuration
```env
# Obsidian Vault Path
OBSIDIAN_VAULT_PATH=/path/to/vault  # Your Obsidian vault location

# RAG Pipeline Configuration
RAG_PIPELINE_TYPE=local          # Use 'local' for Obsidian vaults
RUN_MODE=continuous              # Watch vault for changes
RAG_PIPELINE_ID=obsidian-vault   # Pipeline identifier

# Video Processing
VIDEO_WATCH_DIR=./video-input    # Drop videos here
VIDEO_OUTPUT_DIR=./obsidian-vault # Transcriptions go to vault
WHISPER_MODEL=base.en            # Whisper model size (tiny, base, small, medium, large)

# Optional: Google Drive Sync
GOOGLE_DRIVE_CREDENTIALS_JSON=   # Service account JSON
RAG_WATCH_FOLDER_ID=            # Google Drive folder ID
```

### Frontend
```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_anon_key
VITE_AGENT_ENDPOINT=http://localhost:8001/api/pydantic-agent
VITE_ENABLE_STREAMING=true

# Optional: LangFuse integration for admin dashboard
VITE_LANGFUSE_HOST_WITH_PROJECT=http://localhost:3000/project/your-project-id

# Reverse Proxy Configuration (for Caddy deployments)
AGENT_API_HOSTNAME=agent.yourdomain.com
FRONTEND_HOSTNAME=chat.yourdomain.com
```

## Agent Observability with LangFuse (Optional)

This deployment includes optional LangFuse integration for comprehensive agent observability. LangFuse provides detailed insights into agent conversations, performance metrics, and debugging capabilities - particularly valuable for production deployments.

### What LangFuse Provides
- **Conversation Tracking**: Complete agent interaction histories with user and session context
- **Performance Metrics**: Response times, token usage, and cost tracking
- **Debugging Tools**: Detailed execution traces for troubleshooting agent behavior
- **User Analytics**: Insights into user patterns and agent effectiveness

### Setup (Completely Optional)

**To enable LangFuse observability:**

1. **Create a LangFuse account** at [https://cloud.langfuse.com/](https://cloud.langfuse.com/) (free tier available)

2. **Create a new project** and obtain your credentials

3. **Add LangFuse environment variables** to your agent API `.env` file:
   ```env
   # Agent observability (optional - leave empty to disable)
   LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
   LANGFUSE_SECRET_KEY=your_langfuse_secret_key
   LANGFUSE_HOST=https://cloud.langfuse.com
   ```

4. **Optional: Enable frontend integration** by setting in your frontend `.env`:
   ```env
   # Add clickable LangFuse links in the admin dashboard
   VITE_LANGFUSE_HOST_WITH_PROJECT=https://cloud.langfuse.com/project/your-project-id
   ```

**To disable LangFuse (default behavior):**
- Simply leave the `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` empty
- The agent runs normally with no observability overhead

### Benefits for Different Use Cases

- **Development**: Debug agent behavior and optimize conversation flows
- **Production**: Monitor performance, track usage costs, and identify issues
- **Analytics**: Understand user interactions and improve agent effectiveness
- **Team Collaboration**: Share conversation traces and debugging information

The LangFuse integration is designed to be zero-impact when disabled, making it perfect for development environments where observability isn't needed.

## Troubleshooting

### Docker Compose Issues

1. **Services won't start**:
   ```bash
   # Check service logs
   docker compose logs -f
   
   # Rebuild images
   docker compose build --no-cache
   ```

2. **Port conflicts**:
   ```bash
   # Check what's using ports
   netstat -tlnp | grep :8001
   
   # Stop conflicting services or change ports in docker compose.yml
   ```

3. **Environment variables not loading**:
   ```bash
   # Verify .env file exists and has correct format
   cat .env
   
   # Check environment in container
   docker compose exec agent-api env | grep LLM_
   ```

### Common Issues

1. **Database connection**: Verify Supabase credentials and network access
2. **Vector dimensions**: Ensure embedding model dimensions match database schema
3. **CORS errors**: Check API endpoint configuration in frontend `.env`
4. **Memory issues**: Increase Docker memory limits for large models

### Verification Steps

1. **Database**: Check Supabase dashboard for table creation
2. **Agent API Health**: Visit http://localhost:8001/health
3. **API Documentation**: Visit http://localhost:8001/docs
4. **RAG Pipeline**: Check logs with `docker compose logs rag-pipeline`
5. **Frontend**: Open browser console for any errors

### Health Checks

Monitor service health:
```bash
# Check all service health
docker compose ps

# Check specific service logs
docker compose logs -f agent-api

# Test API health endpoint
curl http://localhost:8001/health

# Test frontend
curl http://localhost:8082/health
```

## Testing

### Frontend Testing with Playwright

The frontend includes Playwright tests for end-to-end testing with mocked Supabase and agent API calls.

```bash
cd frontend

# Make sure Playwright is installed
npx playwright install --with-deps

# Run all tests
npm run test

# Run tests with interactive UI
npm run test:ui

# Run tests in headed browser mode (see the browser)
npm run test:headed

# Run specific test file
npx playwright test auth.spec.ts

# Debug tests
npx playwright test --debug
```

**Test Features:**
- ✅ **Complete mocking** - No database or API calls
- ✅ **Authentication flow** - Login, signup, logout
- ✅ **Chat interface** - Send messages, receive responses
- ✅ **Conversation management** - New chats, conversation history
- ✅ **Loading states** - UI feedback during operations

The tests use comprehensive mocks for:
- Supabase authentication and database
- Agent API streaming responses
- User sessions and conversation data

## Support

For detailed instructions on each component, refer to their individual README files:
- `backend_agent_api/README.md` - Agent API specifics
- `backend_rag_pipeline/README.md` - RAG pipeline details  
- `frontend/README.md` - Frontend development guide

Remember: The modular structure allows you to start with local deployment and gradually move components to the cloud as needed!