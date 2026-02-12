# Ultimate Productivity Agent - Backend API

A powerful AI agent backend designed for Obsidian and productivity workflows, featuring OpenAI-compatible API endpoints, advanced RAG capabilities, long-term memory, and comprehensive tool integration.

## 🎯 Key Features

### Core Capabilities
- **OpenAI-Compatible API**: Connect directly from Obsidian or any OpenAI client
- **Advanced RAG System**: Query your documents with context-aware intelligence
- **Long-term Memory (Mem0)**: Agent remembers important information across conversations
- **Multi-Tool Integration**: Web search, image analysis, code execution, and more
- **User-based Memory Isolation**: Separate memory spaces for different users/vaults
- **Real-time Streaming**: Stream AI responses with SSE (Server-Sent Events)
- **Multi-LLM Support**: Works with OpenAI, Anthropic (via OpenRouter), or local Ollama models

### Obsidian Integration
- **Native Obsidian Support**: Works seamlessly with Obsidian's AI assistant plugins
- **Vault-specific Memory**: Each Obsidian vault can have its own memory space
- **Document Processing**: Analyze and query your Obsidian notes
- **Markdown Support**: Full markdown compatibility for responses

## 📁 Project Structure

```
backend_agent_api/
├── agent_api.py                    # Main FastAPI application with endpoints
├── openai_api_compatibility.py     # OpenAI-compatible API implementation
├── agent.py                        # PydanticAI agent with tool definitions
├── clients.py                      # Client configurations (LLM, DB, Mem0)
├── db_utils.py                     # Database utility functions
├── tools.py                        # Agent tool implementations
├── prompt.py                       # System prompt configuration
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variable template
├── Dockerfile                      # Docker container configuration
├── tests/
│   ├── test_openai_endpoints.py   # OpenAI API compatibility tests
│   ├── test_clients.py            # Client configuration tests
│   └── test_tools.py              # Tool functionality tests
└── README.md                       # This file
```

## 🚀 Quick Start

### Prerequisites

- **Docker** (recommended) or **Python 3.11+**
- **PostgreSQL database** (for Mem0 long-term memory)
- **Supabase project** (for RAG and conversation storage)
- **LLM API access** (OpenAI, OpenRouter, or local Ollama)

### Option 1: Docker Setup (Recommended)

1. **Clone and navigate to the backend directory:**
   ```bash
   git clone <repository-url>
   cd ultimate-productivity-agent/backend_agent_api
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Build and run with Docker:**
   ```bash
   docker build -t productivity-agent .

   docker run -d \
     --name productivity-agent \
     -p 8001:8001 \
     --env-file .env \
     productivity-agent
   ```

4. **Verify the API is running:**
   ```bash
   curl http://localhost:8001/health
   ```

### Option 2: Local Development Setup

1. **Create and activate virtual environment:**
   ```bash
   python -m venv venv

   # Windows:
   venv\Scripts\activate

   # macOS/Linux:
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   **Note:** Add `tiktoken` to requirements.txt for OpenAI token counting:
   ```
   tiktoken==0.7.0
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the API:**
   ```bash
   uvicorn agent_api:app --reload --port 8001
   ```

## 🔧 Configuration

### Essential Environment Variables

```bash
# Environment mode
ENVIRONMENT=development  # or production

# LLM Configuration
LLM_PROVIDER=openai  # openai, openrouter, or ollama
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your_openai_api_key
LLM_CHOICE=gpt-4o-mini  # Model for agent responses
VISION_LLM_CHOICE=gpt-4o-mini  # Model for image analysis

# OpenAI-Compatible API Authentication
OPENAI_COMPATIBLE_API_KEY=sk-your-custom-api-key  # Required for Obsidian

# Embedding Configuration (for RAG)
EMBEDDING_PROVIDER=openai
EMBEDDING_BASE_URL=https://api.openai.com/v1
EMBEDDING_API_KEY=your_openai_api_key
EMBEDDING_MODEL_CHOICE=text-embedding-3-small

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/productivity_db
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_supabase_service_key

# Web Search (optional)
BRAVE_API_KEY=your_brave_api_key  # Or use SEARXNG_BASE_URL

# Observability (optional)
LANGFUSE_PUBLIC_KEY=  # Leave empty to disable
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=https://cloud.langfuse.com
```

## 🔌 API Endpoints

### OpenAI-Compatible Endpoints (NEW)

#### POST `/v1/chat/completions`
OpenAI-compatible chat endpoint for Obsidian and other clients.

**Request:**
```json
{
  "model": "gpt-3.5-turbo",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Help me organize my notes"}
  ],
  "stream": true,
  "user": "obsidian-vault-main",  // For memory isolation
  "max_tokens": 1000,
  "temperature": 0.7
}
```

**Headers:**
```
Authorization: Bearer sk-your-custom-api-key
Content-Type: application/json
```

#### POST `/v1/completions`
Legacy completion endpoint for backward compatibility.

**Request:**
```json
{
  "model": "gpt-3.5-turbo-instruct",
  "prompt": "Complete this thought:",
  "max_tokens": 100,
  "stream": false,
  "user": "obsidian-vault-main"
}
```

### Original Agent Endpoint

#### POST `/api/pydantic-agent`
Original streaming endpoint with Supabase authentication.

## 🔮 Obsidian Integration

### Setting up in Obsidian

1. **Install an OpenAI-compatible plugin** in Obsidian (e.g., Text Generator, Smart Connections)

2. **Configure the plugin:**
   - **API Endpoint**: `http://localhost:8001/v1/chat/completions`
   - **API Key**: Your `OPENAI_COMPATIBLE_API_KEY` from `.env`
   - **Model**: Any value (ignored, uses `LLM_CHOICE` from environment)

