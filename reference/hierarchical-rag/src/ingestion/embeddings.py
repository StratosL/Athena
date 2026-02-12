"""Embedding generation for Hierarchical RAG via OpenRouter.

Reference: examples/ingestion/embedder.py - Adapted for OpenRouter.

IMPORTANT: Uses OpenRouter's embedding API with the SAME API key as LLM.
Endpoint: https://openrouter.ai/api/v1/embeddings
Model: openai/text-embedding-3-small (1536 dimensions)
"""

import logging
from typing import List, Optional

from openai import AsyncOpenAI

from ..settings import load_settings

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generates embeddings via OpenRouter's embedding API.

    Uses the same OPENROUTER_API_KEY as the LLM - single key for everything.

    Reference: examples/ingestion/embedder.py:33-61
    """

    def __init__(self, batch_size: int = 100):
        """Initialize embedding generator.

        Args:
            batch_size: Number of texts to process in parallel.
        """
        settings = load_settings()
        self.model = settings.embedding_model  # "openai/text-embedding-3-small"
        self.batch_size = batch_size

        # Use OpenRouter's OpenAI-compatible embedding endpoint
        # Same API key as LLM - single key for everything!
        self.client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1"
        )

        # Model-specific configurations
        # Reference: examples/ingestion/embedder.py:52-56
        self.model_configs = {
            "openai/text-embedding-3-small": {"dimensions": 1536, "max_tokens": 8191},
            "openai/text-embedding-3-large": {"dimensions": 3072, "max_tokens": 8191},
            "openai/text-embedding-ada-002": {"dimensions": 1536, "max_tokens": 8191}
        }

        self.config = self.model_configs.get(
            self.model,
            {"dimensions": 1536, "max_tokens": 8191}
        )

        logger.info(f"EmbeddingGenerator initialized (model={self.model})")

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text via OpenRouter.

        Reference: examples/ingestion/embedder.py:63-82

        Args:
            text: Text to embed.

        Returns:
            Embedding vector (list of floats).
        """
        # Truncate if too long (rough estimation: 4 chars per token)
        if len(text) > self.config["max_tokens"] * 4:
            text = text[:self.config["max_tokens"] * 4]

        response = await self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding

    async def generate_embeddings_batch(
        self,
        texts: List[str],
        progress_callback: Optional[callable] = None
    ) -> List[List[float]]:
        """Generate embeddings for a batch of texts via OpenRouter.

        Reference: examples/ingestion/embedder.py:84-109

        Args:
            texts: List of texts to embed.
            progress_callback: Optional callback for progress updates.

        Returns:
            List of embedding vectors.
        """
        # Truncate texts if too long
        processed_texts = []
        for text in texts:
            if len(text) > self.config["max_tokens"] * 4:
                text = text[:self.config["max_tokens"] * 4]
            processed_texts.append(text)

        all_embeddings = []
        total_batches = (len(processed_texts) + self.batch_size - 1) // self.batch_size

        for i in range(0, len(processed_texts), self.batch_size):
            batch = processed_texts[i:i + self.batch_size]
            response = await self.client.embeddings.create(
                model=self.model,
                input=batch
            )
            all_embeddings.extend([d.embedding for d in response.data])

            # Progress callback
            current_batch = (i // self.batch_size) + 1
            if progress_callback:
                progress_callback(current_batch, total_batches)

            logger.debug(f"Embedded batch {current_batch}/{total_batches}")

        return all_embeddings

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings for this model.

        Returns:
            Embedding dimension (e.g., 1536).
        """
        return self.config["dimensions"]


def create_embedding_generator(batch_size: int = 100) -> EmbeddingGenerator:
    """Create an EmbeddingGenerator instance.

    Args:
        batch_size: Batch size for processing.

    Returns:
        EmbeddingGenerator instance.
    """
    return EmbeddingGenerator(batch_size=batch_size)
