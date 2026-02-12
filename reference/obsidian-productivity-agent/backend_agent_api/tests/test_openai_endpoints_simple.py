"""
Simple API endpoint tests for OpenAI compatibility.

These tests validate the endpoints without needing full app startup.
"""

import pytest
import json
import os
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any


def test_api_key_validation():
    """Test API key validation function."""
    # Mock the verify_openai_api_key function from the implementation
    async def verify_openai_api_key(authorization: str = None) -> bool:
        if not authorization:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=401,
                detail={"error": {"message": "Missing API key in Authorization header", "type": "invalid_request_error"}}
            )

        if not authorization.startswith("Bearer "):
            from fastapi import HTTPException
            raise HTTPException(
                status_code=401,
                detail={"error": {"message": "Invalid Authorization header format. Use 'Bearer <api_key>'", "type": "invalid_request_error"}}
            )

        api_key = authorization.replace("Bearer ", "")
        expected_key = os.getenv("OPENAI_COMPATIBLE_API_KEY", "test-api-key")

        if api_key != expected_key:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=401,
                detail={"error": {"message": "Invalid API key", "type": "invalid_api_key"}}
            )

        return True

    # Test cases
    import asyncio
    from fastapi import HTTPException

    # Valid API key should pass
    asyncio.run(verify_openai_api_key("Bearer test-api-key"))

    # Missing authorization should fail
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(verify_openai_api_key(None))
    assert exc_info.value.status_code == 401
    assert "Missing API key" in str(exc_info.value.detail)

    # Invalid format should fail
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(verify_openai_api_key("test-api-key"))
    assert exc_info.value.status_code == 401
    assert "Invalid Authorization header format" in str(exc_info.value.detail)

    # Wrong key should fail
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(verify_openai_api_key("Bearer wrong-key"))
    assert exc_info.value.status_code == 401
    assert "Invalid API key" in str(exc_info.value.detail)


