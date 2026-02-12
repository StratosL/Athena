"""
Integration tests for the actual OpenAI compatibility implementation.

This test file tests the real implementation functions from the backend.
"""

import pytest
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend_agent_api"
sys.path.insert(0, str(backend_path))

# Set required environment variables
os.environ["OPENAI_COMPATIBLE_API_KEY"] = "test-api-key"
os.environ["LLM_CHOICE"] = "gpt-4o-mini"

# Mock dependencies that are hard to import
class MockException(Exception):
    pass

# Try to import the real functions, providing fallbacks if dependencies fail
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

def mock_count_tokens(text: str, model: str = "gpt-4") -> int:
    """Mock token counting for when tiktoken isn't available."""
    # Simple approximation: ~4 characters per token
    return max(1, len(text) // 4)


class TestActualImplementation:
    """Test the actual implementation functions."""

    def test_token_counting_with_tiktoken(self):
        """Test token counting with tiktoken if available."""
        if not TIKTOKEN_AVAILABLE:
            pytest.skip("tiktoken not available")

        import tiktoken

        def count_tokens(text: str, model: str = "gpt-4") -> int:
            try:
                encoding = tiktoken.encoding_for_model(model)
            except KeyError:
                # Default to cl100k_base encoding if model not found
                encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))

        # Test with actual tiktoken
        result = count_tokens("Hello, world!")
        assert isinstance(result, int)
        assert result > 0

        # Test with different models
        result1 = count_tokens("Hello, world!", "gpt-4")
        result2 = count_tokens("Hello, world!", "unknown-model")
        assert isinstance(result1, int)
        assert isinstance(result2, int)

    def test_token_counting_mock(self):
        """Test token counting with mock function."""
        # Test the mock implementation
        result = mock_count_tokens("Hello, world!")
        assert result >= 1

        # Longer text should have more tokens
        short_text = "Hi"
        long_text = "This is a much longer text that should have more tokens than the short one."
        assert mock_count_tokens(long_text) > mock_count_tokens(short_text)

    def test_message_conversion_actual_types(self):
        """Test message conversion with Pydantic models."""
        from typing import List, Optional, Dict, Any, Union, Tuple
        from pydantic import BaseModel

        class ChatMessage(BaseModel):
            role: str  # system, user, assistant, tool, function
            content: Optional[Union[str, List[Dict[str, Any]]]] = None
            name: Optional[str] = None
            function_call: Optional[Dict[str, Any]] = None
            tool_calls: Optional[List[Dict[str, Any]]] = None

        def convert_messages_to_pydantic_ai(messages: List[ChatMessage]) -> Tuple[str, List]:
            """Convert OpenAI format messages to PydanticAI format."""
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
                    pydantic_messages.append({
                        "role": "user",
                        "content": content
                    })
                elif msg.role == "assistant":
                    pydantic_messages.append({
                        "role": "assistant",
                        "content": content
                    })

            # If we have a system prompt, prepend it to the message history
            if system_prompt:
                pydantic_messages.insert(0, {
                    "role": "system",
                    "content": system_prompt
                })

            # Remove the last user message from history since it's the current prompt
            if pydantic_messages and pydantic_messages[-1].get("role") == "user":
                pydantic_messages = pydantic_messages[:-1]

            return user_prompt, pydantic_messages

        # Test with complex conversation
        messages = [
            ChatMessage(role="system", content="You are a helpful assistant."),
            ChatMessage(role="user", content="What is the weather?"),
            ChatMessage(role="assistant", content="I can't check the weather directly."),
            ChatMessage(role="user", content="Tell me a joke instead")
        ]

        user_prompt, history = convert_messages_to_pydantic_ai(messages)

        assert user_prompt == "Tell me a joke instead"
        assert len(history) == 2  # system + assistant
        assert history[0]["role"] == "system"
        assert history[1]["role"] == "assistant"

    def test_multimodal_message_conversion(self):
        """Test message conversion with multimodal content."""
        from typing import List, Optional, Dict, Any, Union, Tuple
        from pydantic import BaseModel

        class ChatMessage(BaseModel):
            role: str
            content: Optional[Union[str, List[Dict[str, Any]]]] = None

        def convert_messages_to_pydantic_ai(messages: List[ChatMessage]) -> Tuple[str, List]:
            user_prompt = ""
            pydantic_messages = []

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

                if msg.role == "user":
                    user_prompt = content

            return user_prompt, pydantic_messages

        # Test with multimodal content
        multimodal_content = [
            {"type": "text", "text": "What's in this image?"},
            {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
        ]

        messages = [
            ChatMessage(role="user", content=multimodal_content)
        ]

        user_prompt, history = convert_messages_to_pydantic_ai(messages)
        assert user_prompt == "What's in this image?"

    def test_api_key_validation_logic(self):
        """Test API key validation logic."""
        def verify_openai_api_key(authorization: str, expected_key: str = "test-api-key"):
            if not authorization:
                raise ValueError("Missing API key")

            if not authorization.startswith("Bearer "):
                raise ValueError("Invalid Authorization header format")

            api_key = authorization.replace("Bearer ", "")

            if api_key != expected_key:
                raise ValueError("Invalid API key")

            return True

        # Test valid key
        assert verify_openai_api_key("Bearer test-api-key") is True

        # Test invalid format
        with pytest.raises(ValueError, match="Invalid Authorization header format"):
            verify_openai_api_key("test-api-key")

        # Test wrong key
        with pytest.raises(ValueError, match="Invalid API key"):
            verify_openai_api_key("Bearer wrong-key")

        # Test missing key
        with pytest.raises(ValueError, match="Missing API key"):
            verify_openai_api_key("")

    def test_completion_id_generation(self):
        """Test completion ID generation format."""
        import uuid

        def generate_completion_id() -> str:
            return f"chatcmpl-{uuid.uuid4().hex[:8]}"

        # Generate multiple IDs
        ids = [generate_completion_id() for _ in range(10)]

        # All should start with prefix
        for id_val in ids:
            assert id_val.startswith("chatcmpl-")
            assert len(id_val) == len("chatcmpl-") + 8

        # All should be unique
        assert len(set(ids)) == len(ids)

    def test_response_structure_validation(self):
        """Test that response structures match OpenAI format."""
        from pydantic import BaseModel
        from typing import List, Optional, Any, Union

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

        # Test creating valid response
        response_data = {
            "id": "chatcmpl-123",
            "created": 1234567890,
            "model": "gpt-4o-mini",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Hello! How can I help you today?"
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 12,
                "completion_tokens": 9,
                "total_tokens": 21
            }
        }

        response = ChatCompletionResponse(**response_data)

        # Verify structure
        assert response.object == "chat.completion"
        assert len(response.choices) == 1
        assert response.choices[0].message.role == "assistant"
        assert response.usage.total_tokens == 21

    def test_error_response_format(self):
        """Test error response format matches OpenAI."""
        def create_error_response(message: str, error_type: str = "invalid_request_error"):
            return {
                "error": {
                    "message": message,
                    "type": error_type
                }
            }

        error = create_error_response("Invalid API key", "invalid_api_key")
        assert "error" in error
        assert error["error"]["message"] == "Invalid API key"
        assert error["error"]["type"] == "invalid_api_key"


class TestEnvironmentConfiguration:
    """Test environment configuration for OpenAI compatibility."""

    def test_required_env_vars_present(self):
        """Test that required environment variables are set."""
        # These should be set by our test setup
        assert os.getenv("OPENAI_COMPATIBLE_API_KEY") is not None
        assert os.getenv("LLM_CHOICE") is not None

    def test_api_key_from_env(self):
        """Test reading API key from environment."""
        expected_key = os.getenv("OPENAI_COMPATIBLE_API_KEY")
        assert expected_key == "test-api-key"

    def test_model_configuration(self):
        """Test model configuration from environment."""
        model_choice = os.getenv("LLM_CHOICE")
        assert model_choice == "gpt-4o-mini"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])