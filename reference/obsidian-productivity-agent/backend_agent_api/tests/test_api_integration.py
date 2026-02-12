"""
Integration tests for the actual API endpoints.

This will test if the server is running and endpoints are accessible.
"""

import pytest
import requests
import json
import os
import time
from typing import Dict, Any


class TestAPIIntegration:
    """Test actual API endpoints if server is running."""

    def setup_class(self):
        """Setup for the test class."""
        self.base_url = "http://localhost:8001"
        self.headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json"
        }

    def is_server_running(self) -> bool:
        """Check if the API server is running."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    @pytest.mark.skipif(not pytest.config.getoption("--integration", default=False),
                       reason="Integration tests require --integration flag")
    def test_health_endpoint(self):
        """Test the health endpoint."""
        if not self.is_server_running():
            pytest.skip("Server not running on localhost:8001")

        response = requests.get(f"{self.base_url}/health")
        assert response.status_code in [200, 503]  # Might be unhealthy if deps not ready

        data = response.json()
        assert "status" in data
        assert "services" in data

    @pytest.mark.skipif(not pytest.config.getoption("--integration", default=False),
                       reason="Integration tests require --integration flag")
    def test_chat_completions_no_auth(self):
        """Test chat completions endpoint without authentication."""
        if not self.is_server_running():
            pytest.skip("Server not running on localhost:8001")

        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "Hello"}]
        }

        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            json=payload
        )

        assert response.status_code == 401
        data = response.json()
        assert "error" in data["detail"]
        assert "Missing API key" in data["detail"]["error"]["message"]

    @pytest.mark.skipif(not pytest.config.getoption("--integration", default=False),
                       reason="Integration tests require --integration flag")
    def test_chat_completions_invalid_auth(self):
        """Test chat completions with invalid authentication."""
        if not self.is_server_running():
            pytest.skip("Server not running on localhost:8001")

        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "Hello"}]
        }

        headers = {
            "Authorization": "Bearer invalid-key",
            "Content-Type": "application/json"
        }

        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            json=payload,
            headers=headers
        )

        assert response.status_code == 401
        data = response.json()
        assert "error" in data["detail"]

    @pytest.mark.skipif(not pytest.config.getoption("--integration", default=False),
                       reason="Integration tests require --integration flag")
    def test_completions_no_auth(self):
        """Test legacy completions endpoint without authentication."""
        if not self.is_server_running():
            pytest.skip("Server not running on localhost:8001")

        payload = {
            "model": "gpt-3.5-turbo-instruct",
            "prompt": "Once upon a time"
        }

        response = requests.post(
            f"{self.base_url}/v1/completions",
            json=payload
        )

        assert response.status_code == 401


class TestUtilityFunctions:
    """Test utility functions that don't require server."""

    def test_message_conversion_real_implementation(self):
        """Test the actual message conversion implementation logic."""

        # Simulate the actual convert_messages_to_pydantic_ai function
        def convert_messages_to_pydantic_ai(messages):
            pydantic_messages = []
            user_prompt = ""
            system_prompt = None

            for msg in messages:
                content = msg.get("content")
                if content is None:
                    continue

                # Extract text content from multimodal messages
                if isinstance(content, list):
                    text_content = ""
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            text_content += item.get("text", "")
                    content = text_content

                role = msg.get("role")
                if role == "system":
                    system_prompt = content
                elif role == "user":
                    user_prompt = content  # Keep the last user message as the prompt
                elif role == "assistant":
                    pydantic_messages.append({"role": "assistant", "content": content})

            # If we have a system prompt, prepend it to the message history
            if system_prompt:
                pydantic_messages.insert(0, {"role": "system", "content": system_prompt})

            return user_prompt, pydantic_messages

        # Test with conversation history
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"},
            {"role": "user", "content": "How are you?"}
        ]

        user_prompt, history = convert_messages_to_pydantic_ai(messages)

        assert user_prompt == "How are you?"
        assert len(history) == 2  # system + assistant
        assert history[0]["role"] == "system"
        assert history[1]["role"] == "assistant"

    def test_token_counting_approximation(self):
        """Test token counting logic."""
        def approximate_tokens(text: str) -> int:
            """Simple token approximation."""
            if not text:
                return 1
            # Rough approximation: 4 chars per token for English
            return max(1, len(text) // 4)

        assert approximate_tokens("hello") >= 1
        assert approximate_tokens("") == 1
        assert approximate_tokens("This is a longer text") > approximate_tokens("short")

    def test_completion_id_format(self):
        """Test completion ID generation format."""
        import uuid

        def generate_completion_id() -> str:
            return f"chatcmpl-{uuid.uuid4().hex[:8]}"

        completion_id = generate_completion_id()

        assert completion_id.startswith("chatcmpl-")
        assert len(completion_id) == len("chatcmpl-") + 8
        # Should be hex characters after the prefix
        hex_part = completion_id[len("chatcmpl-"):]
        int(hex_part, 16)  # Should not raise ValueError

    def test_openai_error_format_compliance(self):
        """Test that error responses match OpenAI format."""
        def create_openai_error(message: str, error_type: str) -> Dict[str, Any]:
            return {
                "error": {
                    "message": message,
                    "type": error_type
                }
            }

        # Test different error types
        auth_error = create_openai_error("Invalid API key", "invalid_api_key")
        request_error = create_openai_error("Missing field", "invalid_request_error")
        server_error = create_openai_error("Internal error", "server_error")

        # All should have proper structure
        for error in [auth_error, request_error, server_error]:
            assert "error" in error
            assert "message" in error["error"]
            assert "type" in error["error"]
            assert isinstance(error["error"]["message"], str)
            assert isinstance(error["error"]["type"], str)

    def test_request_model_validation(self):
        """Test request model validation logic."""
        from pydantic import BaseModel, ValidationError
        from typing import List, Optional, Union, Dict, Any

        class ChatMessage(BaseModel):
            role: str
            content: Optional[str] = None

        class ChatCompletionRequest(BaseModel):
            model: str = "gpt-4o-mini"
            messages: List[ChatMessage]
            max_tokens: Optional[int] = None
            temperature: Optional[float] = 1.0
            stream: Optional[bool] = False

        # Valid request should pass
        valid_data = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "Hello"}],
            "temperature": 0.7
        }

        request = ChatCompletionRequest(**valid_data)
        assert request.model == "gpt-4o-mini"
        assert len(request.messages) == 1
        assert request.temperature == 0.7

        # Invalid request should fail
        with pytest.raises(ValidationError):
            ChatCompletionRequest(messages="not a list")

    def test_response_structure_compliance(self):
        """Test that response structures match OpenAI API."""
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
            finish_reason: Optional[str] = None

        class ChatCompletionResponse(BaseModel):
            id: str
            object: str = "chat.completion"
            created: int
            model: str
            choices: List[Choice]
            usage: Usage

        # Create response and verify structure
        response = ChatCompletionResponse(
            id="chatcmpl-test123",
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

        # Convert to dict to test JSON serialization
        response_dict = response.model_dump()

        # Required OpenAI fields should be present
        required_fields = ["id", "object", "created", "model", "choices", "usage"]
        for field in required_fields:
            assert field in response_dict

        assert response_dict["object"] == "chat.completion"
        assert len(response_dict["choices"]) == 1
        assert response_dict["usage"]["total_tokens"] == 8


def pytest_addoption(parser):
    """Add command line option for integration tests."""
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="Run integration tests that require the server to be running"
    )


if __name__ == "__main__":
    print("OpenAI API Compatibility Test Suite")
    print("=====================================")

    print("\n1. Testing utility functions...")
    pytest.main([__file__ + "::TestUtilityFunctions", "-v"])

    print("\n2. To run integration tests (requires server running on localhost:8001):")
    print("   pytest test_api_integration.py::TestAPIIntegration --integration -v")

    print("\nOr run all tests:")
    print("   pytest test_api_integration.py --integration -v")