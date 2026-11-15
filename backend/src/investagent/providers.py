from typing import Protocol


class AIProviderError(Exception):
    """Base error for failures communicating with an AI provider."""


class AIProviderConnectionError(AIProviderError):
    """The AI provider could not be reached."""


class AIProviderTimeoutError(AIProviderError):
    """The AI provider did not respond before the configured timeout."""


class AIProviderResponseError(AIProviderError):
    """The AI provider returned an invalid protocol response."""


class AIProvider(Protocol):
    async def generate(self, prompt: str) -> str:
        """Return a provider response as text."""
