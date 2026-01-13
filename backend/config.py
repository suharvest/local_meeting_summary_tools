"""Configuration loader module."""
import os
from pathlib import Path
from typing import Any
import yaml


class Config:
    """Application configuration loaded from YAML file."""

    _instance = None
    _config: dict = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """Load configuration from config.yaml file."""
        config_path = Path(__file__).parent.parent / "config.yaml"

        if not config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}\n"
                "Please copy config.example.yaml to config.yaml and fill in your credentials."
            )

        with open(config_path, "r", encoding="utf-8") as f:
            self._config = yaml.safe_load(f)

        # Expand environment variables in config values
        self._expand_env_vars(self._config)

    def _expand_env_vars(self, obj: Any) -> Any:
        """Recursively expand environment variables in config values."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                obj[key] = self._expand_env_vars(value)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                obj[i] = self._expand_env_vars(item)
        elif isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
            env_var = obj[2:-1]
            obj = os.environ.get(env_var, obj)
        return obj

    @property
    def server(self) -> dict:
        return self._config.get("server", {})

    @property
    def database(self) -> dict:
        return self._config.get("database", {})

    @property
    def llm(self) -> dict:
        return self._config.get("llm", {})

    @property
    def output(self) -> dict:
        return self._config.get("output", {})

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by dot-separated key path."""
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value


# Global config instance
config = Config()
