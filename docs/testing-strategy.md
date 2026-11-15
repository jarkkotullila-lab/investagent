# Testing strategy

## Backend

Use Pytest for fast, deterministic unit and integration tests. HTTPX's
`AsyncClient` with `ASGITransport` exercises the application in-process, so
backend tests do not need a separately running server. The health endpoint
test checks its HTTP status, JSON contract, and response content type.

Run from `backend/`:

```shell
uv run --locked pytest
```

## API acceptance tests

Robot Framework is the acceptance test layer. API requests and response
contract assertions belong in API resources; suites describe business-readable
behavior and do not issue HTTP requests directly. The shared API configuration
resource defines a local default base URL that can be overridden with
`--variable API_BASE_URL:<url>`.

The implemented health suite is independently runnable against a started API.
Run it from the repository root:

```shell
uv run --no-project --python 3.12 \
  --with-requirements tests/robot/requirements.txt robot \
  --variable API_BASE_URL:http://127.0.0.1:8000 \
  tests/robot/suites/api/health.robot
```

Robot output, log, and report files are written to the current directory.

## Static checks and CI

Ruff checks backend source and tests:

```shell
uv run --locked ruff check src tests
```

GitHub Actions runs Ruff and Pytest, starts the API, waits for its health
endpoint, and then runs the Robot Framework API suite. Robot output and HTML
reports are uploaded even when the suite fails.
