import asyncio
import json
from collections.abc import Callable

import httpx
import pytest

from investagent.configuration import (
    AIConfigurationError,
    create_ai_provider_from_environment,
)
from investagent.main import app, get_ai_provider
from investagent.ollama import OllamaProvider
from investagent.providers import (
    AIProviderConnectionError,
    AIProviderResponseError,
    AIProviderTimeoutError,
)
from investagent.schemas import ResearchAnalyzeResponse

VALID_REQUEST = {
    "company_name": "Example Corporation",
    "sources": [
        {
            "source_id": "source-1",
            "text": "Synthetic source content for local Ollama tests.",
        }
    ],
}

VALID_ANALYSIS = {
    "company_name": "Example Corporation",
    "summary": "A summary supported by the synthetic source.",
    "opportunities": [],
    "risks": [],
    "source_references": ["source-1"],
}


def _provider(
    handler: Callable[[httpx.Request], httpx.Response],
    *,
    timeout: float = 2.0,
) -> OllamaProvider:
    return OllamaProvider(
        base_url="http://127.0.0.1:11434",
        model="qwen2.5:3b",
        timeout=timeout,
        transport=httpx.MockTransport(handler),
    )


def _generate(provider: OllamaProvider) -> str:
    return asyncio.run(provider.generate("synthetic prompt"))


async def _post_research(payload: dict[str, object]) -> httpx.Response:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        return await client.post("/api/v1/research/analyze", json=payload)


def _post_research_with_provider(
    provider: OllamaProvider,
    monkeypatch: pytest.MonkeyPatch,
) -> httpx.Response:
    monkeypatch.setitem(app.dependency_overrides, get_ai_provider, lambda: provider)
    return asyncio.run(_post_research(VALID_REQUEST))


def _raise_timeout(request: httpx.Request) -> httpx.Response:
    raise httpx.ReadTimeout("private prompt detail", request=request)


def _raise_connection_error(request: httpx.Request) -> httpx.Response:
    raise httpx.ConnectError("private connection detail", request=request)


def test_ollama_provider_sends_non_streaming_json_request() -> None:
    def handle(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url == "http://127.0.0.1:11434/api/generate"
        assert json.loads(request.content) == {
            "model": "qwen2.5:3b",
            "prompt": "synthetic prompt",
            "stream": False,
            "format": "json",
        }
        return httpx.Response(200, json={"response": json.dumps(VALID_ANALYSIS)})

    provider = _provider(handle, timeout=3.5)

    assert json.loads(_generate(provider)) == VALID_ANALYSIS
    assert provider.timeout == 3.5


@pytest.mark.parametrize(
    "body",
    [
        b"not JSON",
        b'{"done": true}',
    ],
)
def test_ollama_provider_rejects_malformed_http_responses(body: bytes) -> None:
    provider = _provider(lambda request: httpx.Response(200, content=body))

    with pytest.raises(AIProviderResponseError):
        _generate(provider)


@pytest.mark.parametrize(
    ("error_type", "expected_error"),
    [
        (httpx.ReadTimeout, AIProviderTimeoutError),
        (httpx.ConnectError, AIProviderConnectionError),
    ],
)
def test_ollama_provider_maps_transport_errors(
    error_type: type[httpx.RequestError],
    expected_error: type[Exception],
) -> None:
    def handle(request: httpx.Request) -> httpx.Response:
        raise error_type("private request detail", request=request)

    with pytest.raises(expected_error) as error:
        _generate(_provider(handle))

    assert "private request detail" not in str(error.value)


def test_ollama_provider_hides_http_error_body() -> None:
    provider = _provider(
        lambda request: httpx.Response(500, text="private server details")
    )

    with pytest.raises(AIProviderResponseError) as error:
        _generate(provider)

    assert "private server details" not in str(error.value)


def test_provider_defaults_to_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("INVESTAGENT_AI_PROVIDER", raising=False)
    monkeypatch.setenv("INVESTAGENT_OLLAMA_TIMEOUT", "invalid-but-ignored")

    assert create_ai_provider_from_environment() is None


def test_ollama_provider_uses_environment_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("INVESTAGENT_AI_PROVIDER", "ollama")
    monkeypatch.setenv("INVESTAGENT_OLLAMA_BASE_URL", "http://localhost:11435/")
    monkeypatch.setenv("INVESTAGENT_OLLAMA_MODEL", "qwen2.5:1.5b")
    monkeypatch.setenv("INVESTAGENT_OLLAMA_TIMEOUT", "17.5")

    provider = create_ai_provider_from_environment()

    assert isinstance(provider, OllamaProvider)
    assert provider.base_url == "http://localhost:11435"
    assert provider.model == "qwen2.5:1.5b"
    assert provider.timeout == 17.5


def test_ollama_configuration_rejects_non_local_base_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("INVESTAGENT_AI_PROVIDER", "ollama")
    monkeypatch.setenv("INVESTAGENT_OLLAMA_BASE_URL", "https://example.com")

    with pytest.raises(AIConfigurationError):
        create_ai_provider_from_environment()


def test_research_endpoint_returns_validated_local_analysis(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _provider(
        lambda request: httpx.Response(200, json={"response": json.dumps(VALID_ANALYSIS)})
    )

    response = _post_research_with_provider(provider, monkeypatch)

    assert response.status_code == 200
    assert response.json() == ResearchAnalyzeResponse.model_validate(VALID_ANALYSIS).model_dump()


@pytest.mark.parametrize(
    ("handler", "status_code", "detail"),
    [
        (
            lambda request: httpx.Response(200, content=b"not JSON"),
            502,
            "Local Ollama returned an invalid response.",
        ),
        (
            lambda request: httpx.Response(200, json={"response": "not JSON"}),
            502,
            "Local Ollama returned an invalid response.",
        ),
        (
            _raise_timeout,
            504,
            "Local Ollama request timed out.",
        ),
        (
            _raise_connection_error,
            503,
            "Local Ollama service is unavailable.",
        ),
    ],
)
def test_research_endpoint_returns_safe_provider_errors(
    handler: Callable[[httpx.Request], httpx.Response],
    status_code: int,
    detail: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = _post_research_with_provider(_provider(handler), monkeypatch)

    assert response.status_code == status_code
    assert response.json() == {"detail": detail}
    assert "private" not in response.text


def test_research_endpoint_rejects_unknown_source_references(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    invalid_analysis = {**VALID_ANALYSIS, "source_references": ["unknown-source"]}
    provider = _provider(
        lambda request: httpx.Response(200, json={"response": json.dumps(invalid_analysis)})
    )

    response = _post_research_with_provider(provider, monkeypatch)

    assert response.status_code == 502
    assert response.json() == {"detail": "Local Ollama returned an invalid response."}
