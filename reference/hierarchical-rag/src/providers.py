"""Model providers for Hierarchical RAG Workshop.

Reference: examples/providers.py - BUT USE NATIVE OPENROUTER, NOT OPENAI COMPAT.

CRITICAL: This module uses Pydantic AI's native OpenRouter integration,
NOT the OpenAI compatibility mode shown in the examples.

The examples use:
    from pydantic_ai.providers.openai import OpenAIProvider
    provider = OpenAIProvider(base_url=base_url, api_key=api_key)

We use native OpenRouter:
    from pydantic_ai.models.openrouter import OpenRouterModel
"""

from pydantic_ai.models.openrouter import OpenRouterModel

from .settings import load_settings


def get_llm_model() -> OpenRouterModel:
    """Get LLM model using NATIVE OpenRouter integration.

    Pydantic AI automatically reads OPENROUTER_API_KEY from environment.
    See: https://ai.pydantic.dev/models/openrouter/

    Returns:
        OpenRouterModel configured with the model from settings.
    """
    settings = load_settings()

    # Native OpenRouter - API key is read automatically from OPENROUTER_API_KEY env var
    return OpenRouterModel(settings.llm_model)


def get_model_info() -> dict:
    """Get information about current model configuration.

    Returns:
        Dictionary with model configuration info.
    """
    settings = load_settings()
    return {
        "llm_provider": "openrouter",
        "llm_model": settings.llm_model,
        "embedding_model": settings.embedding_model,
        "embedding_dimension": settings.embedding_dimension,
    }