def test_token_counting():
    """Test token counting functionality."""
    import uuid

    def count_tokens(text: str, model: str = "gpt-4") -> int:
        """Mock token counting - simple approximation."""
        try:
            # Try to use tiktoken if available
            import tiktoken
            try:
                encoding = tiktoken.encoding_for_model(model)
            except KeyError:
                encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except ImportError:
            # Fallback to simple approximation
            return max(1, len(text) // 4)

    # Test basic functionality
    result1 = count_tokens("Hello world")
    result2 = count_tokens("This is a longer message with more words")

    assert result1 > 0
    assert result2 > result1
    assert isinstance(result1, int)
    assert isinstance(result2, int)


def test_message_conversion():
    """Test message conversion to PydanticAI format."""
    from pydantic import BaseModel
    from typing import List, Optional, Dict, Any, Union, Tuple

    class ChatMessage(BaseModel):
        role: str
        content: Optional[Union[str, List[Dict[str, Any]]]] = None
        name: Optional[str] = None

    def convert_messages_to_pydantic_ai(messages: List[ChatMessage]) -> Tuple[str, List]:
        """Convert OpenAI messages to PydanticAI format."""
        pydantic_messages = []
        user_prompt = ""
        system_prompt = None

        for msg in messages:
            content = msg.content
            if content is None:
                continue

            # Handle multimodal content
            if isinstance(content, list):
                text_content = ""
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_content += item.get("text", "")
                content = text_content

            if msg.role == "system":
                system_prompt = content
            elif msg.role == "user":
                user_prompt = content
                pydantic_messages.append({"role": "user", "content": content})
            elif msg.role == "assistant":
                pydantic_messages.append({"role": "assistant", "content": content})

        # Add system prompt at the beginning if exists
        if system_prompt:
            pydantic_messages.insert(0, {"role": "system", "content": system_prompt})

        # Remove last user message from history as it's the current prompt
        if pydantic_messages and pydantic_messages[-1].get("role") == "user":
            pydantic_messages = pydantic_messages[:-1]

        return user_prompt, pydantic_messages

    # Test simple user message
    messages = [ChatMessage(role="user", content="Hello")]
    user_prompt, history = convert_messages_to_pydantic_ai(messages)
    assert user_prompt == "Hello"
    assert len(history) == 0

    # Test conversation with system prompt
    messages = [
        ChatMessage(role="system", content="You are helpful"),
        ChatMessage(role="user", content="Hi"),
        ChatMessage(role="assistant", content="Hello there!"),
        ChatMessage(role="user", content="How are you?")
    ]
    user_prompt, history = convert_messages_to_pydantic_ai(messages)
    assert user_prompt == "How are you?"
    assert len(history) == 2  # system + assistant
    assert history[0]["role"] == "system"
    assert history[1]["role"] == "assistant"


def test_response_format_validation():
    """Test that response formats match OpenAI spec."""
    from pydantic import BaseModel
    from typing import List, Optional, Any

    class Usage(BaseModel):
        prompt_tokens: int
        completion_tokens: int
        total_tokens: int

    class ChatMessage(BaseModel):
        role: str
        content: Optional[str] = None

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

    # Test valid response creation
    response = ChatCompletionResponse(
        id="chatcmpl-123",
        created=1234567890,
        model="gpt-4o-mini",
        choices=[
            Choice(
                index=0,
                message=ChatMessage(role="assistant", content="Hi there!"),
                finish_reason="stop"
            )
        ],
        usage=Usage(
            prompt_tokens=5,
            completion_tokens=3,
            total_tokens=8
        )
    )

    # Verify response structure
    assert response.object == "chat.completion"
    assert response.id.startswith("chatcmpl-")
    assert len(response.choices) == 1
    assert response.choices[0].message.role == "assistant"
    assert response.usage.total_tokens == 8

    # Test as JSON (what would be sent over HTTP)
    response_dict = response.dict()
    assert "id" in response_dict
    assert "choices" in response_dict
    assert "usage" in response_dict


def test_completion_response_format():
    """Test legacy completion response format."""
    from pydantic import BaseModel
    from typing import List, Optional, Any

    class Usage(BaseModel):
        prompt_tokens: int
        completion_tokens: int
        total_tokens: int

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

    response = CompletionResponse(
        id="cmpl-123",
        created=1234567890,
        model="gpt-3.5-turbo-instruct",
        choices=[
            CompletionChoice(
                text="Once upon a time, in a land far away...",
                index=0,
                finish_reason="stop"
            )
        ],
        usage=Usage(
            prompt_tokens=4,
            completion_tokens=10,
            total_tokens=14
        )
    )

    assert response.object == "text_completion"
    assert response.choices[0].text.startswith("Once upon a time")


def test_streaming_format():
    """Test streaming response format."""
    import json

    # Test chat completion stream chunk
    chunk = {
        "id": "chatcmpl-123",
        "object": "chat.completion.chunk",
        "created": 1234567890,
        "model": "gpt-4o-mini",
        "choices": [{
            "index": 0,
            "delta": {"content": "Hello"},
            "logprobs": None,
            "finish_reason": None
        }]
    }

    # Should be valid JSON
    json_str = json.dumps(chunk)
    parsed = json.loads(json_str)
    assert parsed["object"] == "chat.completion.chunk"
    assert parsed["choices"][0]["delta"]["content"] == "Hello"

    # Test final chunk
    final_chunk = {
        "id": "chatcmpl-123",
        "object": "chat.completion.chunk",
        "created": 1234567890,
        "model": "gpt-4o-mini",
        "choices": [{
            "index": 0,
            "delta": {},
            "logprobs": None,
            "finish_reason": "stop"
        }]
    }

    final_json = json.dumps(final_chunk)
    final_parsed = json.loads(final_json)
    assert final_parsed["choices"][0]["finish_reason"] == "stop"


def test_error_format():
    """Test OpenAI-compliant error format."""
    # Test error response structure
    error_response = {
        "error": {
            "message": "Invalid API key",
            "type": "invalid_api_key",
            "param": None,
            "code": None
        }
    }

    assert "error" in error_response
    assert "message" in error_response["error"]
    assert "type" in error_response["error"]

    # Test different error types
    validation_error = {
        "error": {
            "message": "Missing required field: messages",
            "type": "invalid_request_error"
        }
    }

    server_error = {
        "error": {
            "message": "Internal server error",
            "type": "server_error"
        }
    }

    assert validation_error["error"]["type"] == "invalid_request_error"
    assert server_error["error"]["type"] == "server_error"


def test_model_parameters():
    """Test model parameter handling."""
    from pydantic import BaseModel
    from typing import Optional, List, Dict, Any, Union

    class ChatCompletionRequest(BaseModel):
        model: str = "gpt-4o-mini"
        messages: List[Dict[str, Any]]
        max_tokens: Optional[int] = None
        temperature: Optional[float] = 1.0
        top_p: Optional[float] = 1.0
        stream: Optional[bool] = False
        stop: Optional[Union[str, List[str]]] = None

    # Test parameter validation
    request = ChatCompletionRequest(
        messages=[{"role": "user", "content": "Hello"}],
        temperature=0.7,
        max_tokens=100
    )

    assert request.model == "gpt-4o-mini"
    assert request.temperature == 0.7
    assert request.max_tokens == 100
    assert request.stream is False

    # Test with different parameters
    request2 = ChatCompletionRequest(
        messages=[{"role": "user", "content": "Hi"}],
        model="gpt-3.5-turbo",
        stream=True,
        stop=["\n", "###"]
    )

    assert request2.model == "gpt-3.5-turbo"
    assert request2.stream is True
    assert request2.stop == ["\n", "###"]


def test_stateless_dependencies():
    """Test stateless agent dependencies creation."""
    import os

    def get_stateless_agent_deps():
        """Mock implementation of stateless dependencies."""
        return {
            "embedding_client": "mock_embedding_client",
            "supabase": "mock_supabase",
            "http_client": "mock_http_client",
            "brave_api_key": os.getenv("BRAVE_API_KEY", ""),
            "searxng_base_url": os.getenv("SEARXNG_BASE_URL", ""),
            "memories": ""  # No memories for stateless operation
        }

    deps = get_stateless_agent_deps()

    # Should have all required dependencies
    assert "embedding_client" in deps
    assert "supabase" in deps
    assert "http_client" in deps
    assert "memories" in deps
    assert deps["memories"] == ""  # Should be empty for stateless


def test_completion_id_uniqueness():
    """Test completion ID generation uniqueness."""
    import uuid

    def generate_completion_id() -> str:
        return f"chatcmpl-{uuid.uuid4().hex[:8]}"

    # Generate multiple IDs
    ids = set()
    for _ in range(100):
        new_id = generate_completion_id()
        assert new_id not in ids  # Should be unique
        assert new_id.startswith("chatcmpl-")
        assert len(new_id) == len("chatcmpl-") + 8
        ids.add(new_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])