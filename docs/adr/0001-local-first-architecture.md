# ADR-0001: Local-First Architecture

## Status

Accepted

## Context

InvestAgent is initially developed for personal use.

The project must:

- Minimize development and operational costs.
- Protect personal investment data.
- Support local AI inference.
- Allow future, opt-in cloud LLM integration.
- Demonstrate professional software engineering.
- Avoid premature enterprise and commercial architecture.

## Decision

InvestAgent will use a local-first architecture.

Backend:
Python and FastAPI.

Frontend:
React and TypeScript.

Database:
SQLite initially, accessed through SQLAlchemy.

AI:
Hybrid architecture with Ollama as the local default. Cloud providers remain
disabled unless explicitly configured by the user. Introduce CrewAI only if
agent workflows justify an orchestration framework.

Testing:
Pytest and Robot Framework.

## Privacy and local data conventions

- Store real financial files and the local SQLite database under
  `data/private/` (for example, `data/private/investagent.sqlite3`). Keep this
  directory out of version control.
- SQLite journal, write-ahead log, and shared-memory sidecar files are private
  database data too; keep them beside the database and out of version control.
- Never use real financial data in tests, fixtures, examples, screenshots, or
  portfolio documentation. Use synthetic data instead.
- `.gitignore` is a convenience, not a security control. Review staged files
  and diffs before committing, restrict access to local files, and do not put
  private data in issues, logs, or other shared systems.
- Keep credentials in local, ignored configuration such as `.env`; commit only
  placeholder examples, never usable secrets.

## Cloud LLM privacy requirements

Cloud LLM providers must remain disabled by default. Any future integration
must require explicit user configuration and document a clear outbound-data
policy before use. The policy must identify what information is sent, to which
provider and for what purpose; minimize or redact data where possible; and
ensure the user deliberately opts in before private financial information can
leave the device. Local inference remains the default path.

## Consequences

### Benefits

- Low operational costs.
- Local control of financial data.
- Simple development environment.
- No mandatory cloud infrastructure.
- A clear path to add capabilities only when justified.

### Trade-offs

- Local AI performance depends on hardware.
- SQLite has limitations for multi-user deployments.
- Cloud LLM integrations require explicit privacy controls and user consent.

## Explicitly deferred

- PostgreSQL migration, until scale or deployment needs justify it.
- Authentication and multi-user support.
- Cloud application deployment and managed infrastructure.
- Commercial licensing, billing, and enterprise features.
- Production-grade AI observability.

These are not part of the initial local-first implementation.