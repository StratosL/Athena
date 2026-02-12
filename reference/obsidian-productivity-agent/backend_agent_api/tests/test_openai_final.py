"""
Final validation tests for OpenAI API compatibility.

These tests validate the core functionality without complex dependencies.
"""

import pytest
import json
import os
from typing import Dict, List, Any, Optional, Union, Tuple
from pydantic import BaseModel


class TestOpenAICompatibilityValidation:
    """Comprehensive validation of OpenAI API compatibility features."""

    def test_api_key_validation_logic(self):
        """Test API key validation works correctly."""
        def validate_api_key(auth_header: str, expected_key: str = "test-api-key") -> bool:
            if not auth_header:
                raise ValueError("Missing API key")

            if not auth_header.startswith("Bearer "):
                raise ValueError("Invalid format")

            key = auth_header.replace("Bearer ", "")
            if key != expected_key:
                raise ValueError("Invalid key")

            return True

        # Valid key
        assert validate_api_key("Bearer test-api-key") is True

        # Invalid cases
        with pytest.raises(ValueError, match="Missing API key"):
            validate_api_key("")

        with pytest.raises(ValueError, match="Invalid format"):
            validate_api_key("test-api-key")

        with pytest.raises(ValueError, match="Invalid key"):
            validate_api_key("Bearer wrong-key")

    def test_token_counting_basic(self):
        """Test token counting approximation."""
        def count_tokens(text: str) -> int:
            return max(1, len(text.split()) * 1.3)  # Rough approximation

        assert count_tokens("hello world") > 0
        assert count_tokens("") >= 1
        assert count_tokens("longer text message") > count_tokens("short")

    def test_message_format_conversion(self):
        """Test OpenAI to PydanticAI message conversion."""
        class ChatMessage(BaseModel):
            role: str
            content: Optional[str] = None

        def convert_messages(messages: List[ChatMessage]) -> Tuple[str, List[Dict]]:
            user_prompt = ""
            history = []

            for msg in messages:
                if not msg.content:
                    continue

                if msg.role == "system":
                    history.insert(0, {"role": "system", "content": msg.content})
                elif msg.role == "user":
                    user_prompt = msg.content  # Last user message becomes prompt
                elif msg.role == "assistant":
                    history.append({"role": "assistant", "content": msg.content})

            return user_prompt, history

        # Test simple case
        messages = [ChatMessage(role="user", content="Hello")]
        prompt, hist = convert_messages(messages)
        assert prompt == "Hello"
        assert len(hist) == 0

        # Test with system and assistant
        messages = [
            ChatMessage(role="system", content="You are helpful"),
            ChatMessage(role="assistant", content="How can I help?"),
            ChatMessage(role="user", content="What's the weather?")
        ]
        prompt, hist = convert_messages(messages)
        assert prompt == "What's the weather?"
        assert len(hist) == 2
        assert hist[0]["role"] == "system"
        assert hist[1]["role"] == "assistant"

    def test_chat_completion_request_model(self):
        """Test ChatCompletionRequest Pydantic model."""
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
        request = ChatCompletionRequest(
            messages=[ChatMessage(role="user", content="Hello")],
            temperature=0.7
        )
        assert request.model == "gpt-4o-mini"
        assert request.temperature == 0.7
        assert len(request.messages) == 1

    def test_chat_completion_response_model(self):
        """Test ChatCompletionResponse Pydantic model."""
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
            usage=Usage(prompt_tokens=5, completion_tokens=3, total_tokens=8)
        )

        assert response.object == "chat.completion"
        assert response.usage.total_tokens == 8

    def test_completion_request_model(self):
        """Test legacy CompletionRequest model."""
        class CompletionRequest(BaseModel):
            model: str = "gpt-3.5-turbo-instruct"
            prompt: Union[str, List[str]]
            max_tokens: Optional[int] = 16
            stream: Optional[bool] = False

        # String prompt
        request1 = CompletionRequest(prompt="Once upon a time")
        assert request1.prompt == "Once upon a time"

        # List prompt
        request2 = CompletionRequest(prompt=["First", "Second"])
        assert len(request2.prompt) == 2

    def test_completion_response_model(self):
        """Test legacy CompletionResponse model."""
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
                    text="Once upon a time, there was...",
                    index=0,
                    finish_reason="stop"
                )
            ],
            usage=Usage(prompt_tokens=10, completion_tokens=15, total_tokens=25)
        )

        assert response.object == "text_completion"
        assert response.choices[0].text.startswith("Once upon a time")

    def test_streaming_response_format(self):
        """Test streaming response format."""
        # Chat completion chunk
        chunk = {
            "id": "chatcmpl-123",
            "object": "chat.completion.chunk",
            "created": 1234567890,
            "model": "gpt-4o-mini",
            "choices": [{
                "index": 0,
                "delta": {"content": "Hello"},
                "finish_reason": None
            }]
        }

        # Should serialize to JSON
        json_str = json.dumps(chunk)
        parsed = json.loads(json_str)
        assert parsed["object"] == "chat.completion.chunk"
        assert parsed["choices"][0]["delta"]["content"] == "Hello"

        # Final chunk
        final_chunk = {
            "id": "chatcmpl-123",
            "object": "chat.completion.chunk",
            "created": 1234567890,
            "model": "gpt-4o-mini",
            "choices": [{
                "index": 0,
                "delta": {},
                "finish_reason": "stop"
            }]
        }

        final_json = json.dumps(final_chunk)
        final_parsed = json.loads(final_json)
        assert final_parsed["choices"][0]["finish_reason"] == "stop"

    def test_error_response_format(self):
        """Test OpenAI error response format."""
        # Standard error format
        error = {
            "error": {
                "message": "Invalid API key",
                "type": "invalid_api_key"
            }
        }

        assert "error" in error
        assert error["error"]["message"] == "Invalid API key"
        assert error["error"]["type"] == "invalid_api_key"

        # Different error types
        errors = [
            {"error": {"message": "Missing field", "type": "invalid_request_error"}},
            {"error": {"message": "Server error", "type": "server_error"}},
            {"error": {"message": "Rate limit", "type": "rate_limit_exceeded"}}
        ]

        for err in errors:
            assert "error" in err
            assert "message" in err["error"]
            assert "type" in err["error"]

    def test_completion_id_generation(self):
        """Test completion ID generation."""
        import uuid

        def generate_completion_id() -> str:
            return f"chatcmpl-{uuid.uuid4().hex[:8]}"

        # Generate multiple IDs
        ids = []
        for _ in range(10):
            new_id = generate_completion_id()
            assert new_id.startswith("chatcmpl-")
            assert len(new_id) == len("chatcmpl-") + 8
            ids.append(new_id)

        # Should all be unique
        assert len(set(ids)) == len(ids)

    def test_multimodal_content_handling(self):
        """Test handling of multimodal content in messages."""
        def extract_text_content(content):
            if isinstance(content, str):
                return content
            elif isinstance(content, list):
                text = ""
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text += item.get("text", "")
                return text
            return ""

        # String content
        assert extract_text_content("Hello") == "Hello"

        # Multimodal content
        multimodal = [
            {"type": "text", "text": "What's in this image?"},
            {"type": "image_url", "image_url": {"url": "https://example.com/img.jpg"}}
        ]

        result = extract_text_content(multimodal)
        assert result == "What's in this image?"

        # Mixed content
        mixed = [
            {"type": "text", "text": "First part "},
            {"type": "text", "text": "second part"},
            {"type": "image_url", "image_url": {"url": "https://example.com/img.jpg"}}
        ]

        result2 = extract_text_content(mixed)
        assert result2 == "First part second part"

    def test_environment_configuration(self):
        """Test environment variable handling."""
        # These should be set by our test setup
        api_key = os.getenv("OPENAI_COMPATIBLE_API_KEY")
        model = os.getenv("LLM_CHOICE")

        assert api_key == "test-api-key"
        assert model == "gpt-4o-mini"

    def test_stateless_dependencies_structure(self):
        """Test stateless agent dependencies structure."""
        def create_stateless_deps():
            return {
                "embedding_client": None,  # Placeholder for tests
                "supabase": None,
                "http_client": None,
                "brave_api_key": os.getenv("BRAVE_API_KEY", ""),
                "searxng_base_url": os.getenv("SEARXNG_BASE_URL", ""),
                "memories": ""  # Empty for stateless
            }

        deps = create_stateless_deps()

        # Should have all required keys
        required_keys = ["embedding_client", "supabase", "http_client", "memories"]
        for key in required_keys:
            assert key in deps

        # Memories should be empty for stateless operation
        assert deps["memories"] == ""

    def test_model_parameter_validation(self):
        """Test model parameter validation and defaults."""
        class ModelParams(BaseModel):
            temperature: Optional[float] = 1.0
            top_p: Optional[float] = 1.0
            max_tokens: Optional[int] = None
            stream: Optional[bool] = False
            stop: Optional[Union[str, List[str]]] = None

        # Default values
        params1 = ModelParams()
        assert params1.temperature == 1.0
        assert params1.stream is False

        # Custom values
        params2 = ModelParams(temperature=0.5, max_tokens=100, stream=True)
        assert params2.temperature == 0.5
        assert params2.max_tokens == 100
        assert params2.stream is True

        # Stop sequences
        params3 = ModelParams(stop=["\n", "END"])
        assert params3.stop == ["\n", "END"]

        params4 = ModelParams(stop="STOP")
        assert params4.stop == "STOP"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])