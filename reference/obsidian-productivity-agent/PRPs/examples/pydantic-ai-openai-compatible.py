import asyncio
import json
import time
import uuid
import os
from typing import List, Optional, Dict, Any, Union, Literal
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.messages import (
    ModelRequest,
    ModelResponse,
    SystemPromptPart,
    UserPromptPart,
    TextPart,
    ToolCallPart,
    ToolReturn,
)
from dotenv import load_dotenv
import tiktoken

# Load environment variables
load_dotenv()

# Get configuration from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_CHOICE = os.getenv("LLM_CHOICE", "gpt-4o-mini")

# Set OpenAI API key in environment for PydanticAI to use
if OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Initialize the PydanticAI agent with the chosen model
agent = Agent(f'openai:{LLM_CHOICE}')

app = FastAPI(
    title="OpenAI-compatible API",
    version="2.0.0",
    description="OpenAI-compatible API server powered by PydanticAI"
)

# Add CORS middleware with very permissive settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods including OPTIONS
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"]  # Expose all headers
)


class ChatMessage(BaseModel):
    role: str  # More flexible - accept any role string
    content: Optional[Union[str, List[Dict[str, Any]]]] = None  # Content can be string or list for multimodal
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None


class ChatCompletionRequest(BaseModel):
    model: str = "gpt-3.5-turbo"
    messages: List[ChatMessage]
    max_tokens: Optional[int] = Field(default=None, description="Maximum number of tokens to generate")
    temperature: Optional[float] = Field(default=1.0, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(default=1.0, ge=0.0, le=1.0)
    n: Optional[int] = Field(default=1, ge=1, le=128)
    stream: Optional[bool] = Field(default=False)
    stop: Optional[Union[str, List[str]]] = None
    presence_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0)
    frequency_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0)
    logit_bias: Optional[Dict[str, float]] = None
    user: Optional[str] = None
    seed: Optional[int] = None
    response_format: Optional[Dict[str, Any]] = None
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None


class CompletionRequest(BaseModel):
    model: str = "gpt-3.5-turbo-instruct"
    prompt: Union[str, List[str]]
    max_tokens: Optional[int] = Field(default=16)
    temperature: Optional[float] = Field(default=1.0, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(default=1.0, ge=0.0, le=1.0)
    n: Optional[int] = Field(default=1, ge=1, le=128)
    stream: Optional[bool] = Field(default=False)
    logprobs: Optional[int] = None
    echo: Optional[bool] = Field(default=False)
    stop: Optional[Union[str, List[str]]] = None
    presence_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0)
    frequency_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0)
    best_of: Optional[int] = Field(default=1, ge=1)
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
    finish_reason: Optional[str] = None  # More flexible - accept any finish reason


class ChatCompletionResponse(BaseModel):
    id: str
    object: Literal["chat.completion"] = "chat.completion"
    created: int
    model: str
    choices: List[Choice]
    usage: Usage
    system_fingerprint: Optional[str] = None


class CompletionChoice(BaseModel):
    text: str
    index: int
    logprobs: Optional[Any] = None
    finish_reason: Optional[str] = None  # More flexible


class CompletionResponse(BaseModel):
    id: str
    object: Literal["text_completion"] = "text_completion"
    created: int
    model: str
    choices: List[CompletionChoice]
    usage: Usage
    system_fingerprint: Optional[str] = None


