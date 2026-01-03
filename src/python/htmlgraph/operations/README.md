# HtmlGraph Operations Layer

This module defines a shared, backend operations layer for HtmlGraph. The CLI and SDK
should call these operations rather than duplicating logic. The operations layer is
pure Python, stateless, and returns structured data instead of printing.

## Design Principles

- Stateless: all inputs passed explicitly; no global CLI state.
- Typed: full type hints, dataclasses for results.
- Structured results: return data, warnings, and metadata; no printing.
- Exceptions for errors: no sys.exit.
- Path-first: accept Path objects for filesystem inputs.
- Reusable: callable from CLI, SDK, and tests.

## Module Structure

- `operations/server.py`   Server startup and lifecycle helpers
- `operations/hooks.py`    Git hook installation and configuration
- `operations/events.py`   Event export, index rebuild, event queries
- `operations/analytics.py` Analytics summaries and report generation

## Example Signature

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Any

@dataclass
class ServerHandle:
    url: str
    port: int
    host: str

@dataclass
class ServerStartResult:
    handle: ServerHandle
    warnings: list[str]
    config_used: dict[str, Any]

class ServerStartError(RuntimeError):
    pass


def start_server(
    *,
    port: int,
    graph_dir: Path,
    host: str = "localhost",
    watch: bool = True,
    auto_port: bool = False,
) -> ServerStartResult:
    """Start HtmlGraph server with validated config."""
    raise NotImplementedError
```

## Conventions

- Functions should avoid any CLI-specific formatting.
- Results should be serializable for JSON output.
- Keep modules focused on a single domain (server, hooks, events, analytics).
