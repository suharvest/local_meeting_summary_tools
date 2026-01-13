"""Google Gemini LLM Provider implementation."""
import google.generativeai as genai
from typing import AsyncGenerator, Optional

from .base import BaseLLMProvider, LLMResponse


class GeminiProvider(BaseLLMProvider):
    """Google Gemini API provider.

    Uses the google-generativeai SDK for Gemini Flash and other models.
    """

    def __init__(self, config: dict):
        super().__init__(config)
        genai.configure(api_key=config["api_key"])
        self.model = genai.GenerativeModel(
            config.get("model", "gemini-1.5-flash")
        )

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> LLMResponse:
        """Generate a complete response using Gemini."""
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        response = await self.model.generate_content_async(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
        )

        return LLMResponse(
            content=response.text,
            tokens_used=response.usage_metadata.total_token_count if response.usage_metadata else 0,
            model=self.get_model_name(),
            finish_reason=response.candidates[0].finish_reason.name if response.candidates else "unknown"
        )

    async def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> AsyncGenerator[str, None]:
        """Stream generate response chunks using Gemini."""
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        response = await self.model.generate_content_async(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            ),
            stream=True
        )

        async for chunk in response:
            if chunk.text:
                yield chunk.text

    async def is_available(self) -> bool:
        """Check if Gemini API is available."""
        try:
            # Simple availability check with minimal request
            response = await self.model.generate_content_async(
                "Hi",
                generation_config=genai.types.GenerationConfig(max_output_tokens=10)
            )
            return True
        except Exception:
            return False