def generate_completion_id() -> str:
    return f"chatcmpl-{uuid.uuid4().hex[:8]}"


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens in text using tiktoken"""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def convert_messages_to_pydantic_ai(messages: List[ChatMessage]) -> tuple[str, list]:
    """Convert OpenAI format messages to PydanticAI format
    Returns: (user_prompt, message_history)
    """
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


async def stream_chat_completion_real(request: ChatCompletionRequest):
    """Stream chat completion responses using PydanticAI"""
    completion_id = generate_completion_id()
    created = int(time.time())

    # Convert messages to PydanticAI format
    user_prompt, message_history = convert_messages_to_pydantic_ai(request.messages)

    # Prepare model settings
    model_settings = {
        'temperature': request.temperature,
        'top_p': request.top_p,
    }
    if request.max_tokens:
        model_settings['max_tokens'] = request.max_tokens

    # Send initial chunk with role
    initial_chunk = {
        "id": completion_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": request.model,
        "system_fingerprint": f"fp_{LLM_CHOICE}",
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
            FinalResultEvent,
        )

        # Run the agent with streaming using iter()
        async with agent.iter(
            user_prompt,
            message_history=message_history,
            model_settings=model_settings
        ) as agent_run:
            async for node in agent_run:
                # Check if this is a model request node (where streaming happens)
                if Agent.is_model_request_node(node):
                    # Stream model responses
                    async with node.stream(agent_run.ctx) as request_stream:
                        final_result_found = False

                        async for event in request_stream:
                            # Handle text delta events
                            if isinstance(event, PartDeltaEvent):
                                if isinstance(event.delta, TextPartDelta):
                                    chunk = {
                                        "id": completion_id,
                                        "object": "chat.completion.chunk",
                                        "created": created,
                                        "model": request.model,
                                        "system_fingerprint": f"fp_{LLM_CHOICE}",
                                        "choices": [{
                                            "index": 0,
                                            "delta": {"content": event.delta.content_delta},
                                            "logprobs": None,
                                            "finish_reason": None
                                        }]
                                    }
                                    yield f"data: {json.dumps(chunk)}\n\n"
                            elif isinstance(event, FinalResultEvent):
                                final_result_found = True
                                break

                        # Stream final result text if found
                        if final_result_found:
                            async for text_chunk in request_stream.stream_text(delta=True):
                                if text_chunk:
                                    chunk = {
                                        "id": completion_id,
                                        "object": "chat.completion.chunk",
                                        "created": created,
                                        "model": request.model,
                                        "system_fingerprint": f"fp_{LLM_CHOICE}",
                                        "choices": [{
                                            "index": 0,
                                            "delta": {"content": text_chunk},
                                            "logprobs": None,
                                            "finish_reason": None
                                        }]
                                    }
                                    yield f"data: {json.dumps(chunk)}\n\n"

            # Send final chunk with finish_reason
            final_chunk = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": request.model,
                "system_fingerprint": f"fp_{LLM_CHOICE}",
                "choices": [{
                    "index": 0,
                    "delta": {},
                    "logprobs": None,
                    "finish_reason": "stop"
                }]
            }
            yield f"data: {json.dumps(final_chunk)}\n\n"

    except Exception as e:
        # Send error in OpenAI format
        error_chunk = {
            "id": completion_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": request.model,
            "error": {
                "message": str(e),
                "type": "internal_error",
                "code": None
            }
        }
        yield f"data: {json.dumps(error_chunk)}\n\n"

    # Send [DONE] marker
    yield "data: [DONE]\n\n"


async def stream_completion_real(request: CompletionRequest):
    """Stream completion responses using PydanticAI"""
    completion_id = f"cmpl-{uuid.uuid4().hex[:8]}"
    created = int(time.time())

    prompt = request.prompt if isinstance(request.prompt, str) else request.prompt[0]

    # Prepare model settings
    model_settings = {
        'temperature': request.temperature,
        'top_p': request.top_p,
    }
    if request.max_tokens:
        model_settings['max_tokens'] = request.max_tokens

    try:
        # Import streaming event types
        from pydantic_ai.messages import (
            PartDeltaEvent,
            TextPartDelta,
            FinalResultEvent,
        )

        # For completions, we just pass the prompt directly
        async with agent.iter(
            prompt,
            model_settings=model_settings
        ) as agent_run:
            async for node in agent_run:
                # Check if this is a model request node (where streaming happens)
                if Agent.is_model_request_node(node):
                    # Stream model responses
                    async with node.stream(agent_run.ctx) as request_stream:
                        final_result_found = False

                        async for event in request_stream:
                            # Handle text delta events
                            if isinstance(event, PartDeltaEvent):
                                if isinstance(event.delta, TextPartDelta):
                                    chunk = {
                                        "id": completion_id,
                                        "object": "text_completion",
                                        "created": created,
                                        "model": request.model,
                                        "choices": [{
                                            "text": event.delta.content_delta,
                                            "index": 0,
                                            "logprobs": None,
                                            "finish_reason": None
                                        }]
                                    }
                                    yield f"data: {json.dumps(chunk)}\n\n"
                            elif isinstance(event, FinalResultEvent):
                                final_result_found = True
                                break

                        # Stream final result text if found
                        if final_result_found:
                            async for text_chunk in request_stream.stream_text(delta=True):
                                if text_chunk:
                                    chunk = {
                                        "id": completion_id,
                                        "object": "text_completion",
                                        "created": created,
                                        "model": request.model,
                                        "choices": [{
                                            "text": text_chunk,
                                            "index": 0,
                                            "logprobs": None,
                                            "finish_reason": None
                                        }]
                                    }
                                    yield f"data: {json.dumps(chunk)}\n\n"

            # Send final chunk with finish_reason
            final_chunk = {
                "id": completion_id,
                "object": "text_completion",
                "created": created,
                "model": request.model,
                "choices": [{
                    "text": "",
                    "index": 0,
                    "logprobs": None,
                    "finish_reason": "stop"
                }]
            }
            yield f"data: {json.dumps(final_chunk)}\n\n"

    except Exception as e:
        # Send error in OpenAI format
        error_chunk = {
            "id": completion_id,
            "object": "text_completion",
            "created": created,
            "model": request.model,
            "error": {
                "message": str(e),
                "type": "internal_error",
                "code": None
            }
        }
        yield f"data: {json.dumps(error_chunk)}\n\n"

    yield "data: [DONE]\n\n"


@app.get("/")
async def root():
    return {"message": "OpenAI-compatible API server is running with PydanticAI"}


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest, authorization: Optional[str] = Header(None)):
    """Create a chat completion using PydanticAI"""

    if request.stream:
        return StreamingResponse(
            stream_chat_completion_real(request),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            }
        )

    # Non-streaming response
    completion_id = generate_completion_id()
    created = int(time.time())

    # Convert messages to PydanticAI format
    user_prompt, message_history = convert_messages_to_pydantic_ai(request.messages)

    # Prepare model settings
    model_settings = {
        'temperature': request.temperature,
        'top_p': request.top_p,
    }
    if request.max_tokens:
        model_settings['max_tokens'] = request.max_tokens

    try:
        # Run the agent
        result = await agent.run(
            user_prompt,
            message_history=message_history,
            model_settings=model_settings
        )

        # Get the response text from the last message
        if result.messages:
            last_message = result.messages[-1]
            if isinstance(last_message, ModelResponse):
                # Extract text from the response parts
                response_text = ""
                for part in last_message.parts:
                    if isinstance(part, TextPart):
                        response_text += part.content
            else:
                response_text = ""
        else:
            response_text = ""

        # Calculate token counts
        prompt_tokens = 0
        for msg in request.messages:
            if msg.content:
                if isinstance(msg.content, str):
                    prompt_tokens += count_tokens(msg.content)
                elif isinstance(msg.content, list):
                    for item in msg.content:
                        if item.get("type") == "text":
                            prompt_tokens += count_tokens(item.get("text", ""))

        completion_tokens = count_tokens(response_text)

        response = ChatCompletionResponse(
            id=completion_id,
            created=created,
            model=request.model,
            choices=[
                Choice(
                    index=0,
                    message=ChatMessage(role="assistant", content=response_text),
                    finish_reason="stop"
                )
            ],
            usage=Usage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens
            ),
            system_fingerprint=f"fp_{LLM_CHOICE}"
        )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/completions")
async def completions(request: CompletionRequest, authorization: Optional[str] = Header(None)):
    """Create a completion using PydanticAI"""

    if request.stream:
        return StreamingResponse(
            stream_completion_real(request),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            }
        )

    # Non-streaming response
    completion_id = f"cmpl-{uuid.uuid4().hex[:8]}"
    created = int(time.time())

    prompt = request.prompt if isinstance(request.prompt, str) else request.prompt[0]

    # Prepare model settings
    model_settings = {
        'temperature': request.temperature,
        'top_p': request.top_p,
    }
    if request.max_tokens:
        model_settings['max_tokens'] = request.max_tokens

    try:
        # Run the agent with just the prompt
        result = await agent.run(
            prompt,
            model_settings=model_settings
        )

        # Get the response text from the last message
        if result.messages:
            last_message = result.messages[-1]
            if isinstance(last_message, ModelResponse):
                # Extract text from the response parts
                response_text = ""
                for part in last_message.parts:
                    if isinstance(part, TextPart):
                        response_text += part.content
            else:
                response_text = ""
        else:
            response_text = ""

        # Calculate token counts
        prompt_tokens = count_tokens(prompt)
        completion_tokens = count_tokens(response_text)

        response = CompletionResponse(
            id=completion_id,
            created=created,
            model=request.model,
            choices=[
                CompletionChoice(
                    text=response_text,
                    index=0,
                    finish_reason="stop"
                )
            ],
            usage=Usage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens
            ),
            system_fingerprint=f"fp_{LLM_CHOICE}"
        )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions in OpenAI format"""
    return {
        "error": {
            "message": exc.detail,
            "type": "invalid_request_error",
            "param": None,
            "code": None
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8090)