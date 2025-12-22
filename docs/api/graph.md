# HtmlGraph

Core graph operations and algorithms.

## Overview

The HtmlGraph class provides low-level graph operations:

- Node and edge management
- Graph traversal
- Query execution
- Graph algorithms

## Initialization

```python
from htmlgraph import HtmlGraph

# Initialize with graph directory
graph = HtmlGraph(graph_dir=".htmlgraph")
```

## Nodes

### Adding Nodes

```python
from htmlgraph.models import Feature

feature = Feature(
    id="feature-001",
    title="Add login",
    status="todo",
    priority="high"
)

graph.add_node(feature)
```

### Querying Nodes

```python
# Get all nodes
nodes = graph.get_nodes()

# Get by type
features = graph.get_nodes(type="feature")
sessions = graph.get_nodes(type="session")

# CSS selector query
blocked = graph.query('[data-status="blocked"]')
```

## Edges

### Adding Edges

```python
# Add relationship
graph.add_edge(
    from_id="feature-001",
    to_id="feature-002",
    relationship="blocks"
)
```

### Querying Edges

```python
# Get all edges
edges = graph.get_edges()

# Get edges for a node
edges = graph.get_edges(node_id="feature-001")

# Get edges by relationship type
blocking_edges = graph.get_edges(relationship="blocks")
```

## Graph Algorithms

### Shortest Path

```python
# Find shortest path between nodes
path = graph.shortest_path("feature-001", "feature-045")
# Returns: ["feature-001", "feature-012", "feature-045"]
```

### Transitive Dependencies

```python
# Get all transitive dependencies
deps = graph.transitive_deps("feature-001")
# Returns all features that feature-001 depends on
```

### Bottlenecks

```python
# Find bottleneck features (blocking many others)
bottlenecks = graph.find_bottlenecks()
# Returns features sorted by number of blocked features
```

### Critical Path

```python
# Find longest dependency chain
critical_path = graph.find_critical_path()
# Returns the longest path through the graph
```

## Complete API Reference

For detailed API documentation with method signatures and graph algorithms, see the Python source code in `src/python/htmlgraph/graph.py`.