3. **User Isolation for Vaults:**
   - Set a unique user ID for each vault (e.g., `obsidian-vault-main`, `obsidian-vault-work`)
   - This ensures memory isolation between different vaults

### Example Obsidian Configuration

```yaml
# In your Obsidian plugin settings:
api_endpoint: http://localhost:8001/v1/chat/completions
api_key: sk-your-custom-api-key
model: gpt-3.5-turbo
user_identifier: obsidian-vault-main
stream: true
max_tokens: 2000
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_openai_endpoints.py -v

# Run with coverage
pytest --cov=. --cov-report=html
```

### Test OpenAI Compatibility
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="sk-your-custom-api-key"
)

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "Hello!"}
    ],
    stream=True,
    user="test-user"
)

for chunk in response:
    print(chunk.choices[0].delta.content, end="")
```

## 🧠 Memory Management

The agent uses Mem0 for long-term memory with user-based isolation:

- **User Identification**: Pass a unique `user` field in requests
- **Memory Retrieval**: Automatic context retrieval based on conversation
- **Memory Storage**: Important information automatically saved
- **Isolation**: Each user ID has completely separate memory space

### Memory Best Practices

1. **For Obsidian**: Use vault name as user ID (e.g., `obsidian-personal`, `obsidian-work`)
2. **For Teams**: Use email or username as user ID
3. **For Applications**: Use application instance ID

## 🛠️ Agent Tools

The agent has access to powerful tools:

- **Web Search**: Search the internet via Brave API or SearXNG
- **RAG Search**: Query your document database
- **Image Analysis**: Analyze images with vision models
- **Code Execution**: Execute Python code safely (requires MCP server)
- **SQL Queries**: Run analytical queries on your data
- **File Operations**: Read and analyze various file formats

## 🐳 Docker Management

```bash
# View logs
docker logs -f productivity-agent

# Stop the container
docker stop productivity-agent

# Restart the container
docker restart productivity-agent

# Update and rebuild
docker stop productivity-agent
docker rm productivity-agent
docker build -t productivity-agent .
docker run -d --name productivity-agent -p 8001:8001 --env-file .env productivity-agent
```

## 📊 Database Setup

### Create Required Tables

Run these SQL scripts in your Supabase SQL editor:

1. **User tables**: `sql/1-user_profiles_requests.sql`
2. **Conversation tables**: `sql/3-conversations_messages.sql`
3. **Document tables**: `sql/5-documents.sql`
4. **Metadata tables**: `sql/6-document_metadata.sql`
5. **RPC functions**: `sql/8-execute_sql_rpc.sql`

### Vector Dimensions

- **OpenAI embeddings**: 1536 dimensions (default)
- **Ollama nomic-embed-text**: 768 dimensions
- Adjust the vector column size in SQL scripts to match your embedding model

## 🚨 Troubleshooting

### Common Issues

1. **"Invalid API key" error**
   - Ensure `OPENAI_COMPATIBLE_API_KEY` matches in both `.env` and client

2. **Memory not persisting**
   - Check `DATABASE_URL` is correctly configured
   - Verify PostgreSQL is running and accessible
   - Ensure `user` field is provided in requests

3. **Streaming not working**
   - Some clients don't support SSE streaming
   - Try setting `stream: false` in requests

4. **Token counting errors**
   - Install tiktoken: `pip install tiktoken`
   - Restart the API after installation

5. **Database connection failed**
   - Verify PostgreSQL is running
   - Check credentials in `DATABASE_URL`
   - Ensure database exists

## 📈 Performance Optimization

- **Use streaming**: Better user experience for long responses
- **Configure memory limits**: Adjust Mem0 retrieval limits based on needs
- **Optimize embeddings**: Use smaller models for faster processing
- **Cache frequently accessed data**: Implement caching for common queries

## 🔒 Security Considerations

- **API Key**: Always use strong, unique API keys in production
- **HTTPS**: Use reverse proxy with SSL in production
- **Rate Limiting**: Consider implementing rate limits
- **Input Validation**: The API validates all inputs automatically
- **Memory Isolation**: User-based isolation prevents data leakage

## 📝 License

[Your License Here]

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## 💬 Support

- **Issues**: [GitHub Issues](your-repo-url/issues)
- **Discussions**: [GitHub Discussions](your-repo-url/discussions)
- **Documentation**: [Full Docs](your-docs-url)

---

Built with ❤️ for the Obsidian community and productivity enthusiasts.