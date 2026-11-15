# InvestAgent

InvestAgent is a local-first AI investment research assistant for exploring
financial information while keeping personal data under the user's control.
It is also a public portfolio project focused on maintainable engineering and
reliable AI quality practices.

## Technology stack

- **Backend:** Python 3.12, FastAPI, Uvicorn, SQLAlchemy 2.x, Alembic
- **Frontend:** React, TypeScript, Vite, `react-i18next`
- **Database:** SQLite initially; PostgreSQL is a future migration option
- **AI:** Ollama for local inference by default; optional cloud LLM providers
  only after explicit configuration; CrewAI may be used for orchestration
  when agent workflows justify it
- **Testing:** Pytest for backend unit/integration tests; Robot Framework as
  the primary acceptance test framework

## Architecture principles

- Keep development local-first and minimize operational costs.
- Keep personal financial data local and out of version control; use only
  synthetic data in tests and examples.
- Keep business logic independent of web, database, and AI provider details.
- Add abstractions only when a real use case requires them.
- Keep provider integrations interchangeable without requiring cloud services.
- Use SQLite first while keeping database access compatible with a future
  PostgreSQL migration.
- Use deterministic tests for AI behavior; do not make test results depend on
  live model calls.

See [ADR-0001](docs/adr/0001-local-first-architecture.md) for the architecture
decision and local-data/cloud-privacy conventions.

## Current implementation status

The backend is an installable FastAPI package with `GET /api/v1/health`,
Pytest coverage, Ruff checks, and Robot Framework API acceptance tests. The
React dashboard displays the local backend connection status and supports
English and Finnish. Database access, AI integrations, authentication, and
investment analysis are not implemented. No Docker setup or cloud
infrastructure is required.

## Backend development

Use Python 3.12 and [uv](https://docs.astral.sh/uv/). From the repository root,
install the locked backend dependencies:

```shell
uv sync --locked --project backend
```

From the `backend/` directory, start the API:

```shell
uv run --locked uvicorn investagent.main:app --reload
```

The API listens on `http://127.0.0.1:8000`; its health endpoint is
`http://127.0.0.1:8000/api/v1/health`.

### Research API contract

`POST /api/v1/research/analyze` accepts `company_name` (string) and `sources`
(a list of objects with unique `source_id` and `text` strings). Its planned
response contains `company_name` and `summary` strings, plus `opportunities`,
`risks`, and `source_references` (source ID) string lists. The analysis
service is not implemented yet, so valid requests currently return HTTP 501
with an explanatory message; the API does not generate placeholder analysis.

Run backend tests and lint checks from `backend/`:

```shell
uv run --locked pytest
uv run --locked ruff check src tests
```

## Frontend development

Install the locked frontend dependencies from `frontend/`:

```shell
npm ci
```

In one terminal, start the backend using the instructions above. In another
terminal, start the Vite development server from `frontend/`:

```shell
npm run dev
```

Open `http://127.0.0.1:5173`. Vite forwards `/api` requests to the local
backend at `http://127.0.0.1:8000`. The dashboard remains available if the
backend is stopped and reports the connection as offline.

Run frontend checks from `frontend/`:

```shell
npm run test:run
npm run lint
npm run typecheck
npm run build
```

Component tests mock network requests and do not require a running backend.
The development server requires the backend only to report its live status.

## Robot Framework API acceptance test

Start the API in a separate terminal first. From the repository root, run:

```shell
uv run --no-project --python 3.12 \
  --with-requirements tests/robot/requirements.txt robot \
  --variable API_BASE_URL:http://127.0.0.1:8000 \
  tests/robot/suites/api/health.robot
```

`API_BASE_URL` defaults to `http://127.0.0.1:8000` and can be overridden with
Robot's `--variable` option. Robot Framework writes `output.xml`, `log.html`,
and `report.html` in the current directory.

## Robot Framework UI acceptance tests

The UI suite requires both the backend and frontend development server. From
the repository root on macOS or Linux, install the Robot dependencies and
Chromium once:

```shell
uv venv tests/robot/.venv --python 3.12
uv pip install --python tests/robot/.venv/bin/python \
  -r tests/robot/requirements.txt \
  -r tests/robot/requirements-ui.txt
tests/robot/.venv/bin/rfbrowser init chromium
```

The Robot requirements files pin direct dependencies and are shared by local
setup and CI. Transitive Python dependencies are not lockfile-pinned and can
vary within their upstream constraints; Browser Library's Node wrapper uses
the lockfile shipped with its pinned package.

With the backend and frontend running in separate terminals, run the suite:

```shell
tests/robot/.venv/bin/robot \
  --outputdir test-results/ui \
  --variable FRONTEND_BASE_URL:http://127.0.0.1:5173 \
  tests/robot/suites/ui
```

`FRONTEND_BASE_URL` defaults to `http://127.0.0.1:5173`. UI tests use isolated
browser contexts and mock the health endpoint as unavailable for the offline
scenario.

## Planned development phases

1. **Local research workflow:** implement a useful end-to-end research flow
   using local data and Ollama, with versioned prompts and deterministic AI
   tests.
2. **Data management:** add local SQLite persistence and migrations, keeping
   database access compatible with a future PostgreSQL migration.
3. **Acceptance testing and usability:** extend the layered Robot Framework
   suites as workflows are introduced and continue improving translated UI.
4. **Reassess future needs:** consider cloud providers, authentication, or
   commercial features only when actual requirements justify them.

The Robot Framework layers are a design convention, not a reason to create
unused resource abstractions before there are workflows to test.
