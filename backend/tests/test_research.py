import asyncio

import httpx
import pytest
from pydantic import ValidationError

from investagent.main import app
from investagent.schemas import ResearchAnalyzeRequest, ResearchAnalyzeResponse

VALID_REQUEST = {
    "company_name": "Example Corporation",
    "sources": [
        {
            "source_id": "synthetic-source-1",
            "text": "Synthetic research note for API contract testing.",
        }
    ],
}


async def _post_research_response(payload: dict[str, object]) -> httpx.Response:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        return await client.post("/api/v1/research/analyze", json=payload)


def _post_research(payload: dict[str, object]) -> httpx.Response:
    return asyncio.run(_post_research_response(payload))


def test_research_request_accepts_company_and_sources() -> None:
    request = ResearchAnalyzeRequest.model_validate(VALID_REQUEST)

    assert request.company_name == "Example Corporation"
    assert request.sources[0].source_id == "synthetic-source-1"


def test_research_request_rejects_duplicate_source_ids() -> None:
    invalid_request = {
        **VALID_REQUEST,
        "sources": [
            {"source_id": "duplicate", "text": "Synthetic note one."},
            {"source_id": "duplicate", "text": "Synthetic note two."},
        ],
    }

    with pytest.raises(ValidationError, match="source IDs must be unique"):
        ResearchAnalyzeRequest.model_validate(invalid_request)


def test_research_response_model_matches_contract() -> None:
    response = ResearchAnalyzeResponse(
        company_name="Example Corporation",
        summary="Synthetic summary.",
        opportunities=[],
        risks=[],
        source_references=["synthetic-source-1"],
    )

    assert response.model_dump() == {
        "company_name": "Example Corporation",
        "summary": "Synthetic summary.",
        "opportunities": [],
        "risks": [],
        "source_references": ["synthetic-source-1"],
    }


def test_research_analyze_returns_501_until_service_exists() -> None:
    response = _post_research(VALID_REQUEST)

    assert response.status_code == 501
    assert response.json() == {"detail": "Research analysis is not implemented yet."}


def test_research_analyze_rejects_duplicate_source_ids() -> None:
    invalid_request = {
        **VALID_REQUEST,
        "sources": [
            {"source_id": "duplicate", "text": "Synthetic note one."},
            {"source_id": "duplicate", "text": "Synthetic note two."},
        ],
    }

    response = _post_research(invalid_request)

    assert response.status_code == 422
    assert "source IDs must be unique" in response.json()["detail"][0]["msg"]
