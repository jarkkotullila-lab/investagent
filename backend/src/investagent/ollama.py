import ipaddress
import math
from urllib.parse import urlsplit

import httpx

from investagent.providers import (
    AIProviderConnectionError,
    AIProviderResponseError,
    AIProviderTimeoutError,
)


class OllamaProvider:
    def __init__(
        self,
        base_url: str,
        model: str,
        timeout: float,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.base_url = self._validate_base_url(base_url)
        if not model.strip():
            raise ValueError("Ollama model must not be empty.")
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("Ollama timeout must be a finite positive number.")

        self.model = model.strip()
        self.timeout = timeout
        self._transport = transport

    async def generate(self, prompt: str) -> str:
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                transport=self._transport,
                trust_env=False,
            ) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json",
                    },
                )
                response.raise_for_status()
        except httpx.TimeoutException as error:
            raise AIProviderTimeoutError("Ollama request timed out.") from error
        except httpx.HTTPStatusError as error:
            raise AIProviderResponseError("Ollama returned an unsuccessful status.") from error
        except httpx.RequestError as error:
            raise AIProviderConnectionError("Ollama request failed.") from error

        try:
            payload = response.json()
        except ValueError as error:
            raise AIProviderResponseError("Ollama returned malformed JSON.") from error

        if not isinstance(payload, dict) or not isinstance(payload.get("response"), str):
            raise AIProviderResponseError("Ollama response did not contain generated text.")

        return payload["response"]

    @staticmethod
    def _validate_base_url(base_url: str) -> str:
        try:
            parsed_url = urlsplit(base_url.strip())
            hostname = parsed_url.hostname
            parsed_url.port
        except ValueError as error:
            raise ValueError("Ollama base URL must be a valid loopback URL.") from error

        if (
            parsed_url.scheme not in {"http", "https"}
            or hostname is None
            or parsed_url.username is not None
            or parsed_url.password is not None
            or parsed_url.query
            or parsed_url.fragment
        ):
            raise ValueError("Ollama base URL must be a valid loopback URL.")

        try:
            is_loopback = ipaddress.ip_address(hostname).is_loopback
        except ValueError:
            is_loopback = hostname.lower() == "localhost"
        if not is_loopback:
            raise ValueError("Ollama base URL must use localhost or a loopback IP.")

        return base_url.strip().rstrip("/")
