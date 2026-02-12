# Implementation Plan: OpenAI API Compatibility

## Overview
This plan details the implementation of OpenAI API compatible endpoints for the existing AI agent application. This will enable integration with OpenAI-compatible clients, particularly the Obsidian AI plugin, while maintaining all existing agent capabilities (RAG, web search, image analysis, etc.) in a stateless operation mode.

## Requirements Summary
- Implement two OpenAI-standard endpoints: `/v1/chat/completions` and `/v1/completions`
- Support both streaming (SSE format) and non-streaming responses
- Add simple API key authentication via Bearer token
- Enable stateless operation without Supabase authentication or conversation storage
- Maintain all existing agent tools (RAG, web search, image analysis, SQL, code execution)
- Ensure compatibility with Obsidian AI plugin
- No impact on existing `/api/pydantic-agent` endpoint

## Research Findings

### Best Practices
- Use Server-Sent Events (SSE) format for streaming responses per OpenAI specification
- Implement proper token counting using tiktoken library
- Handle message format conversion between OpenAI and Pydantic AI formats
- Maintain stateless operation for simplified deployment and scaling
- Follow existing FastAPI patterns and middleware configurations

### Reference Implementations
- `PRPs/examples/pydantic-ai-openai-compatible.py` - Complete working example with all required features
- Current `agent_api.py` - Existing streaming patterns and agent integration
- Current `tools.py` - Tool implementations that will be reused

### Technology Decisions
- **FastAPI**: Continue using existing framework for consistency
- **Pydantic AI**: Leverage existing agent implementation with stateless deps
- **tiktoken**: Add for accurate token counting matching OpenAI's methodology
- **SSE Format**: Implement proper OpenAI streaming format with "data: " prefixes
- **Bearer Auth**: Simple API key authentication without complex JWT handling

## Implementation Tasks

### Phase 1: Foundation Setup
1. **Add OpenAI Message Models**
   - Description: Create Pydantic models for OpenAI request/response formats
   - Files to modify/create: `backend_agent_api/agent_api.py`
   - Dependencies: None
   - Estimated effort: 30 minutes

2. **Implement Message Format Conversion**
   - Description: Create utilities to convert between OpenAI and Pydantic AI message formats
   - Files to modify/create: `backend_agent_api/agent_api.py`
   - Dependencies: Task 1
   - Estimated effort: 45 minutes

3. **Add Token Counting Utility**
   - Description: Implement token counting using tiktoken for usage reporting
   - Files to modify/create: `backend_agent_api/agent_api.py`
   - Dependencies: Install tiktoken package
   - Estimated effort: 20 minutes

4. **Configure Environment Variables**
   - Description: Add OPENAI_COMPATIBLE_API_KEY to environment configuration
   - Files to modify/create: `.env.example`, `docker-compose.yml`
   - Dependencies: None
   - Estimated effort: 15 minutes

