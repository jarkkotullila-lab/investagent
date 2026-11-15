# InvestAgent – Copilot Engineering Instructions

## Project Overview

InvestAgent is a local-first AI investment research application.

The project has two primary goals:

1. Build a useful personal AI investment research assistant.
2. Demonstrate professional AI engineering and senior-level
   test automation expertise.

## Technology Stack

Backend:
- Python 3.12
- FastAPI
- SQLAlchemy 2.x
- Alembic
- SQLite initially, PostgreSQL later

Frontend:
- React
- TypeScript
- Vite
- react-i18next

AI:
- Hybrid LLM architecture
- Ollama for local inference
- Cloud LLM providers through an abstraction layer
- CrewAI for agent orchestration

Testing:
- Pytest
- Robot Framework
- Robot Framework Browser Library
- Robot Framework RequestsLibrary
- GitHub Actions

## Architecture Principles

1. Follow separation of concerns.
2. Prefer simple and maintainable solutions.
3. Avoid unnecessary abstractions.
4. Use dependency injection where appropriate.
5. Keep business logic independent of frameworks.
6. Design database access for future PostgreSQL migration.
7. Keep LLM providers interchangeable.
8. Never hardcode secrets.
9. Never commit personal financial data.
10. Use synthetic test data.

## Robot Framework Standards

Follow a layered test automation architecture.

Test suites:
- Describe business behavior.
- Do not contain CSS selectors.
- Do not contain direct HTTP requests.
- Must be independently executable.

Business resources:
- Implement business-level keywords.
- Coordinate workflows.
- Must not depend on browser selectors.

Page resources:
- Encapsulate UI interactions.
- Centralize selectors.
- Prefer data-testid attributes.

API resources:
- Encapsulate API requests.
- Validate response contracts.
- Handle API-specific details.

Test data:
- Use synthetic data.
- Avoid shared mutable state.
- Prefer API-based setup and cleanup.

Reliability:
- Avoid fixed sleeps.
- Use condition-based waits.
- Do not hide failures with retries.
- Capture diagnostics on failure.
- Support local and CI execution.

## AI Quality Engineering

AI behavior must be testable.

- Version prompts.
- Mock LLM calls in deterministic tests.
- Validate tool selection.
- Validate structured outputs.
- Track evaluation results.
- Test prompt injection resistance.
- Prevent sensitive data leakage.

## Copilot Workflow

Before implementation:

1. Read the relevant GitHub Issue.
2. Review existing architecture.
3. Propose an implementation plan.
4. Identify required tests.

During implementation:

1. Follow existing project conventions.
2. Implement only the requested scope.
3. Add appropriate automated tests.
4. Avoid unnecessary dependencies.

After implementation:

1. Run relevant tests.
2. Run linting.
3. Report actual results.
4. Summarize changed files.
5. Document unresolved risks.

Never claim tests passed unless they were executed.