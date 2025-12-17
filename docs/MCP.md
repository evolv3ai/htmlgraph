# Minimal MCP Server

HtmlGraph includes a tiny MCP (Model Context Protocol) server intended as a **workflow conduit** for agents that don’t have native hooks (e.g., Codex/Gemini).

## Goals

- Expose only **3 tools** to avoid context/tool-schema bloat.
- Route all state into HtmlGraph’s existing filesystem-first tracking (`.htmlgraph/events/*.jsonl`).
- Encourage agents to use the **HtmlGraph HTTP API** and/or **CLI** for discovery and operations beyond logging.

## Run

```bash
htmlgraph mcp serve
```

Use `--graph-dir` to point at a specific HtmlGraph directory:

```bash
htmlgraph mcp serve -g .htmlgraph
```

## Tools

- `log_event(tool, summary, files?, success?, feature_id?, payload?, agent?)`
- `get_active_feature(agent?)`
- `set_active_feature(feature_id, collection?, agent?)`

## Notes

- The server runs over **stdio** (JSON-RPC style messages).
- The event stream is append-only under `.htmlgraph/events/`; the analytics DB is rebuildable (`htmlgraph index rebuild`).
- `get_active_feature` and `set_active_feature` **auto-log** lightweight MCP events by default (throttled). Disable with `HTMLGRAPH_MCP_AUTOLOG=0`.

## How Agents Should Use It

MCP is intentionally minimal. For anything beyond “what am I working on?” and “log what I did”, use:

1) **CLI for discovery and batch operations**

```bash
htmlgraph --help
htmlgraph query "[data-status='in-progress']"
htmlgraph events export-sessions -g .htmlgraph
htmlgraph index rebuild -g .htmlgraph
```

2) **HTTP API for structured reads/writes**

Run the server:

```bash
htmlgraph serve
```

Common endpoints:

- `GET /api/collections` → list collections
- `GET /api/status` → WIP + primary overview
- `GET /api/query?selector=...` → cross-collection query (CSS selector)
- `GET /api/<collection>` / `GET /api/<collection>/<id>` → list/get nodes
- `PATCH /api/<collection>/<id>` → update node fields (include `"agent": "<agent-name>"` for attribution)
- `GET /api/analytics/overview|features|continuity|transitions|commits` → analytics (rebuilt from JSONL)

Recommended pattern:
- Use API/CLI to do the work.
- Call `log_event(...)` (or rely on git hooks / watchers) to record significant actions in the event stream for cross-session analytics.
