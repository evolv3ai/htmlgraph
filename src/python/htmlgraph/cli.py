#!/usr/bin/env python3
"""
HtmlGraph CLI.

Usage:
    htmlgraph serve [--port PORT] [--dir DIR]
    htmlgraph init [DIR]
    htmlgraph status [--dir DIR]
    htmlgraph query SELECTOR [--dir DIR]
"""

import argparse
import sys
from pathlib import Path


def cmd_serve(args):
    """Start the HtmlGraph server."""
    from htmlgraph.server import serve
    serve(
        port=args.port,
        graph_dir=args.graph_dir,
        static_dir=args.static_dir,
        host=args.host
    )


def cmd_init(args):
    """Initialize a new .htmlgraph directory."""
    from htmlgraph.server import HtmlGraphAPIHandler

    graph_dir = Path(args.dir) / ".htmlgraph"
    graph_dir.mkdir(parents=True, exist_ok=True)

    for collection in HtmlGraphAPIHandler.COLLECTIONS:
        (graph_dir / collection).mkdir(exist_ok=True)

    # Copy stylesheet
    styles_src = Path(__file__).parent / "styles.css"
    styles_dest = graph_dir / "styles.css"
    if styles_src.exists() and not styles_dest.exists():
        styles_dest.write_text(styles_src.read_text())

    # Create default index.html if not exists
    index_path = Path(args.dir) / "index.html"
    if not index_path.exists():
        create_default_index(index_path)

    print(f"Initialized HtmlGraph in {graph_dir}")
    print(f"Collections: {', '.join(HtmlGraphAPIHandler.COLLECTIONS)}")
    print(f"\nStart server with: htmlgraph serve")


def cmd_status(args):
    """Show status of the graph."""
    from htmlgraph.graph import HtmlGraph

    graph_dir = Path(args.graph_dir)
    if not graph_dir.exists():
        print(f"Error: {graph_dir} not found. Run 'htmlgraph init' first.")
        sys.exit(1)

    total = 0
    by_status = {}
    by_collection = {}

    for collection_dir in graph_dir.iterdir():
        if collection_dir.is_dir() and not collection_dir.name.startswith("."):
            graph = HtmlGraph(collection_dir, auto_load=True)
            stats = graph.stats()
            by_collection[collection_dir.name] = stats["total"]
            total += stats["total"]
            for status, count in stats["by_status"].items():
                by_status[status] = by_status.get(status, 0) + count

    print(f"HtmlGraph Status: {graph_dir}")
    print(f"{'=' * 40}")
    print(f"Total nodes: {total}")
    print(f"\nBy Collection:")
    for coll, count in sorted(by_collection.items()):
        print(f"  {coll}: {count}")
    print(f"\nBy Status:")
    for status, count in sorted(by_status.items()):
        print(f"  {status}: {count}")


def cmd_query(args):
    """Query nodes with CSS selector."""
    from htmlgraph.graph import HtmlGraph
    from htmlgraph.converter import node_to_dict
    import json

    graph_dir = Path(args.graph_dir)
    if not graph_dir.exists():
        print(f"Error: {graph_dir} not found.", file=sys.stderr)
        sys.exit(1)

    results = []
    for collection_dir in graph_dir.iterdir():
        if collection_dir.is_dir() and not collection_dir.name.startswith("."):
            graph = HtmlGraph(collection_dir, auto_load=True)
            for node in graph.query(args.selector):
                data = node_to_dict(node)
                data["_collection"] = collection_dir.name
                results.append(data)

    if args.format == "json":
        print(json.dumps(results, indent=2, default=str))
    else:
        for node in results:
            status = node.get("status", "?")
            priority = node.get("priority", "?")
            print(f"[{node['_collection']}] {node['id']}: {node['title']} ({status}, {priority})")


