# SDK

The SDK is the main interface for interacting with HtmlGraph.

## Overview

The SDK provides a high-level API for:

- Creating and managing features
- Creating and managing tracks
- Querying the graph
- Session management
- Activity tracking

## Initialization

```python
from htmlgraph import SDK

# Basic initialization
sdk = SDK(agent="claude")

# Custom graph directory
sdk = SDK(agent="claude", graph_dir="/path/to/.htmlgraph")

# Disable auto-session management
sdk = SDK(agent="claude", auto_session=False)
```

## Features API

### Creating Features

```python
# Basic feature
feature = sdk.features.create(
    title="Add login page",
    priority="high"
)

# Feature with steps
feature = sdk.features.create(
    title="Add login page",
    priority="high",
    steps=["Create component", "Add routing", "Write tests"]
)

# Feature with custom properties
feature = sdk.features.create(
    title="Add login page",
    priority="high",
    properties={"effort": 4, "assignee": "claude"}
)
```

### Querying Features

```python
# Get all features
all_features = sdk.features.all()

# Filter by status
in_progress = sdk.features.where(status="in-progress")

# Filter by priority
high_priority = sdk.features.where(priority="high")

# Multiple filters
blocked_high = sdk.features.where(status="blocked", priority="high")

# Get specific feature
feature = sdk.features.get("feature-20241216-103045")
```

### Updating Features

```python
# Get feature
feature = sdk.features.get("feature-20241216-103045")

# Update and save
feature.status = "in-progress"
feature.steps[0].completed = True
feature.save()
```

### Deleting Features

```python
sdk.features.delete("feature-20241216-103045")
```

## Tracks API

### Creating Tracks

```python
# Simple track
track = sdk.tracks.create(title="Project", priority="high")

# Track with TrackBuilder
track = sdk.tracks.builder() \
    .title("OAuth Integration") \
    .priority("high") \
    .with_spec(
        overview="Add OAuth 2.0 support",
        requirements=[("Google OAuth", "must-have")]
    ) \
    .with_plan_phases([
        ("Phase 1", ["Setup OAuth (2h)", "Configure (1h)"])
    ]) \
    .create()
```

### Querying Tracks

```python
# Get all tracks
all_tracks = sdk.tracks.all()

# Get specific track
track = sdk.tracks.get("track-20241216-120000")

# Get features for a track
features = sdk.features.where(track_id=track.track_id)
```

## Sessions API

### Session Management

```python
# Get all sessions
sessions = sdk.sessions.all()

# Get current session
current = sdk.sessions.current()

# Get specific session
session = sdk.sessions.get("session-abc-123")
```

### Activity Tracking

```python
# Track custom activity
sdk.track_activity(
    feature_id="feature-001",
    activity="Chose PostgreSQL over MongoDB for better transactions"
)
```

## Status API

```python
# Get current status
status = sdk.status()

print(f"Current session: {status.current_session}")
print(f"Active features: {status.active_features}")
print(f"Total features: {status.total_features}")
print(f"Progress: {status.progress}%")
```

## Graph Operations

### Relationships

```python
# Add edge between features
sdk.features.add_edge(
    from_id="feature-001",
    to_id="feature-002",
    relationship="blocks"
)

# Get dependencies
deps = sdk.features.get_dependencies("feature-001")

# Get blocking features
blocking = sdk.features.get_blocking("feature-001")
```

### Graph Queries

```python
# Query with CSS selectors
blocked = sdk.features.query('[data-status="blocked"]')
high_priority = sdk.features.query('[data-priority="high"]')

# Graph traversal
path = sdk.graph.shortest_path("feature-001", "feature-045")
transitive_deps = sdk.graph.transitive_deps("feature-001")
bottlenecks = sdk.graph.find_bottlenecks()
```

## Complete API Reference

For detailed API documentation with type signatures and docstrings, see the Python source code in `src/python/htmlgraph/sdk.py`.
