import asyncio

import httpx

from investagent.main import app


async def _request_health_response() -> httpx.Response:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        return await client.get("/api/v1/health")


def _get_health_response() -> httpx.Response:
    return asyncio.run(_request_health_response())


def test_health_returns_http_200() -> None:
    response = _get_health_response()

    assert response.status_code == 200


def test_health_response_matches_contract() -> None:
    response = _get_health_response()

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "investagent-api",
        "version": "0.1.0",
    }


def test_health_response_content_type_is_json() -> None:
    response = _get_health_response()

    assert response.headers["content-type"].startswith("application/json")
