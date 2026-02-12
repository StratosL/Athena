"""Hierarchical RAG agent with native OpenRouter.

Reference: examples/agent.py - Adapted for hierarchical retrieval.
"""

from typing import Optional

from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel

from .dependencies import AgentDependencies
from .prompts import HIERARCHICAL_RAG_SYSTEM_PROMPT


# Default model name (can be overridden via settings)
DEFAULT_MODEL = "anthropic/claude-haiku-4.5"

# Agent instance - created lazily
_rag_agent: Optional[Agent] = None


def create_rag_agent(model_name: Optional[str] = None) -> Agent:
    """Create a new RAG agent instance.

    Args:
        model_name: OpenRouter model name. If None, uses settings or default.

    Returns:
        Configured Agent instance.
    """
    if model_name is None:
        try:
            from ..settings import load_settings
            model_name = load_settings().llm_model
        except Exception:
            model_name = DEFAULT_MODEL

    agent = Agent(
        OpenRouterModel(model_name),
        deps_type=AgentDependencies,
        system_prompt=HIERARCHICAL_RAG_SYSTEM_PROMPT
    )

    return agent


def get_rag_agent() -> Agent:
    """Get the shared RAG agent instance (lazy initialization).

    Returns:
        The shared RAG agent instance with tools registered.
    """
    global _rag_agent
    if _rag_agent is None:
        _rag_agent = create_rag_agent()
        # Register tools after creation
        from .tools import register_tools
        register_tools(_rag_agent)
    return _rag_agent


# Export
__all__ = ["create_rag_agent", "get_rag_agent"]
