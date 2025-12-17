# Repository Guidelines

## Project Structure & Module Organization

- `src/python/htmlgraph/`: primary Python package (CLI, server, parsers, session + event logging, Git hook event logging).
- `tests/python/`: pytest test suite (unit/integration-style).
- `index.html`: dashboard UI (served by `htmlgraph serve`).
- `.htmlgraph/`: runtime + project data (HTML nodes, sessions, event logs, hooks, analytics cache).
  - `.htmlgraph/events/*.jsonl`: append-only event stream (intended source of truth; typically committed).
  - `.htmlgraph/index.sqlite`: rebuildable analytics cache (gitignored).
  - `.htmlgraph/hooks/*.sh`: versioned Git hook scripts (installed into `.git/hooks/` via CLI).

## Build, Test, and Development Commands

- `htmlgraph serve`: run local server (static dashboard + `/api/*`); open `http://localhost:8080`.
- `htmlgraph init --install-hooks`: initialize `.htmlgraph/` and install Git hooks (`post-commit`, `post-checkout`, `post-merge`, `pre-push`).
- `.venv/bin/python -m pytest -q`: run test suite.
- `htmlgraph index rebuild`: rebuild `.htmlgraph/index.sqlite` from `.htmlgraph/events/*.jsonl`.
- `htmlgraph events export-sessions`: migrate legacy session HTML activity logs into JSONL events.

## Coding Style & Naming Conventions

- Python: 4-space indentation, type hints preferred, keep modules dependency-light (server uses stdlib `http.server`).
- Favor small, composable helpers; avoid breaking the event schema (`EventRecord` / JSONL keys).
- Work item naming: `feature-*`, `bug-*`, `chore-*`, `spike-*` files under `.htmlgraph/<collection>/`.

## Testing Guidelines

- Framework: `pytest` (see `tests/python/`).
- Test file naming: `tests/python/test_*.py`.
- UI tests (`tests/python/test_dashboard_ui.py`) are gated: set `HTMLGRAPH_UI_TESTS=1` and ensure Playwright browsers are installed (`playwright install`).

## Commit & Pull Request Guidelines

- Commit messages follow a Conventional Commits-style prefix seen in history: `feat:`, `fix:`, `docs:`, `chore:`.
- PRs: include a short description, how to validate (`pytest` / `htmlgraph serve`), and note any `.htmlgraph/` data changes (especially event logs vs. SQLite cache).

## Agent-Specific Notes

- Git hooks provide agent-agnostic continuity for tools without native hooks (Codex/Gemini): install via `htmlgraph init --install-hooks`.
- Keep `.htmlgraph/index.sqlite` out of Git; use `htmlgraph index rebuild` to regenerate.
