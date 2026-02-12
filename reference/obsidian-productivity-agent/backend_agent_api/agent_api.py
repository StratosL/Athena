from typing import List, Optional, Dict, Any, AsyncIterator, Union, Tuple, Literal
from fastapi import FastAPI, HTTPException, Security, Depends, Request, Form, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager, nullcontext
from supabase import create_client, Client
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
from dotenv import load_dotenv
from httpx import AsyncClient
from pathlib import Path
from mem0 import Memory
import asyncio
import base64
import time
import json
import sys
import os
import uuid
import tiktoken

# Import Langfuse configuration
from configure_langfuse import configure_langfuse

# Import database utility functions
from db_utils import (
    fetch_conversation_history,
    create_conversation,
    update_conversation_title,
    generate_session_id,
    generate_conversation_title,
    store_message,
    convert_history_to_pydantic_format,
    check_rate_limit,
    store_request
)

from pydantic_ai import Agent, BinaryContent
# Import all the message part classes from Pydantic AI
from pydantic_ai.messages import (
    ModelMessage, ModelRequest, ModelResponse, TextPart, ModelMessagesTypeAdapter,
    UserPromptPart, PartDeltaEvent, PartStartEvent, TextPartDelta, SystemPromptPart
)

from agent import agent, AgentDeps, get_model
from clients import get_agent_clients, get_mem0_client_async

# Check if we're in production
is_production = os.getenv("ENVIRONMENT") == "production"

if not is_production:
    # Development: prioritize .env file
    project_root = Path(__file__).resolve().parent
    dotenv_path = project_root / '.env'
    load_dotenv(dotenv_path, override=True)
else:
    # Production: use cloud platform env vars only
    load_dotenv()

# Define clients as None initially
embedding_client = None
supabase = None
http_client = None
title_agent = None
mem0_client = None
tracer = None

# Define the lifespan context manager for the application
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the FastAPI application.
    
    Handles initialization and cleanup of resources.
    """
    global embedding_client, supabase, http_client, title_agent, mem0_client, tracer

    # Initialize Langfuse tracer (returns None if not configured)
    tracer = configure_langfuse()    
    
    # Startup: Initialize all clients
    embedding_client, supabase = get_agent_clients()
    http_client = AsyncClient()
    title_agent = Agent(model=get_model())
    mem0_client = await get_mem0_client_async()
    
    yield  # This is where the app runs
    
    # Shutdown: Clean up resources
    if http_client:
        await http_client.aclose()

# Initialize FastAPI app
app = FastAPI(lifespan=lifespan)
security = HTTPBearer()        

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict[str, Any]:
    """
    Verify the JWT token from Supabase and return the user information.
    
    Args:
        credentials: The HTTP Authorization credentials containing the bearer token
        
    Returns:
        Dict[str, Any]: The user information from Supabase
        
    Raises:
        HTTPException: If the token is invalid or the user cannot be verified
    """
    try:
        # Get the token from the Authorization header
        token = credentials.credentials
        
        # Access the global HTTP client
        global http_client # noqa: F824
        if not http_client:
            raise HTTPException(status_code=500, detail="HTTP client not initialized")
        
        # Get the Supabase URL and anon key from environment variables
        # These should match the environment variable names used in your project
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        # Make request to Supabase auth API to get user info using the global HTTP client
        response = await http_client.get(
            f"{supabase_url}/auth/v1/user",
            headers={
                "Authorization": f"Bearer {token}",
                "apikey": supabase_key
            }
        )
        
        # Check if the request was successful
        if response.status_code != 200:
            print(f"Auth response error: {response.text}")
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        
        # Return the user information
        user_data = response.json()
        return user_data
    except Exception as e:
        print(f"Authentication error: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")

async def verify_openai_api_key(authorization: Optional[str] = None) -> bool:
    """
    Verify the API key for OpenAI compatible endpoints.

    Args:
        authorization: The Authorization header value

    Returns:
        True if the API key is valid

    Raises:
        HTTPException: If the API key is missing or invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail={"error": {"message": "Missing API key in Authorization header", "type": "invalid_request_error"}}
        )

    # Extract the API key from "Bearer <key>" format
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail={"error": {"message": "Invalid Authorization header format. Use 'Bearer <api_key>'", "type": "invalid_request_error"}}
        )

    api_key = authorization.replace("Bearer ", "")
    expected_key = os.getenv("OPENAI_COMPATIBLE_API_KEY")

    if not expected_key:
        raise HTTPException(
            status_code=500,
            detail={"error": {"message": "OpenAI compatible API is not configured", "type": "server_error"}}
        )

    if api_key != expected_key:
        raise HTTPException(
            status_code=401,
            detail={"error": {"message": "Invalid API key", "type": "invalid_api_key"}}
        )

    return True

