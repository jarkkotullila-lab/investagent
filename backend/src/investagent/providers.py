from typing import Protocol


class AIProvider(Protocol):
    async def generate(self, prompt: str) -> str:
        """Return a provider response as text."""
