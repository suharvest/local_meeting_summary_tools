"""LLM Provider Factory for creating and managing LLM instances."""
from typing import Dict, Type, Optional, List

from .base import BaseLLMProvider
from .gemini import GeminiProvider
from .qwen import QwenProvider
from .ollama import OllamaProvider


class LLMFactory:
    """Factory for creating and managing LLM provider instances.

    Supports multiple providers and implements singleton pattern for each provider.
    """

    _providers: Dict[str, Type[BaseLLMProvider]] = {
        "gemini": GeminiProvider,
        "qwen": QwenProvider,
        "ollama": OllamaProvider,
    }

    _instances: Dict[str, BaseLLMProvider] = {}

    def __init__(self, config: dict):
        """Initialize the factory with LLM configuration.

        Args:
            config: LLM configuration containing provider settings
        """
        self.config = config
        self.default_provider = config.get("default_provider", "gemini")

    def get_provider(self, name: Optional[str] = None) -> BaseLLMProvider:
        """Get an LLM provider instance by name.

        Args:
            name: Provider name (gemini, qwen, ollama). Uses default if not specified.

        Returns:
            LLM provider instance

        Raises:
            ValueError: If provider name is unknown
        """
        provider_name = name or self.default_provider

        if provider_name not in self._instances:
            if provider_name not in self._providers:
                raise ValueError(f"Unknown LLM provider: {provider_name}")

            provider_config = self.config.get("providers", {}).get(provider_name, {})
            provider_class = self._providers[provider_name]
            self._instances[provider_name] = provider_class(provider_config)

        return self._instances[provider_name]

    def list_providers(self) -> List[str]:
        """List all registered provider names."""
        return list(self._providers.keys())

    async def get_available_providers(self) -> List[str]:
        """Get list of currently available (operational) providers."""
        available = []
        for name in self._providers:
            try:
                provider = self.get_provider(name)
                if await provider.is_available():
                    available.append(name)
            except Exception:
                continue
        return available

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[BaseLLMProvider]):
        """Register a new LLM provider type.

        Args:
            name: Provider name to register
            provider_class: Provider class implementing BaseLLMProvider
        """
        cls._providers[name] = provider_class


# Global factory instance (will be initialized in main.py)
llm_factory: Optional[LLMFactory] = None


def get_llm_factory() -> LLMFactory:
    """Dependency for FastAPI to get LLM factory instance."""
    if llm_factory is None:
        raise RuntimeError("LLM Factory not initialized")
    return llm_factory