# Request/Response Models
class FileAttachment(BaseModel):
    fileName: str
    content: str  # Base64 encoded content
    mimeType: str

class AgentRequest(BaseModel):
    query: str
    user_id: str
    request_id: str
    session_id: str
    files: Optional[List[FileAttachment]] = None

# OpenAI API Compatible Models
class ChatMessage(BaseModel):
    role: str  # system, user, assistant, tool, function
    content: Optional[Union[str, List[Dict[str, Any]]]] = None
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None

class ChatCompletionRequest(BaseModel):
    model: str = "gpt-4o-mini"
    messages: List[ChatMessage]
    max_tokens: Optional[int] = None
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    logit_bias: Optional[Dict[str, float]] = None
    user: Optional[str] = None
    seed: Optional[int] = None
    response_format: Optional[Dict[str, Any]] = None
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None

class CompletionRequest(BaseModel):
    model: str = "gpt-3.5-turbo-instruct"
    prompt: Union[str, List[str]]
    max_tokens: Optional[int] = 16
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    logprobs: Optional[int] = None
    echo: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    best_of: Optional[int] = 1
    logit_bias: Optional[Dict[str, float]] = None
    user: Optional[str] = None
    suffix: Optional[str] = None

class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class Choice(BaseModel):
    index: int
    message: ChatMessage
    logprobs: Optional[Any] = None
    finish_reason: Optional[str] = None

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Choice]
    usage: Usage
    system_fingerprint: Optional[str] = None

class CompletionChoice(BaseModel):
    text: str
    index: int
    logprobs: Optional[Any] = None
    finish_reason: Optional[str] = None

class CompletionResponse(BaseModel):
    id: str
    object: str = "text_completion"
    created: int
    model: str
    choices: List[CompletionChoice]
    usage: Usage
    system_fingerprint: Optional[str] = None

# OpenAI Utility Functions
def generate_completion_id() -> str:
    """Generate a unique completion ID in OpenAI format"""
    return f"chatcmpl-{uuid.uuid4().hex[:8]}"

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Count tokens in text using tiktoken.

    Args:
        text: The text to count tokens for
        model: The model name to use for encoding

    Returns:
        Number of tokens in the text
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # Default to cl100k_base encoding if model not found
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

def convert_messages_to_pydantic_ai(messages: List[ChatMessage]) -> Tuple[str, List]:
    """
    Convert OpenAI format messages to PydanticAI format.

    Args:
        messages: List of ChatMessage objects in OpenAI format

    Returns:
        Tuple of (user_prompt, message_history) for PydanticAI
    """
    from pydantic_ai.messages import (
        ModelRequest, ModelResponse, SystemPromptPart,
        UserPromptPart, TextPart
    )

    pydantic_messages = []
    user_prompt = ""
    system_prompt = None

    for msg in messages:
        content = msg.content
        if content is None:
            continue

        # Extract text content from multimodal messages
        if isinstance(content, list):
            text_content = ""
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_content += item.get("text", "")
            content = text_content

        if msg.role == "system":
            system_prompt = content
        elif msg.role == "user":
            user_prompt = content  # Keep the last user message as the prompt
            # Create a ModelRequest with UserPromptPart
            pydantic_messages.append(
                ModelRequest(parts=[UserPromptPart(content=content)])
            )
        elif msg.role == "assistant":
            # Create ModelResponse with TextPart
            pydantic_messages.append(
                ModelResponse(parts=[TextPart(content=content)])
            )

    # If we have a system prompt, prepend it to the message history
    if system_prompt:
        pydantic_messages.insert(
            0,
            ModelRequest(parts=[SystemPromptPart(content=system_prompt)])
        )

    # Remove the last user message from history since it's the current prompt
    if pydantic_messages and isinstance(pydantic_messages[-1], ModelRequest):
        # Check if last message contains a UserPromptPart
        if any(isinstance(part, UserPromptPart) for part in pydantic_messages[-1].parts):
            pydantic_messages = pydantic_messages[:-1]

    return user_prompt, pydantic_messages

