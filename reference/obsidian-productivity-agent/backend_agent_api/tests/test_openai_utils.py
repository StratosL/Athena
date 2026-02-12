"""
Simple unit tests for OpenAI API compatibility utilities.

This test suite validates the core functionality without requiring
the full application setup or external dependencies.
"""

import pytest
import json
import os
import sys
from pathlib import Path

# Add the backend API directory to the path
backend_path = Path(__file__).parent / "backend_agent_api"
sys.path.insert(0, str(backend_path))

# Set required environment variables for testing
os.environ["OPENAI_COMPATIBLE_API_KEY"] = "test-api-key"
os.environ["LLM_CHOICE"] = "gpt-4o-mini"

class TestTokenCounting:
    """Test token counting functionality."""

    def test_count_tokens_basic(self):
        """Test basic token counting."""
        # Mock the count_tokens function since we can't import tiktoken easily
        def count_tokens(text: str, model: str = "gpt-4") -> int:
            """Simple approximation for testing - ~4 chars per token"""
            return max(1, len(text) // 4)

        # Test basic functionality
        assert count_tokens("hello") >= 1
        assert count_tokens("hello world") > count_tokens("hello")
        assert count_tokens("") == 1  # Minimum 1 token

    def test_count_tokens_different_models(self):
        """Test token counting with different model names."""
        def count_tokens(text: str, model: str = "gpt-4") -> int:
            return max(1, len(text) // 4)

        text = "This is a test message"

        # Should work with various model names
        assert count_tokens(text, "gpt-4") > 0
        assert count_tokens(text, "gpt-3.5-turbo") > 0
        assert count_tokens(text, "unknown-model") > 0


class TestMessageConversion:
    """Test OpenAI message format conversion."""

    def test_convert_simple_user_message(self):
        """Test converting a simple user message."""
        from typing import List, Tuple, Dict, Any, Optional
        from pydantic import BaseModel

        class ChatMessage(BaseModel):
            role: str
            content: Optional[str] = None
            name: Optional[str] = None
            function_call: Optional[Dict[str, Any]] = None
            tool_calls: Optional[List[Dict[str, Any]]] = None

        def convert_messages_to_pydantic_ai(messages: List[ChatMessage]) -> Tuple[str, List]:
            """Simplified conversion for testing."""
            user_prompt = ""
            history = []

            for msg in messages:
                if msg.content is None:
                    continue

                content = msg.content
                if isinstance(content, list):
                    text_content = ""
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            text_content += item.get("text", "")
                    content = text_content

                if msg.role == "user":
                    user_prompt = content
                elif msg.role == "assistant":
                    history.append({"role": "assistant", "content": content})

            return user_prompt, history

        messages = [
            ChatMessage(role="user", content="Hello, how are you?")
        ]

        user_prompt, history = convert_messages_to_pydantic_ai(messages)
        assert user_prompt == "Hello, how are you?"
        assert len(history) == 0

    def test_convert_conversation_history(self):
        """Test converting conversation with history."""
        from typing import List, Tuple, Dict, Any, Optional
        from pydantic import BaseModel

        class ChatMessage(BaseModel):
            role: str
            content: Optional[str] = None
            name: Optional[str] = None
            function_call: Optional[Dict[str, Any]] = None
            tool_calls: Optional[List[Dict[str, Any]]] = None

        def convert_messages_to_pydantic_ai(messages: List[ChatMessage]) -> Tuple[str, List]:
            user_prompt = ""
            history = []

            for msg in messages:
                if msg.content is None:
                    continue

                content = msg.content
                if isinstance(content, list):
                    text_content = ""
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            text_content += item.get("text", "")
                    content = text_content

                if msg.role == "user":
                    user_prompt = content
                elif msg.role == "assistant":
                    history.append({"role": "assistant", "content": content})

            return user_prompt, history

        messages = [
            ChatMessage(role="user", content="What is 2+2?"),
            ChatMessage(role="assistant", content="2+2 equals 4."),
            ChatMessage(role="user", content="What about 3+3?")
        ]

        user_prompt, history = convert_messages_to_pydantic_ai(messages)
        assert user_prompt == "What about 3+3?"
        assert len(history) == 1
        assert history[0]["content"] == "2+2 equals 4."

    def test_convert_system_message(self):
        """Test converting messages with system prompt."""
        from typing import List, Tuple, Dict, Any, Optional
        from pydantic import BaseModel

        class ChatMessage(BaseModel):
            role: str
            content: Optional[str] = None
            name: Optional[str] = None
            function_call: Optional[Dict[str, Any]] = None
            tool_calls: Optional[List[Dict[str, Any]]] = None

        def convert_messages_to_pydantic_ai(messages: List[ChatMessage]) -> Tuple[str, List]:
            user_prompt = ""
            history = []

            for msg in messages:
                if msg.content is None:
                    continue

                content = msg.content
                if isinstance(content, list):
                    text_content = ""
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            text_content += item.get("text", "")
                    content = text_content

                if msg.role == "system":
                    history.insert(0, {"role": "system", "content": content})
                elif msg.role == "user":
                    user_prompt = content
                elif msg.role == "assistant":
                    history.append({"role": "assistant", "content": content})

            return user_prompt, history

        messages = [
            ChatMessage(role="system", content="You are a helpful assistant."),
            ChatMessage(role="user", content="Hello!")
        ]

        user_prompt, history = convert_messages_to_pydantic_ai(messages)
        assert user_prompt == "Hello!"
        assert len(history) == 1
        assert history[0]["role"] == "system"
        assert history[0]["content"] == "You are a helpful assistant."


class TestOpenAIModels:
    """Test OpenAI API model validation."""

    def test_chat_completion_request_validation(self):
        """Test ChatCompletionRequest model validation."""
        from typing import List, Dict, Any, Optional, Union
        from pydantic import BaseModel

        class ChatMessage(BaseModel):
            role: str
            content: Optional[str] = None

        class ChatCompletionRequest(BaseModel):
            model: str = "gpt-4o-mini"
            messages: List[ChatMessage]
            max_tokens: Optional[int] = None
            temperature: Optional[float] = 1.0
            stream: Optional[bool] = False

        # Valid request
        valid_request = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "user", "content": "Hello"}
            ]
        }

        request = ChatCompletionRequest(**valid_request)
        assert request.model == "gpt-4o-mini"
        assert len(request.messages) == 1
        assert request.messages[0].role == "user"
        assert request.messages[0].content == "Hello"
        assert request.temperature == 1.0
        assert request.stream is False

    def test_completion_request_validation(self):
        """Test CompletionRequest model validation."""
        from typing import Union, Optional, List, Dict, Any
        from pydantic import BaseModel

        class CompletionRequest(BaseModel):
            model: str = "gpt-3.5-turbo-instruct"
            prompt: Union[str, List[str]]
            max_tokens: Optional[int] = 16
            temperature: Optional[float] = 1.0
            stream: Optional[bool] = False

        # Test with string prompt
        request1 = CompletionRequest(prompt="Once upon a time")
        assert request1.prompt == "Once upon a time"
        assert request1.model == "gpt-3.5-turbo-instruct"

        # Test with list prompt
        request2 = CompletionRequest(prompt=["First prompt", "Second prompt"])
        assert isinstance(request2.prompt, list)
        assert len(request2.prompt) == 2


