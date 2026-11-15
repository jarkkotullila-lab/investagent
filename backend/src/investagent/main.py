from importlib.metadata import version

from fastapi import Depends, FastAPI, HTTPException

from investagent.configuration import AIConfigurationError, create_ai_provider_from_environment
from investagent.providers import (
    AIProvider,
    AIProviderConnectionError,
    AIProviderResponseError,
    AIProviderTimeoutError,
)
from investagent.research_service import ResearchProviderResponseError, ResearchService
from investagent.schemas import ResearchAnalyzeRequest, ResearchAnalyzeResponse

app = FastAPI(title="InvestAgent API", version=version("investagent"))


def get_ai_provider() -> AIProvider | None:
    try:
        return create_ai_provider_from_environment()
    except AIConfigurationError:
        raise HTTPException(
            status_code=500,
            detail="AI provider configuration is invalid.",
        ) from None


@app.post(
    "/api/v1/research/analyze",
    response_model=ResearchAnalyzeResponse,
    responses={
        500: {"description": "AI provider configuration is invalid."},
        501: {"description": "Research analysis is not implemented yet."},
        502: {"description": "Local Ollama returned an invalid response."},
        503: {"description": "Local Ollama service is unavailable."},
        504: {"description": "Local Ollama request timed out."},
    },
)
async def analyze_research(
    request: ResearchAnalyzeRequest,
    provider: AIProvider | None = Depends(get_ai_provider),
) -> ResearchAnalyzeResponse:
    if provider is None:
        raise HTTPException(
            status_code=501,
            detail="Research analysis is not implemented yet.",
        )

    try:
        return await ResearchService(provider).analyze(request)
    except AIProviderTimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Local Ollama request timed out.",
        ) from None
    except AIProviderConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Local Ollama service is unavailable.",
        ) from None
    except (AIProviderResponseError, ResearchProviderResponseError):
        raise HTTPException(
            status_code=502,
            detail="Local Ollama returned an invalid response.",
        ) from None


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "investagent-api",
        "version": app.version,
    }