def get_stateless_agent_deps() -> AgentDeps:
    """
    Create simplified AgentDeps for stateless OpenAI-compatible operations.

    This function creates minimal dependencies without requiring user authentication
    or conversation history tracking. Perfect for OpenAI API compatibility.

    Returns:
        AgentDeps with essential services for stateless operation
    """
    global embedding_client, supabase, http_client

    return AgentDeps(
        embedding_client=embedding_client,
        supabase=supabase,
        http_client=http_client,
        brave_api_key=os.getenv("BRAVE_API_KEY", ""),
        searxng_base_url=os.getenv("SEARXNG_BASE_URL", ""),
        memories=""  # No memories for stateless operation
    )


# Add this helper function to your backend code
async def stream_error_response(error_message: str, session_id: str):
    """
    Creates a streaming response for error messages.
    
    Args:
        error_message: The error message to display to the user
        session_id: The current session ID
        
    Yields:
        Encoded JSON chunks for the streaming response
    """
    # First yield the error message as text
    yield json.dumps({"text": error_message}).encode('utf-8') + b'\n'
    
    # Then yield a final chunk with complete flag
    final_data = {
        "text": error_message,
        "session_id": session_id,
        "error": error_message,
        "complete": True
    }
    yield json.dumps(final_data).encode('utf-8') + b'\n'

