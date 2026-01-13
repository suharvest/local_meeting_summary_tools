"""Abstract base class for LLM providers."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncGenerator, Optional


@dataclass
class LLMResponse:
    """Response from LLM generation."""

    content: str
    tokens_used: int
    model: str
    finish_reason: str


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers.

    All LLM providers (Gemini, Qwen, Ollama, TensorRT) must implement this interface.
    """

    def __init__(self, config: dict):
        self.config = config
        self.name = self.__class__.__name__.replace("Provider", "").lower()

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> LLMResponse:
        """Generate a complete response synchronously.

        Args:
            prompt: The user prompt/input text
            system_prompt: Optional system prompt for context
            temperature: Sampling temperature (0.0 - 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            LLMResponse with generated content
        """
        pass

    @abstractmethod
    async def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> AsyncGenerator[str, None]:
        """Generate response with streaming output.

        Args:
            prompt: The user prompt/input text
            system_prompt: Optional system prompt for context
            temperature: Sampling temperature (0.0 - 1.0)
            max_tokens: Maximum tokens to generate

        Yields:
            Text chunks as they are generated
        """
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the LLM service is available.

        Returns:
            True if service is reachable and operational
        """
        pass

    def get_model_name(self) -> str:
        """Get the current model name from config."""
        return self.config.get("model", "unknown")