def create_default_index(path: Path):
    """Create a default index.html that uses the API."""
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HtmlGraph Dashboard</title>
    <style>
        :root {
            --color-primary: #2563eb;
            --color-success: #16a34a;
            --color-warning: #d97706;
            --color-danger: #dc2626;
            --color-bg: #f9fafb;
            --color-card: #ffffff;
            --color-text: #1f2937;
            --color-muted: #6b7280;
            --color-border: #e5e7eb;
        }
        @media (prefers-color-scheme: dark) {
            :root {
                --color-bg: #111827;
                --color-card: #1f2937;
                --color-text: #f9fafb;
                --color-muted: #9ca3af;
                --color-border: #374151;
            }
        }
        * { box-sizing: border-box; }
        body {
            font-family: system-ui, -apple-system, sans-serif;
            background: var(--color-bg);
            color: var(--color-text);
            margin: 0;
            padding: 2rem;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        header { text-align: center; margin-bottom: 2rem; }
        header h1 { margin: 0; }
        header p { color: var(--color-muted); }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        .stat {
            background: var(--color-card);
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
        }
        .stat-value { font-size: 2rem; font-weight: 700; color: var(--color-primary); }
        .stat-label { font-size: 0.75rem; color: var(--color-muted); text-transform: uppercase; }
        .kanban {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1rem;
        }
        .column {
            background: var(--color-card);
            border-radius: 8px;
            padding: 1rem;
        }
        .column h2 {
            font-size: 0.875rem;
            margin: 0 0 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--color-border);
            display: flex;
            justify-content: space-between;
        }
        .column h2 span {
            background: var(--color-bg);
            padding: 0.125rem 0.5rem;
            border-radius: 999px;
            font-size: 0.75rem;
        }
        .cards { display: flex; flex-direction: column; gap: 0.5rem; }
        .card {
            display: block;
            background: var(--color-bg);
            padding: 0.75rem;
            border-radius: 6px;
            text-decoration: none;
            color: inherit;
            border-left: 3px solid var(--color-primary);
        }
        .card:hover { opacity: 0.8; }
        .card-title { font-weight: 600; margin-bottom: 0.25rem; }
        .card-meta { font-size: 0.75rem; color: var(--color-muted); }
        .badge {
            display: inline-block;
            padding: 0.125rem 0.375rem;
            border-radius: 999px;
            font-size: 0.625rem;
            font-weight: 600;
            margin-right: 0.25rem;
        }
        .priority-critical { background: #fee2e2; color: #dc2626; }
        .priority-high { background: #fef3c7; color: #d97706; }
        .priority-medium { background: #dbeafe; color: #2563eb; }
        .priority-low { background: #f3f4f6; color: #6b7280; }
        .type-feature { border-left-color: var(--color-warning); }
        .type-bug { border-left-color: var(--color-danger); }
        .type-spike { border-left-color: #8b5cf6; }
        .type-chore { border-left-color: var(--color-muted); }
        .empty { color: var(--color-muted); text-align: center; padding: 2rem; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>HtmlGraph</h1>
            <p>"HTML is All You Need"</p>
        </header>
        <div class="stats" id="stats">Loading...</div>
        <div class="kanban" id="kanban"></div>
    </div>
    <script>
        const API = '/api';
        const STATUSES = ['in-progress', 'todo', 'blocked', 'done'];
        const STATUS_LABELS = {
            'in-progress': 'In Progress',
            'todo': 'Todo',
            'blocked': 'Blocked',
            'done': 'Done'
        };

        async function loadData() {
            const [status, query] = await Promise.all([
                fetch(`${API}/status`).then(r => r.json()),
                fetch(`${API}/query`).then(r => r.json())
            ]);
            return { status, nodes: query.nodes };
        }

        function renderStats(status) {
            const s = status.by_status || {};
            document.getElementById('stats').innerHTML = `
                <div class="stat"><div class="stat-value">${status.total_nodes}</div><div class="stat-label">Total</div></div>
                <div class="stat"><div class="stat-value">${s['done'] || 0}</div><div class="stat-label">Done</div></div>
                <div class="stat"><div class="stat-value">${s['in-progress'] || 0}</div><div class="stat-label">Active</div></div>
                <div class="stat"><div class="stat-value">${s['blocked'] || 0}</div><div class="stat-label">Blocked</div></div>
            `;
        }

        function renderKanban(nodes) {
            const byStatus = {};
            STATUSES.forEach(s => byStatus[s] = []);
            nodes.forEach(n => {
                if (byStatus[n.status]) byStatus[n.status].push(n);
            });

            document.getElementById('kanban').innerHTML = STATUSES.map(status => `
                <div class="column">
                    <h2>${STATUS_LABELS[status]} <span>${byStatus[status].length}</span></h2>
                    <div class="cards">
                        ${byStatus[status].length === 0 ? '<div class="empty">Empty</div>' : ''}
                        ${byStatus[status].map(n => `
                            <div class="card type-${n.type}">
                                <div class="card-title">${n.title}</div>
                                <div class="card-meta">
                                    <span class="badge priority-${n.priority}">${n.priority}</span>
                                    ${n._collection}/${n.id}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `).join('');
        }

        loadData().then(({ status, nodes }) => {
            renderStats(status);
            renderKanban(nodes);
        }).catch(err => {
            document.getElementById('stats').innerHTML = `<div class="empty">Error loading data: ${err.message}</div>`;
        });
    </script>
</body>
</html>
'''
    path.write_text(html)


def main():
    parser = argparse.ArgumentParser(
        description="HtmlGraph - HTML is All You Need",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  htmlgraph init                    # Initialize .htmlgraph in current dir
  htmlgraph serve                   # Start server on port 8080
  htmlgraph serve --port 3000       # Start server on port 3000
  htmlgraph status                  # Show graph status
  htmlgraph query "[data-status='todo']"  # Query nodes

curl Examples:
  curl localhost:8080/api/status
  curl localhost:8080/api/features
  curl -X POST localhost:8080/api/features -d '{"title": "New feature"}'
  curl -X PATCH localhost:8080/api/features/feat-001 -d '{"status": "done"}'
"""
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # serve
    serve_parser = subparsers.add_parser("serve", help="Start the HtmlGraph server")
    serve_parser.add_argument("--port", "-p", type=int, default=8080, help="Port (default: 8080)")
    serve_parser.add_argument("--host", default="localhost", help="Host (default: localhost)")
    serve_parser.add_argument("--graph-dir", "-g", default=".htmlgraph", help="Graph directory")
    serve_parser.add_argument("--static-dir", "-s", default=".", help="Static files directory")

    # init
    init_parser = subparsers.add_parser("init", help="Initialize .htmlgraph directory")
    init_parser.add_argument("dir", nargs="?", default=".", help="Directory to initialize")

    # status
    status_parser = subparsers.add_parser("status", help="Show graph status")
    status_parser.add_argument("--graph-dir", "-g", default=".htmlgraph", help="Graph directory")

    # query
    query_parser = subparsers.add_parser("query", help="Query nodes with CSS selector")
    query_parser.add_argument("selector", help="CSS selector (e.g. [data-status='todo'])")
    query_parser.add_argument("--graph-dir", "-g", default=".htmlgraph", help="Graph directory")
    query_parser.add_argument("--format", "-f", choices=["text", "json"], default="text", help="Output format")

    args = parser.parse_args()

    if args.command == "serve":
        cmd_serve(args)
    elif args.command == "init":
        cmd_init(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "query":
        cmd_query(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
