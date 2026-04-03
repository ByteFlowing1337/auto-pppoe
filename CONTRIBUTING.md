# Contributing

## Scope

Contributions should keep the project small and implementation-driven. AutoDialer is a CLI package with router-specific integrations, so changes are easiest to review when they are narrow, tested, and explicit about firmware assumptions.

## Local Setup


```bash
python -m venv .venv

# Windows (PowerShell)
. .\.venv\Scripts\Activate.ps1

# Linux/macOS
source .venv/bin/activate

python -m pip install -r requirements-dev.txt
```

`requirements-dev.txt` includes the editable install plus the development tools used by the repository.

## Development Commands

Run these before opening a pull request:

```bash
pre-commit run --all-files
ruff check .
python -m unittest
python -m build
```



## Pre-commit Hooks

This repository already includes a [`.pre-commit-config.yaml`](.pre-commit-config.yaml) with local Ruff hooks for both `pre-commit` and `pre-push`.

Install the hooks after setting up your environment:

```bash
pre-commit install
pre-commit install --hook-type pre-push
```


To run the configured checks manually across the repository:

```bash
pre-commit run --all-files
```

## Project Layout

- `src/autodialer/`: package source
- `src/autodialer/apis/routers/`: router-specific integrations
- `src/autodialer/apis/utils/`: gateway detection, ISP checks, vendor detection, and helper utilities
- `tests/`: unit tests

## Coding Expectations

- Target Python 3.10+.
- Prefer type hints for new code and preserve the existing typed style.
- Use `logging` for diagnostics instead of ad hoc prints in library code.
- Keep vendor- and firmware-specific payloads inside the router module that owns them.
- Avoid adding broad abstractions unless they remove repeated logic across multiple router integrations.

## Testing Expectations

- Add or update tests for behavior changes.
- Prefer unit tests with mocked network/process calls over tests that require a real router or public network access.
- When adding a new router integration, cover vendor resolution and at least the main reconnection path.

## Documentation Expectations

Update documentation when you change:

- CLI arguments or behavior
- environment variables
- supported router vendors
- contributor workflow or required tooling

At minimum, keep `README.MD`, `docs/`, and this file aligned with the implementation.

## Pull Requests

A good pull request for this project usually includes:

- a focused change set,
- tests for new or changed behavior,
- documentation updates when user-facing behavior changes, and
- a short explanation of firmware or router assumptions if the change is vendor-specific.

If a router behavior only works on a narrow model or firmware family, state that clearly in code comments, tests, or the pull request description.
