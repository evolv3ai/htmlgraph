# Quick Start

Get up and running with HtmlGraph in 5 minutes.

## Initialize a Project

```bash
# Create a new directory for your graph
mkdir my-project
cd my-project

# Initialize HtmlGraph
htmlgraph init
```

This creates a `.htmlgraph/` directory with the following structure:

```
.htmlgraph/
├── features/       # Feature nodes
├── sessions/       # Session activity logs
├── tracks/         # Multi-feature tracks
├── events/         # Event log (JSONL)
└── index.db        # SQLite index (auto-generated)
```

## Using the SDK

### Basic Feature Creation

```python
from htmlgraph import SDK

# Initialize SDK (auto-discovers .htmlgraph directory)
sdk = SDK(agent="claude")

# Create a feature
feature = sdk.features.create(
    title="User Authentication",
    priority="high",
    steps=[
        "Create login endpoint",
        "Add JWT middleware",
        "Write tests"
    ]
)

print(f"Created feature: {feature.id}")
# Output: Created feature: feature-20241216-103045
```

### Query Features

```python
# Get all high-priority features
high_priority = sdk.features.where(priority="high")

# Get features by status
in_progress = sdk.features.where(status="in-progress")

# Get a specific feature
feature = sdk.features.get("feature-20241216-103045")
```

### Update Feature Status

```python
# Start working on a feature
feature.status = "in-progress"
feature.save()

# Complete a step
feature.steps[0].completed = True
feature.save()

# Mark feature as complete
feature.status = "done"
feature.save()
```

## Using the CLI

### Feature Management

```bash
# List all features
htmlgraph feature list

# Create a new feature
htmlgraph feature create "Add OAuth support" --priority high

# Start working on a feature
htmlgraph feature start feature-20241216-103045

# Mark a feature as complete
htmlgraph feature complete feature-20241216-103045
```

### Session Management

```bash
# View session status
htmlgraph status

# List all sessions
htmlgraph session list

# View session details
htmlgraph session show session-abc-123
```

### Dashboard

Launch the interactive dashboard:

```bash
htmlgraph serve
```

Then open [http://localhost:8080](http://localhost:8080) in your browser.

## Creating a Track

For multi-feature projects, create a track with spec and plan:

```python
from htmlgraph import SDK

sdk = SDK(agent="claude")

# Use TrackBuilder for complex tracks
track = sdk.tracks.builder() \
    .title("OAuth Integration") \
    .priority("high") \
    .with_spec(
        overview="Add OAuth 2.0 support for Google and GitHub",
        requirements=[
            ("Support Google OAuth", "must-have"),
            ("Support GitHub OAuth", "must-have"),
            ("JWT token management", "must-have")
        ],
        success_criteria=[
            "Users can sign in with Google",
            "Users can sign in with GitHub",
            "Tokens refresh automatically"
        ]
    ) \
    .with_plan_phases([
        ("Phase 1: OAuth Setup", [
            "Configure OAuth providers (2h)",
            "Set up redirect endpoints (1h)"
        ]),
        ("Phase 2: Implementation", [
            "Implement Google OAuth (4h)",
            "Implement GitHub OAuth (4h)",
            "Add JWT middleware (3h)"
        ]),
        ("Phase 3: Testing", [
            "Write integration tests (3h)",
            "Test with real providers (2h)"
        ])
    ]) \
    .create()

print(f"Created track: {track.track_id}")
# View at: .htmlgraph/tracks/{track.track_id}/index.html
```

## View Your Graph

All graph nodes are HTML files that you can open in any browser:

```bash
# Open a feature in your browser
open .htmlgraph/features/feature-20241216-103045.html

# Open a track
open .htmlgraph/tracks/track-20241216-120000/index.html

# Open the dashboard
open index.html
```

## Next Steps

- [Core Concepts](concepts.md) - Understand features, tracks, and sessions
- [User Guide](../guide/index.md) - In-depth guides for all features
- [API Reference](../api/index.md) - Complete SDK documentation
- [Examples](../examples/index.md) - Real-world use cases
