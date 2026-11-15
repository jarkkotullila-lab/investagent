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
The direct Robot Framework and RequestsLibrary versions are pinned in
`tests/robot/requirements.txt`; UI tests add the pinned Browser Library from
`tests/robot/requirements-ui.txt`. CI and local setup use these same files.
Transitive Python dependencies are not lockfile-pinned and may vary within
their upstream constraints. Browser Library's Node wrapper dependencies are
locked by the package's bundled npm lockfile.

## Frontend component tests

Vitest and React Testing Library cover dashboard rendering, loading/online/
offline backend states, and switching to Finnish. Network requests are mocked,
so component tests do not require a running API.

Run from `frontend/`:

```shell
npm ci
npm run test:run
```

Frontend quality checks are also available from `frontend/`:

```shell
npm run lint
npm run typecheck
npm run build
```

## UI acceptance tests

Robot Framework Browser Library tests cover the dashboard, backend connection
states, and English/Finnish language switching. Test suites express user-visible
behavior, business resources coordinate actions, and page resources own
selectors and browser interactions. Each test opens its own browser and
context; the offline case mocks the health endpoint within that test's browser
page instead of stopping the shared API.

The suite requires the API and Vite frontend server to be running. Setup and
execution commands are documented in the README. Reports and logs are uploaded
as artifacts by the UI acceptance workflow, including after test failures.

## Static checks and CI

Ruff checks backend source and tests:

```shell
uv run --locked ruff check src tests
```

GitHub Actions runs Ruff and Pytest, starts the API, waits for its health
endpoint, and then runs the Robot Framework API suite. Robot output and HTML
reports are uploaded even when the suite fails.

The frontend workflow runs linting, TypeScript checks, component tests, and a
production build. The separate UI acceptance workflow installs Chromium,
starts the local API and frontend servers, runs the Browser suite, and stops
both servers during cleanup.
