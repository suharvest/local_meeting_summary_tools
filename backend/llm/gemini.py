"""Google Gemini LLM Provider implementation."""
import asyncio
import logging
import google.generativeai as genai
from typing import AsyncGenerator, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .base import BaseLLMProvider, LLMResponse

logger = logging.getLogger(__name__)

# Timeout for Gemini API calls (seconds)
API_TIMEOUT = 60


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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(Exception),
        before_sleep=lambda retry_state: logger.warning(
            f"Gemini API call failed, retrying (attempt {retry_state.attempt_number})..."
        )
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
        """Stream generate response chunks using Gemini.

        Note: Streaming doesn't use retry decorator to avoid duplicate content.
        Errors are propagated to the caller for handling.
        """
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        try:
            async with asyncio.timeout(API_TIMEOUT):
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
        except asyncio.TimeoutError:
            logger.error(f"Gemini API timeout after {API_TIMEOUT}s - check network connectivity")
            raise RuntimeError(f"Gemini API timeout - cannot connect to Google services")
        except Exception as e:
            logger.error(f"Gemini streaming error: {e}")
            raise

    async def is_available(self) -> bool:
        """Check if Gemini API is available."""
        try:
            # Simple availability check with minimal request
            response = await self.model.generate_content_async(
                "Hi",
                generation_config=genai.types.GenerationConfig(max_output_tokens=10)
            )
            return True
        except Exception as e:
            logger.warning(f"Gemini availability check failed: {e}")
            return False