@app.post("/api/pydantic-agent")
async def pydantic_agent(request: AgentRequest, user: Dict[str, Any] = Depends(verify_token)):
    # Verify that the user ID in the request matches the user ID from the token
    if request.user_id != user.get("id"):
        return StreamingResponse(
            stream_error_response("User ID in request does not match authenticated user", request.session_id),
            media_type='text/plain'
        )
        
    try:
        # Check rate limit
        rate_limit_ok = await check_rate_limit(supabase, request.user_id)
        if not rate_limit_ok:
            return StreamingResponse(
                stream_error_response("Rate limit exceeded. Please try again later.", request.session_id),
                media_type='text/plain'
            )
        
        # Start request tracking in parallel
        request_tracking_task = asyncio.create_task(
            store_request(supabase, request.request_id, request.user_id, request.query)
        )
        
        session_id = request.session_id
        conversation_record = None
        conversation_title = None
        
        # Check if session_id is empty, create a new conversation if needed
        if not session_id:
            session_id = generate_session_id(request.user_id)
            # Create a new conversation record
            conversation_record = await create_conversation(supabase, request.user_id, session_id)
        
        # Store user's query immediately with any file attachments
        file_attachments = None
        if request.files:
            # Convert Pydantic models to dictionaries for storage
            file_attachments = [{
                "fileName": file.fileName,
                "content": file.content,
                "mimeType": file.mimeType
            } for file in request.files]
            
        await store_message(
            supabase=supabase,
            session_id=session_id,
            message_type="human",
            content=request.query,
            files=file_attachments
        )
        
        # Fetch conversation history from the DB
        conversation_history = await fetch_conversation_history(supabase, session_id)
        
        # Convert conversation history to Pydantic AI format
        pydantic_messages = await convert_history_to_pydantic_format(conversation_history)
        
        # Retrieve relevant memories with Mem0
        relevant_memories = {"results": []}
        try:
            relevant_memories = await mem0_client.search(query=request.query, user_id=request.user_id, limit=3)
        except:
            # Slight hack - retry again with a new connection pool
            time.sleep(1)
            relevant_memories = await mem0_client.search(query=request.query, user_id=request.user_id, limit=3)

        memories_str = "\n".join(f"- {entry['memory']}" for entry in relevant_memories["results"])
        
        # Create memory task to run in parallel
        memory_messages = [{"role": "user", "content": request.query}]
        memory_task = asyncio.create_task(mem0_client.add(memory_messages, user_id=request.user_id))
        
        # Start title generation in parallel if this is a new conversation
        title_task = None
        if conversation_record:
            title_task = asyncio.create_task(generate_conversation_title(title_agent, request.query))
        
        async def stream_response():
            # Process title result if it exists (in the background)
            nonlocal conversation_title

            # Use the global HTTP client
            agent_deps = AgentDeps(
                embedding_client=embedding_client, 
                supabase=supabase, 
                http_client=http_client,
                brave_api_key=os.getenv("BRAVE_API_KEY", ""),
                searxng_base_url=os.getenv("SEARXNG_BASE_URL", ""),
                memories=memories_str
            )
            
            # Process any file attachments for the agent
            binary_contents = []
            if request.files:
                for file in request.files:
                    try:
                        # Decode the base64 content
                        binary_data = base64.b64decode(file.content)
                        # Create a BinaryContent object
                        fileMimeType = "application/pdf" if file.mimeType == "text/plain" else file.mimeType
                        binary_content = BinaryContent(
                            data=binary_data,
                            media_type=fileMimeType
                        )
                        binary_contents.append(binary_content)
                    except Exception as e:
                        print(f"Error processing file {file.fileName}: {str(e)}")
            
            # Create input for the agent with the query and any binary contents
            agent_input = [request.query]
            if binary_contents:
                agent_input.extend(binary_contents)
            
            full_response = ""
            
            # Use tracer context if available, otherwise use nullcontext
            span_context = tracer.start_as_current_span("Pydantic-Ai-Trace") if tracer else nullcontext()
            
            with span_context as span:
                if tracer and span:
                    # Set user and session attributes for Langfuse
                    span.set_attribute("langfuse.user.id", request.user_id)
                    span.set_attribute("langfuse.session.id", session_id)
                    span.set_attribute("input.value", request.query)
                
                # Run the agent with the user prompt, binary contents, and the chat history
                async with agent.iter(agent_input, deps=agent_deps, message_history=pydantic_messages) as run:
                    async for node in run:
                        if Agent.is_model_request_node(node):
                            # A model request node => We can stream tokens from the model's request
                            async with node.stream(run.ctx) as request_stream:
                                async for event in request_stream:
                                    if isinstance(event, PartStartEvent) and event.part.part_kind == 'text':
                                        yield json.dumps({"text": event.part.content}).encode('utf-8') + b'\n'
                                        full_response += event.part.content
                                    elif isinstance(event, PartDeltaEvent) and isinstance(event.delta, TextPartDelta):
                                        delta = event.delta.content_delta
                                        yield json.dumps({"text": full_response}).encode('utf-8') + b'\n'
                                        full_response += delta
                
                # Set the output value after completion if tracing
                if tracer and span:
                    span.set_attribute("output.value", full_response)
                    
            # After streaming is complete, store the full response in the database
            message_data = run.result.new_messages_json()
            
            # Store agent's response
            await store_message(
                supabase=supabase,
                session_id=session_id,
                message_type="ai",
                content=full_response,
                message_data=message_data,
                data={"request_id": request.request_id}
            )
            
            # Wait for title generation to complete if it's running
            if title_task:
                try:
                    title_result = await title_task
                    conversation_title = title_result
                    # Update the conversation title in the database
                    await update_conversation_title(supabase, session_id, conversation_title)
                    
                    # Send the final title in the last chunk
                    final_data = {
                        "text": full_response,
                        "session_id": session_id,
                        "conversation_title": conversation_title,
                        "complete": True
                    }
                    yield json.dumps(final_data).encode('utf-8') + b'\n'
                except Exception as e:
                    print(f"Error processing title: {str(e)}")
            else:
                yield json.dumps({"text": full_response, "complete": True}).encode('utf-8') + b'\n'

            # Wait for the memory task to complete if needed
            try:
                await memory_task
            except Exception as e:
                print(f"Error updating memories: {str(e)}")
                
            # Wait for request tracking task to complete
            try:
                await request_tracking_task
            except Exception as e:
                print(f"Error tracking request: {str(e)}")
            except asyncio.CancelledError:
                # This is expected if the task was cancelled
                pass
        
        return StreamingResponse(stream_response(), media_type='text/plain')

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        # Store error message in conversation if session_id exists
        if request.session_id:
            await store_message(
                supabase=supabase,
                session_id=request.session_id,
                message_type="ai",
                content="I apologize, but I encountered an error processing your request.",
                data={"error": str(e), "request_id": request.request_id}
            )
        # Return a streaming response with the error
        return StreamingResponse(
            stream_error_response(f"Error: {str(e)}", request.session_id),
            media_type='text/plain'
        )


