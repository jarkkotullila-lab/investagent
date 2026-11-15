from importlib.metadata import version

from fastapi import FastAPI

app = FastAPI(title="InvestAgent API", version=version("investagent"))


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "investagent-api",
        "version": app.version,
    }