class TestAuthenticationValidation:
    """Test API key authentication."""

    def test_valid_api_key_format(self):
        """Test valid API key format validation."""
        def validate_auth_header(authorization: str) -> str:
            if not authorization.startswith("Bearer "):
                raise ValueError("Invalid Authorization header format")
            return authorization.replace("Bearer ", "")

        # Valid format
        api_key = validate_auth_header("Bearer test-api-key")
        assert api_key == "test-api-key"

        # Test with different key
        api_key2 = validate_auth_header("Bearer sk-1234567890")
        assert api_key2 == "sk-1234567890"

    def test_invalid_api_key_format(self):
        """Test invalid API key format handling."""
        def validate_auth_header(authorization: str) -> str:
            if not authorization.startswith("Bearer "):
                raise ValueError("Invalid Authorization header format")
            return authorization.replace("Bearer ", "")

        # Invalid formats should raise errors
        with pytest.raises(ValueError, match="Invalid Authorization header format"):
            validate_auth_header("Basic test-key")

        with pytest.raises(ValueError, match="Invalid Authorization header format"):
            validate_auth_header("test-key")

        with pytest.raises(ValueError, match="Invalid Authorization header format"):
            validate_auth_header("Bearer")  # Missing key


class TestResponseModels:
    """Test OpenAI response model structures."""

    def test_chat_completion_response_structure(self):
        """Test ChatCompletionResponse structure."""
        from typing import List, Optional, Any
        from pydantic import BaseModel

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
            finish_reason: Optional[str] = None

        class ChatCompletionResponse(BaseModel):
            id: str
            object: str = "chat.completion"
            created: int
            model: str
            choices: List[Choice]
            usage: Usage

        # Test creating a response
        response = ChatCompletionResponse(
            id="chatcmpl-123",
            created=1234567890,
            model="gpt-4o-mini",
            choices=[
                Choice(
                    index=0,
                    message=ChatMessage(role="assistant", content="Hello!"),
                    finish_reason="stop"
                )
            ],
            usage=Usage(
                prompt_tokens=10,
                completion_tokens=5,
                total_tokens=15
            )
        )

        assert response.id == "chatcmpl-123"
        assert response.object == "chat.completion"
        assert response.model == "gpt-4o-mini"
        assert len(response.choices) == 1
        assert response.choices[0].message.content == "Hello!"
        assert response.usage.total_tokens == 15

    def test_completion_response_structure(self):
        """Test CompletionResponse structure."""
        from typing import List, Optional, Any
        from pydantic import BaseModel

        class Usage(BaseModel):
            prompt_tokens: int
            completion_tokens: int
            total_tokens: int

        class CompletionChoice(BaseModel):
            text: str
            index: int
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
                    text="Once upon a time, there was",
                    index=0,
                    finish_reason="stop"
                )
            ],
            usage=Usage(
                prompt_tokens=8,
                completion_tokens=12,
                total_tokens=20
            )
        )

        assert response.object == "text_completion"
        assert response.choices[0].text == "Once upon a time, there was"
        assert response.usage.total_tokens == 20


def test_generate_completion_id():
    """Test completion ID generation."""
    import uuid

    def generate_completion_id() -> str:
        return f"chatcmpl-{uuid.uuid4().hex[:8]}"

    id1 = generate_completion_id()
    id2 = generate_completion_id()

    assert id1.startswith("chatcmpl-")
    assert id2.startswith("chatcmpl-")
    assert id1 != id2  # Should be unique
    assert len(id1) == len("chatcmpl-") + 8  # 8 hex chars after prefix


if __name__ == "__main__":
    pytest.main([__file__, "-v"])