@app.post("/v1/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    authorization: str = Header(None)
):
    """
    OpenAI-compatible chat completions endpoint.

    This endpoint provides OpenAI API compatibility for chat-based interactions.
    Supports both streaming and non-streaming responses.
    """
    # Verify API key
    await verify_openai_api_key(authorization)

    # Convert messages to PydanticAI format
    user_prompt, message_history = convert_messages_to_pydantic_ai(request.messages)

    # Get stateless dependencies
    agent_deps = get_stateless_agent_deps()

    # Configure model settings
    model_settings = {}
    if request.temperature is not None:
        model_settings['temperature'] = request.temperature
    if request.top_p is not None:
        model_settings['top_p'] = request.top_p
    if request.max_tokens is not None:
        model_settings['max_tokens'] = request.max_tokens

    if request.stream:
        # Streaming response
        async def stream_response():
            completion_id = generate_completion_id()
            created = int(time.time())

            # Send initial chunk with role
            initial_chunk = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": request.model,
                "system_fingerprint": f"fp_{os.getenv('LLM_CHOICE', 'gpt-4o-mini')}",
                "choices": [{
                    "index": 0,
                    "delta": {"role": "assistant", "content": ""},
                    "logprobs": None,
                    "finish_reason": None
                }]
            }
            yield f"data: {json.dumps(initial_chunk)}\n\n"

            try:
                # Import streaming event types
                from pydantic_ai.messages import (
                    PartDeltaEvent,
                    TextPartDelta,
                )

                # Run the agent with iter() for proper delta streaming
                async with agent.iter(
                    user_prompt,
                    message_history=message_history,
                    deps=agent_deps,
                    model_settings=model_settings
                ) as agent_run:
                    async for node in agent_run:
                        # Check if this is a model request node (where streaming happens)
                        if Agent.is_model_request_node(node):
                            # Stream model responses
                            async with node.stream(agent_run.ctx) as request_stream:
                                async for event in request_stream:
                                    # Handle text delta events
                                    if isinstance(event, PartDeltaEvent):
                                        if isinstance(event.delta, TextPartDelta):
                                            chunk = {
                                                "id": completion_id,
                                                "object": "chat.completion.chunk",
                                                "created": created,
                                                "model": request.model,
                                                "choices": [{
                                                    "index": 0,
                                                    "delta": {"content": event.delta.content_delta},
                                                    "logprobs": None,
                                                    "finish_reason": None
                                                }]
                                            }
                                            yield f"data: {json.dumps(chunk)}\n\n"

                # Send final chunk
                final_chunk = {
                    "id": completion_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": request.model,
                    "choices": [{
                        "index": 0,
                        "delta": {},
                        "logprobs": None,
                        "finish_reason": "stop"
                    }]
                }
                yield f"data: {json.dumps(final_chunk)}\n\n"
                yield "data: [DONE]\n\n"

            except Exception as e:
                error_chunk = {
                    "error": {
                        "message": f"Stream error: {str(e)}",
                        "type": "server_error"
                    }
                }
                yield f"data: {json.dumps(error_chunk)}\n\n"

        return StreamingResponse(
            stream_response(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
        )
    else:
        # Non-streaming response
        try:
            # Run the agent
            result = await agent.run(
                user_prompt,
                message_history=message_history,
                deps=agent_deps,
                model_settings=model_settings
            )

            # Count tokens for usage reporting
            prompt_text = user_prompt
            for msg in request.messages:
                if msg.content:
                    if isinstance(msg.content, str):
                        prompt_text += " " + msg.content
                    elif isinstance(msg.content, list):
                        for item in msg.content:
                            if isinstance(item, dict) and item.get("type") == "text":
                                prompt_text += " " + item.get("text", "")

            prompt_tokens = count_tokens(prompt_text, request.model)
            completion_tokens = count_tokens(result.data or "", request.model)

            # Build the response
            response = ChatCompletionResponse(
                id=generate_completion_id(),
                object="chat.completion",
                created=int(time.time()),
                model=request.model,
                choices=[
                    Choice(
                        index=0,
                        message=ChatMessage(
                            role="assistant",
                            content=result.data or ""
                        ),
                        finish_reason="stop"
                    )
                ],
                usage=Usage(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens
                ),
                system_fingerprint=f"fp_{os.getenv('LLM_CHOICE', 'gpt-4o-mini')}"
            )

            return response

        except Exception as e:
            print(f"Error in chat completion: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail={"error": {"message": f"Internal server error: {str(e)}", "type": "server_error"}}
            )

@app.get("/health")
async def health_check():
    """
    Health check endpoint for container orchestration and monitoring.
    
    Returns:
        Dict with status and service health information
    """
    # Check if critical dependencies are initialized
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {
            "embedding_client": embedding_client is not None,
            "supabase": supabase is not None,
            "http_client": http_client is not None,
            "title_agent": title_agent is not None,
            "mem0_client": mem0_client is not None
        }
    }
    
    # If any critical service is not initialized, mark as unhealthy
    if not all(health_status["services"].values()):
        health_status["status"] = "unhealthy"
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status


if __name__ == "__main__":
    import uvicorn
    # Feel free to change the port here if you need
    uvicorn.run(app, host="0.0.0.0", port=8001)