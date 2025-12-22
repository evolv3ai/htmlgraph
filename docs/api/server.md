# Server

Development server for the dashboard.

## Overview

The server module provides a lightweight HTTP server for serving the HtmlGraph dashboard during development.

## Usage

### Command Line

```bash
# Start server on default port (8080)
htmlgraph serve

# Custom port
htmlgraph serve --port 3000

# Custom host
htmlgraph serve --host 0.0.0.0 --port 8080

# Auto-reload on file changes
htmlgraph serve --watch
```

### Python API

```python
from htmlgraph.server import serve

# Start server
serve(
    graph_dir=".htmlgraph",
    port=8080,
    host="localhost",
    watch=False
)
```

## Features

- Serves static HTML/CSS/JS files
- Watches for file changes (optional)
- CORS headers for local development
- Gzip compression
- Cache headers

## Complete API Reference

For detailed API documentation with method signatures and server configuration, see the Python source code in `src/python/htmlgraph/server.py`.
