# Dashboard

The HtmlGraph dashboard provides visual exploration of your graph with Kanban boards, timelines, and graph visualizations.

## Accessing the Dashboard

### Local Files

Open `index.html` directly in any browser:

```bash
open index.html
```

### Development Server

Run the built-in server for live updates:

```bash
htmlgraph serve
```

Then open [http://localhost:8080](http://localhost:8080) in your browser.

## Dashboard Views

### Kanban Board

The default view shows features organized by status:

```
┌─────────┬──────────────┬─────────┬──────┐
│  TODO   │ IN PROGRESS  │ BLOCKED │ DONE │
├─────────┼──────────────┼─────────┼──────┤
│ Task 1  │   Task 3     │ Task 5  │Task 8│
│ Task 2  │   Task 4     │         │Task 9│
│         │              │         │      │
└─────────┴──────────────┴─────────┴──────┘
```

**Features:**

- Drag and drop to change status
- Color-coded by priority
- Progress bars show completion
- Click to view details

### Graph View

Visualize relationships between features:

```
      ┌─────────┐
      │Feature 1│
      └────┬────┘
           │ blocks
      ┌────▼────┐      related to
      │Feature 2├───────────────┐
      └─────────┘               │
                           ┌────▼────┐
                           │Feature 3│
                           └─────────┘
```

**Features:**

- Force-directed layout
- Relationship types shown as edge labels
- Zoom and pan
- Click nodes to view details

### Timeline View

See activity over time:

```
Day 1:  ████████░░░░░░  50% (Feature 1)
Day 2:  ████████████░░  75% (Feature 1)
Day 3:  ██████████████ 100% (Feature 1)
        ██░░░░░░░░░░░░  15% (Feature 2)
```

**Features:**

- Daily/weekly/monthly views
- Progress tracking
- Session markers
- Agent attribution

### Session History

View all past sessions:

```
Session ABC-123 | claude | 2h 34m | 2024-12-16
  - User Authentication (80% → 100%)
  - 12 activities logged

Session XYZ-456 | gemini | 1h 15m | 2024-12-15
  - Database Schema (0% → 40%)
  - 7 activities logged
```

**Features:**

- Filter by agent
- Filter by date range
- View session details
- Session summaries

## Navigation

### Search

Use the search bar to find features:

```
Search: "auth" ─────┐
                    ▼
Results:
  - User Authentication (in-progress)
  - OAuth Setup (todo)
  - Auth Middleware (done)
```

### Filters

Filter features by:

- **Status**: todo, in-progress, blocked, done
- **Priority**: low, medium, high, critical
- **Agent**: claude, gemini, codex, etc.
- **Track**: Features belonging to a specific track

### Sort

Sort features by:

- **Priority**: High to low
- **Created**: Newest first
- **Updated**: Most recently updated
- **Completion**: Progress percentage

## Dashboard Customization

### Layout

Choose your preferred layout:

```bash
htmlgraph serve --layout kanban    # Kanban board (default)
htmlgraph serve --layout graph     # Graph visualization
htmlgraph serve --layout timeline  # Timeline view
htmlgraph serve --layout list      # Simple list
```

### Theme

Switch between themes:

- **Dark**: High contrast, easy on eyes (default)
- **Light**: Clean, bright
- **Terminal**: Matrix-style green on black
- **Custom**: Define your own CSS

### Stats Panel

The stats panel shows:

- Total features
- Features by status
- Features by priority
- Average completion time
- Active agents

## Interactive Features

### Drag and Drop

Drag features between status columns:

```
TODO            IN PROGRESS
┌────────┐      ┌────────┐
│Task 1  │  →   │Task 1  │
└────────┘      └────────┘
```

### Quick Actions

Right-click features for:

- Start working (changes status to in-progress)
- Mark complete (changes status to done)
- Block (changes status to blocked)
- Edit details
- Delete feature

### Inline Editing

Click any field to edit:

- Feature title
- Priority
- Steps (add/remove/check)
- Properties

## Keyboard Shortcuts

- `n`: Create new feature
- `s`: Focus search
- `/`: Command palette
- `1-4`: Switch views (Kanban, Graph, Timeline, List)
- `h`: Show help
- `Esc`: Close modals

## Mobile View

The dashboard is fully responsive:

- Swipe between status columns
- Tap to expand feature details
- Simplified graph view
- Touch-friendly controls

## Browser Compatibility

Works in all modern browsers:

- Chrome/Edge (recommended)
- Firefox
- Safari
- Mobile browsers (iOS/Android)

No server required - runs entirely in the browser.

## Advanced Features

### Graph Algorithms

Run graph analysis:

```javascript
// Find bottlenecks (features blocking many others)
const bottlenecks = graph.findBottlenecks();

// Find critical path (longest dependency chain)
const criticalPath = graph.findCriticalPath();

// Find orphaned features (no relationships)
const orphans = graph.findOrphans();
```

### Export

Export your graph:

- **JSON**: Complete graph data
- **CSV**: Feature list
- **SVG**: Graph visualization
- **Markdown**: Feature list with links

### Embed

Embed the dashboard in other sites:

```html
<iframe src="htmlgraph/index.html" width="100%" height="600"></iframe>
```

## Next Steps

- [Features & Tracks Guide](features-tracks.md) - Creating and managing work
- [Sessions Guide](sessions.md) - Understanding session tracking
- [API Reference](../api/index.md) - Complete SDK documentation
