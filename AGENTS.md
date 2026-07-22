# Instructions for coding agents

This repository is a permanent, local-first CV generation tool. Prefer small, typed modules and
deterministic behaviour. Keep domain logic independent of the CLI and renderer. Do not add SaaS,
database, Docker, telemetry, or cloud dependencies.

## Non-negotiable content rules

- Never fabricate experience.
- Never modify dates.
- Never modify employers.
- Never invent technologies.
- Always preserve factual correctness.
- Every tailored experience or project bullet must retain its master `source_id`.
- A validation failure must stop rendering.

## Development rules

- Use Python 3.13, Pydantic, Typer, pytest, Ruff, mypy, and British English.
- Put application code in `src/cv_builder` and keep filesystem access at module boundaries.
- Add tests for behaviour changes and regressions.
- Always run tests, Ruff, and mypy before handing work back.
- Always validate a tailored CV before rendering it.
- Preserve backwards compatibility of saved YAML where practical.
- Do not commit generated application output, caches, secrets, or personal data beyond the
  deliberately versioned example master CV.

