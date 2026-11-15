import math
import os

from investagent.ollama import OllamaProvider
from investagent.providers import AIProvider

DEFAULT_OLLAMA_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_OLLAMA_MODEL = "qwen2.5:3b"
DEFAULT_OLLAMA_TIMEOUT = 120.0


class AIConfigurationError(ValueError):
    """Raised when AI provider environment configuration is invalid."""


def create_ai_provider_from_environment() -> AIProvider | None:
    provider_name = os.getenv("INVESTAGENT_AI_PROVIDER", "disabled").strip().lower()
    if provider_name == "disabled":
        return None
    if provider_name != "ollama":
        raise AIConfigurationError("Unsupported AI provider.")

    model = os.getenv("INVESTAGENT_OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL).strip()
    if not model:
        raise AIConfigurationError("Ollama model must not be empty.")

    try:
        timeout = float(os.getenv("INVESTAGENT_OLLAMA_TIMEOUT", str(DEFAULT_OLLAMA_TIMEOUT)))
    except ValueError as error:
        raise AIConfigurationError("Ollama timeout must be a number.") from error
    if not math.isfinite(timeout) or timeout <= 0:
        raise AIConfigurationError("Ollama timeout must be a finite positive number.")

    base_url = os.getenv("INVESTAGENT_OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL)
    try:
        return OllamaProvider(base_url=base_url, model=model, timeout=timeout)
    except ValueError as error:
        raise AIConfigurationError("Ollama configuration is invalid.") from error
