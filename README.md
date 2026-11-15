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
Pytest coverage, Ruff checks, and a Robot Framework API acceptance test.
Database access, AI integrations, authentication, and frontend functionality
are not implemented. No Docker setup or cloud infrastructure is required.

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

Run backend tests and lint checks from `backend/`:

```shell
uv run --locked pytest
uv run --locked ruff check src tests
```

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

## Planned development phases

1. **Local application skeleton:** add the React/TypeScript frontend and
   establish focused backend and frontend checks.
2. **Local research workflow:** implement a useful end-to-end research flow
   using local data and Ollama, with versioned prompts and deterministic AI
   tests.
3. **Acceptance testing and usability:** extend Robot Framework tests using
   business, page, and API resources; add translated UI resources as
   user-facing screens are introduced.
4. **Reassess future needs:** consider PostgreSQL or other deferred features
   only when actual requirements justify them.

The Robot Framework layers are a design convention, not a reason to create
unused resource abstractions before there are workflows to test.
