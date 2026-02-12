# Feature Request: OpenAI API Compatible Endpoints

## Feature Overview
Add OpenAI API compatible endpoints to the existing agent_api.py to enable integration with OpenAI-compatible clients, particularly the Obsidian AI plugin. This will allow users to connect their AI agent to Obsidian vaults and other OpenAI-compatible applications.

## Motivation
- Enable Obsidian AI plugin integration for knowledge management workflows
- Support any OpenAI-compatible client applications
- Provide a standard API interface while maintaining all agent capabilities (RAG, web search, image analysis, etc.)
- Allow stateless operation without requiring Supabase authentication or conversation storage

## Technical Requirements

### 1. New Endpoints
Implement two OpenAI-standard endpoints:
- `POST /v1/chat/completions` - Chat completion endpoint (primary)
- `POST /v1/completions` - Text completion endpoint (legacy support)

Both endpoints should support:
- Streaming responses (SSE format per OpenAI spec)
- Non-streaming responses
- Standard OpenAI request/response models

### 2. Authentication
- Add simple API key authentication via `Authorization: Bearer <api-key>` header
- Use a new environment variable `OPENAI_API_KEY` for validation
- No Supabase authentication required (stateless operation)

### 3. Message Format Conversion
Create utilities to convert between:
- OpenAI message format: `{role: "user|assistant|system", content: "..."}`
- Pydantic AI message format: `ModelRequest`, `ModelResponse`, `UserPromptPart`, etc.

### 4. Agent Dependencies
Reuse existing agent with simplified dependencies:
```python
agent_deps = AgentDeps(
    embedding_client=embedding_client,
    supabase=supabase,  # Still needed for RAG tool
    http_client=http_client,
    brave_api_key=os.getenv("BRAVE_API_KEY", ""),
    searxng_base_url=os.getenv("SEARXNG_BASE_URL", ""),
    memories=""  # Empty for stateless operation
)
```

### 5. Response Format
Implement OpenAI-compliant response structure:
```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "gpt-4o-mini",
  "choices": [{
    "index": 0,
    "message": {"role": "assistant", "content": "..."},
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 50,
    "total_tokens": 150
  }
}
```

## Implementation Reference

### Primary Example
The main implementation reference is located at:
**`PRPs/examples/pydantic-ai-openai-compatible.py`**

This example demonstrates:
- Complete OpenAI API request/response models
- Message format conversion functions
- Streaming implementation using Pydantic AI's `iter()` method
- Proper SSE chunk formatting
- Token counting with tiktoken
- Error handling in OpenAI format

### Key Code Sections from Example

1. **Message Conversion** (lines 157-205):
```python
def convert_messages_to_pydantic_ai(messages: List[ChatMessage]) -> tuple[str, list]:
    """Convert OpenAI format messages to PydanticAI format"""
    # Handles system, user, and assistant messages
    # Returns (user_prompt, message_history)
```

2. **Streaming Implementation** (lines 208-334):
```python
async def stream_chat_completion_real(request: ChatCompletionRequest):
    # Uses agent.iter() for streaming
    # Properly formats SSE chunks
    # Handles PartDeltaEvent and TextPartDelta
```

3. **Non-streaming Implementation** (lines 449-535):
```python
@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    # Uses agent.run() for non-streaming
    # Formats response per OpenAI spec
```

## Environment Configuration

### New Environment Variable
Add to `.env` and `.env.example`:
```env
# OpenAI API Compatible Endpoints Authentication
OPENAI_COMPATIBLE_API_KEY=your-secret-api-key-here  # Required for /v1/* endpoints
```

### Docker Compose Update
Update `docker-compose.yml` to include the new environment variable:
```yaml
services:
  agent-api:
    environment:
      - OPENAI_COMPATIBLE_API_KEY=${OPENAI_COMPATIBLE_API_KEY}
```

## Implementation Considerations

### 1. Stateless Operation
- No conversation history storage in database
- Client manages conversation context
- No rate limiting on OpenAI endpoints
- No request tracking/logging

### 2. Tool Availability
All agent tools remain available:
- ✅ RAG search (via Supabase client)
- ✅ Web search (Brave/SearXNG)
- ✅ Image analysis
- ✅ SQL query execution
- ✅ Code execution (if MCP server configured)
- ✅ Document listing and retrieval

### 3. Memory System
- Mem0 integration disabled for OpenAI endpoints (stateless)
- No memory retrieval or storage
- Memories parameter passed as empty string

### 4. Error Handling
- Return errors in OpenAI format:
```json
{
  "error": {
    "message": "Error description",
    "type": "invalid_request_error",
    "code": null
  }
}
```

### 5. CORS Configuration
- Existing CORS middleware already allows all origins
- No changes needed for Obsidian plugin compatibility

## Benefits

1. **Obsidian Integration**: Seamlessly connect AI agent to Obsidian for enhanced note-taking and knowledge management
2. **Standard Compatibility**: Works with any OpenAI-compatible client
3. **Full Agent Capabilities**: Maintains access to RAG, web search, and all tools
4. **Simple Deployment**: No additional infrastructure required
5. **Security**: Simple API key auth without complex token management

## Documentation Updates

After implementation, update:
1. `backend_agent_api/README.md` - Add OpenAI endpoints documentation
2. `README.md` - Add Obsidian integration guide
3. `.env.example` - Add OPENAI_COMPATIBLE_API_KEY variable
4. API documentation with example requests

## Security Considerations

1. **API Key Storage**: Store OPENAI_COMPATIBLE_API_KEY securely, never commit to git
2. **Rate Limiting**: Consider adding rate limiting for OpenAI endpoints in production
3. **Input Validation**: Validate all OpenAI request parameters
4. **Token Limits**: Respect max_tokens parameter to prevent excessive generation
5. **HTTPS**: Use HTTPS in production for API key transmission

## Success Criteria

- [ ] OpenAI endpoints return valid responses matching OpenAI spec
- [ ] Streaming works correctly with SSE format
- [ ] All agent tools (RAG, web search, etc.) function via OpenAI endpoints
- [ ] Obsidian AI plugin successfully connects and operates
- [ ] No impact on existing `/api/pydantic-agent` endpoint
- [ ] Docker deployment includes new environment variable
- [ ] Tests demonstrate functionality with curl commands