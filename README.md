# InvestAgent

InvestAgent is a local-first AI investment research assistant for exploring
financial information while keeping personal data under the user's control.
It is also a public portfolio project focused on maintainable engineering and
reliable AI quality practices.

## Technology stack

- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2.x, Alembic
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

This repository is at the engineering-foundation stage. It contains project
guidance and architecture documentation, but no backend or frontend
functionality, dependency manifests, automated tests, or CI workflows have
been implemented. No Docker setup, authentication, multi-user support, or
cloud infrastructure is required at this stage.

## Planned development phases

1. **Foundation:** document conventions and establish a minimal, reproducible
   local development and test workflow.
2. **Local application skeleton:** add the smallest runnable FastAPI and
   React/TypeScript applications, SQLite persistence, and focused Pytest
   coverage.
3. **Local research workflow:** implement a useful end-to-end research flow
   using local data and Ollama, with versioned prompts and deterministic AI
   tests.
4. **Acceptance testing and usability:** add Robot Framework acceptance tests
   using business, page, and API resources; add translated UI resources as
   user-facing screens are introduced.
5. **Reassess future needs:** consider PostgreSQL or other deferred features
   only when actual requirements justify them.

The Robot Framework layers are a design convention, not a reason to create
unused resource abstractions before there are workflows to test.
