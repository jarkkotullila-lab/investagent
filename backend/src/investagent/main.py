from importlib.metadata import version

from fastapi import FastAPI, HTTPException

from investagent.schemas import ResearchAnalyzeRequest, ResearchAnalyzeResponse

app = FastAPI(title="InvestAgent API", version=version("investagent"))


@app.post(
    "/api/v1/research/analyze",
    response_model=ResearchAnalyzeResponse,
    responses={501: {"description": "Research analysis is not implemented yet."}},
)
def analyze_research(request: ResearchAnalyzeRequest) -> ResearchAnalyzeResponse:
    raise HTTPException(
        status_code=501,
        detail="Research analysis is not implemented yet.",
    )


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "investagent-api",
        "version": app.version,
    }