### Phase 2: Core Implementation
5. **Implement Authentication Middleware**
   - Description: Add API key validation for /v1/* endpoints
   - Files to modify/create: `backend_agent_api/agent_api.py`
   - Dependencies: Task 4
   - Estimated effort: 30 minutes

6. **Create Stateless Agent Dependencies**
   - Description: Setup simplified AgentDeps for stateless operation
   - Files to modify/create: `backend_agent_api/agent_api.py`
   - Dependencies: None
   - Estimated effort: 20 minutes

7. **Implement Chat Completions Endpoint (Non-streaming)**
   - Description: Create `/v1/chat/completions` POST endpoint for non-streaming responses
   - Files to modify/create: `backend_agent_api/agent_api.py`
   - Dependencies: Tasks 1, 2, 3, 5, 6
   - Estimated effort: 1 hour

8. **Implement Chat Completions Streaming**
   - Description: Add streaming support with proper SSE format for chat completions
   - Files to modify/create: `backend_agent_api/agent_api.py`
   - Dependencies: Task 7
   - Estimated effort: 1.5 hours

9. **Implement Legacy Completions Endpoint**
   - Description: Create `/v1/completions` POST endpoint for legacy support
   - Files to modify/create: `backend_agent_api/agent_api.py`
   - Dependencies: Tasks 1, 2, 3, 5, 6
   - Estimated effort: 45 minutes

10. **Add Error Handling in OpenAI Format**
    - Description: Implement OpenAI-compliant error responses
    - Files to modify/create: `backend_agent_api/agent_api.py`
    - Dependencies: Tasks 7, 8, 9
    - Estimated effort: 30 minutes

### Phase 3: Integration & Testing
11. **Update Requirements File**
    - Description: Add tiktoken dependency to requirements.txt
    - Files to modify/create: `backend_agent_api/requirements.txt`
    - Dependencies: None
    - Estimated effort: 10 minutes

12. **Create Test Suite**
    - Description: Write tests for OpenAI endpoints with curl command examples
    - Files to modify/create: `tests/test_openai_endpoints.py`
    - Dependencies: Tasks 7, 8, 9
    - Estimated effort: 1.5 hours

13. **Test Obsidian Integration**
    - Description: Validate connection and functionality with Obsidian AI plugin
    - Files to modify/create: None (manual testing)
    - Dependencies: All previous tasks
    - Estimated effort: 1 hour

14. **Update Documentation**
    - Description: Document OpenAI endpoints, usage examples, and Obsidian integration
    - Files to modify/create: `backend_agent_api/README.md`, `README.md`
    - Dependencies: All previous tasks
    - Estimated effort: 45 minutes

## Codebase Integration Points

### Files to Modify
- `backend_agent_api/agent_api.py` - Add new endpoints and OpenAI compatibility logic
- `backend_agent_api/requirements.txt` - Add tiktoken dependency
- `.env.example` - Add OPENAI_COMPATIBLE_API_KEY variable
- `docker-compose.yml` - Include new environment variable
- `backend_agent_api/README.md` - Add OpenAI endpoints documentation
- `README.md` - Add Obsidian integration guide

### New Files to Create
- `tests/test_openai_endpoints.py` - Test suite for OpenAI compatibility

### Existing Patterns to Follow
- Use existing CORS middleware configuration (already allows all origins)
- Follow current streaming implementation pattern from `/api/pydantic-agent`
- Reuse existing agent initialization and tool registration
- Maintain current error handling approach with proper status codes
- Use existing client configuration patterns for Supabase and OpenAI

## Technical Design

### Architecture Overview
```
Client (Obsidian/OpenAI-compatible)
            ↓
    [Authorization Header]
            ↓
    /v1/chat/completions
            ↓
    [API Key Validation]
            ↓
    [Message Format Conversion]
            ↓
    [Stateless Agent Execution]
            ↓
    [Tool Invocation (RAG, Web, etc.)]
            ↓
    [Response Formatting]
            ↓
    [SSE Streaming / JSON Response]
```

### Data Flow
1. Client sends OpenAI-formatted request with Bearer token
2. API validates the token against OPENAI_COMPATIBLE_API_KEY
3. Convert OpenAI messages to Pydantic AI format
4. Initialize stateless agent with simplified dependencies
5. Execute agent with all tools available
6. Stream or return response in OpenAI format
7. Include proper token usage statistics

### API Endpoints
- `POST /v1/chat/completions` - Main chat endpoint supporting streaming
- `POST /v1/completions` - Legacy completion endpoint for compatibility

### Request/Response Models
```python
# OpenAI Chat Request
{
  "model": "gpt-4o-mini",
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."}
  ],
  "stream": true/false,
  "max_tokens": 1000,
  "temperature": 0.7
}

# OpenAI Chat Response
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

## Dependencies and Libraries
- **tiktoken** - Token counting library (new dependency)
- **Existing dependencies**: FastAPI, Pydantic AI, httpx, Supabase client, AsyncOpenAI

## Testing Strategy
- **Unit tests** for message format conversion utilities
- **Integration tests** for endpoint functionality
- **Streaming tests** to validate SSE format compliance
- **Authentication tests** for API key validation
- **Tool invocation tests** to ensure all tools work via OpenAI endpoints
- **Edge cases**: Empty messages, invalid formats, authentication failures
- **Manual testing** with Obsidian AI plugin

## Success Criteria
- [ ] OpenAI endpoints return valid responses matching OpenAI spec
- [ ] Streaming works correctly with SSE format including "data: [DONE]" terminator
- [ ] All agent tools (RAG, web search, image analysis, SQL, code execution) function via OpenAI endpoints
- [ ] Obsidian AI plugin successfully connects and operates
- [ ] No impact on existing `/api/pydantic-agent` endpoint functionality
- [ ] Docker deployment includes new OPENAI_COMPATIBLE_API_KEY environment variable
- [ ] Tests demonstrate functionality with curl commands
- [ ] Token counting accurately reflects usage
- [ ] Error responses follow OpenAI error format

## Security Considerations
- Store OPENAI_COMPATIBLE_API_KEY securely using environment variables
- Never commit API keys to version control
- Validate all input parameters to prevent injection attacks
- Respect max_tokens parameter to prevent excessive generation
- Use HTTPS in production for secure API key transmission
- Consider adding rate limiting for production deployment

## Notes and Considerations
- **Stateless Design**: No conversation history is stored, clients must manage context
- **Memory System**: Mem0 integration is disabled for OpenAI endpoints
- **Tool Availability**: All tools remain functional including RAG (via Supabase)
- **Model Selection**: Uses configured LLM_CHOICE from existing environment
- **CORS**: Existing permissive CORS settings support Obsidian plugin
- **Future Enhancements**: Consider adding model listing endpoint, function calling support

---
*This plan is ready for execution with `/execute-plan`*