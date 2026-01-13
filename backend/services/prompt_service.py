"""Service for loading and managing prompt templates."""
from pathlib import Path
from typing import Dict, List, Optional


# Supported languages
SUPPORTED_LANGUAGES = {
    "zh": "中文",
    "en": "English"
}

DEFAULT_LANGUAGE = "en"


class PromptService:
    """Service for loading prompt templates from files.

    Prompts are stored in the prompts/<lang>/ directory and can be edited by users.
    Supports multiple languages (zh, en).
    """

    def __init__(self, prompts_dir: Optional[str] = None, language: str = DEFAULT_LANGUAGE):
        """Initialize prompt service.

        Args:
            prompts_dir: Directory containing prompt files. Defaults to ./prompts
            language: Language code (zh, en). Defaults to zh
        """
        if prompts_dir:
            self.prompts_dir = Path(prompts_dir)
        else:
            self.prompts_dir = Path(__file__).parent.parent.parent / "prompts"

        self.language = language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
        self._cache: Dict[str, str] = {}

    def set_language(self, language: str):
        """Set the language for prompts.

        Args:
            language: Language code (zh, en)
        """
        if language in SUPPORTED_LANGUAGES:
            self.language = language
            self._cache.clear()  # Clear cache when language changes

    def load_prompt(self, filename: str, force_reload: bool = False) -> str:
        """Load a prompt template from file.

        Args:
            filename: Name of the prompt file (e.g., "meeting_summary.txt")
            force_reload: If True, reload from disk even if cached

        Returns:
            Prompt template string

        Raises:
            FileNotFoundError: If prompt file doesn't exist
        """
        cache_key = f"{self.language}:{filename}"

        if not force_reload and cache_key in self._cache:
            return self._cache[cache_key]

        # Try language-specific directory first (e.g., prompts/en/meeting_summary.txt)
        lang_specific_path = self.prompts_dir / self.language / filename

        # Fall back to root prompts directory if language-specific doesn't exist
        prompt_path = lang_specific_path if lang_specific_path.exists() else self.prompts_dir / filename

        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

        with open(prompt_path, "r", encoding="utf-8") as f:
            content = f.read().strip()

        self._cache[cache_key] = content
        return content

    def get_meeting_summary_prompt(self) -> str:
        """Get the meeting summary generation prompt."""
        return self.load_prompt("meeting_summary.txt")

    def get_key_points_prompt(self) -> str:
        """Get the key points extraction prompt."""
        return self.load_prompt("key_points.txt")

    def get_action_items_prompt(self) -> str:
        """Get the action items extraction prompt."""
        return self.load_prompt("action_items.txt")

    def clear_cache(self):
        """Clear the prompt cache to force reload on next access."""
        self._cache.clear()

    def list_prompts(self) -> list:
        """List all available prompt files."""
        if not self.prompts_dir.exists():
            return []
        return [f.name for f in self.prompts_dir.glob("*.txt")]
