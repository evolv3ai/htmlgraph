# HtmlGraph for Gemini

**MANDATORY instructions for Google Gemini AI agents working with HtmlGraph projects.**

---

## 📚 REQUIRED READING - DO THIS FIRST

**→ READ [AGENTS.md](./AGENTS.md) BEFORE USING HTMLGRAPH**

The AGENTS.md file contains ALL core documentation:
- ✅ **Python SDK Quick Start** - REQUIRED installation and usage
- ✅ **Deployment Instructions** - How to use `deploy-all.sh`
- ✅ **API & CLI Alternatives** - When SDK isn't available
- ✅ **Best Practices** - MUST-FOLLOW patterns for AI agents
- ✅ **Complete Workflow Examples** - Copy these patterns
- ✅ **API Reference** - Full method documentation

**DO NOT proceed without reading AGENTS.md first.**

---

## Gemini-Specific REQUIREMENTS

### ABSOLUTE RULE: Use SDK, Never Direct File Edits

**CRITICAL: NEVER use file operations on `.htmlgraph/` HTML files.**

❌ **FORBIDDEN:**
```python
# NEVER DO THIS
Write('/path/to/.htmlgraph/features/feature-123.html', ...)
Edit('/path/to/.htmlgraph/sessions/session-456.html', ...)
```

✅ **REQUIRED - Use SDK:**
```python
from htmlgraph import SDK

# ALWAYS initialize with agent="gemini"
sdk = SDK(agent="gemini")

# Get project summary (DO THIS at session start)
print(sdk.summary(max_items=10))

# Create features (USE builder pattern)
feature = sdk.features.create("Implement Search") \
    .set_priority("high") \
    .add_steps([
        "Design search UI",
        "Add search endpoint",
        "Implement indexing"
    ]) \
    .save()

# Update features (USE context manager for auto-save)
with sdk.features.edit(feature.id) as f:
    f.status = "in-progress"
    f.agent_assigned = "gemini"
```

### Gemini Extension Integration

The HtmlGraph Gemini extension is located at `packages/gemini-extension/`.

**Installation:**
```bash
# Development
cd packages/gemini-extension
# Load as unpacked extension in Gemini

# Production
# Extension marketplace distribution (TBD)
```

**Extension Files:**
- `gemini-extension.json` - Extension manifest
- `skills/` - Gemini-specific skills
- `commands/` - Slash commands (auto-generated from YAML)

---

## Commands Available in Gemini

All HtmlGraph commands are available in Gemini through the extension:

- `/htmlgraph:start` - Start session with project context
- `/htmlgraph:status` - Check current status
- `/htmlgraph:plan` - Smart planning workflow
- `/htmlgraph:spike` - Create research spike
- `/htmlgraph:recommend` - Get strategic recommendations
- `/htmlgraph:end` - End session with summary

**→ Full command reference in [AGENTS.md](./AGENTS.md)**

---

## Platform Differences

### Gemini vs Claude Code

| Feature | Gemini | Claude Code |
|---------|--------|-------------|
| SDK Access | ✅ Full | ✅ Full |
| Slash Commands | ✅ Via Extension | ✅ Via Plugin |
| Dashboard | ✅ Browser | ✅ Browser |
| CLI Integration | ✅ Same | ✅ Same |

**Both platforms use the same:**
- Python SDK (`htmlgraph` package)
- REST API (port 8080)
- CLI commands (`uv run htmlgraph`)
- HTML file format

---

## Integration Pattern

```python
# Gemini Code Assist workflow
def gemini_workflow():
    """Example workflow for Gemini agents."""
    from htmlgraph import SDK

    # 1. Initialize with Gemini identifier
    sdk = SDK(agent="gemini")

    # 2. Get recommendations
    recs = sdk.recommend_next_work(agent_count=1)
    if recs:
        print(f"Recommended: {recs[0]['title']}")

    # 3. Get next task
    task = sdk.next_task(priority="high", auto_claim=True)

    if task:
        print(f"Working on: {task.title}")

        # 4. Complete work
        with sdk.features.edit(task.id) as f:
            for i, step in enumerate(f.steps):
                if not step.completed:
                    # Do the work...
                    step.completed = True
                    step.agent = "gemini"
                    break

        print("Step completed!")
```

---

## Troubleshooting

### Extension Not Loading

Check extension status in Gemini settings:
```
Gemini Settings → Extensions → HtmlGraph
```

### Commands Not Available

Regenerate commands from YAML:
```bash
cd packages/gemini-extension
uv run python ../common/generators/generate_commands.py
# Reload extension
```

### SDK Import Errors

Ensure htmlgraph is installed:
```bash
uv pip install htmlgraph
# or
pip install htmlgraph
```

---

## Documentation

- **Main Guide**: [AGENTS.md](./AGENTS.md) - Complete AI agent documentation
- **Deployment**: [AGENTS.md#deployment--release](./AGENTS.md#deployment--release)
- **SDK Reference**: `docs/SDK_FOR_AI_AGENTS.md`
- **Extension Code**: `packages/gemini-extension/`

---

## Updates

The Gemini extension version is synchronized with the main package:

```bash
# Version updated by deployment script
./scripts/deploy-all.sh 0.7.1

# Manual update
# Edit: packages/gemini-extension/gemini-extension.json
```

---

**→ For complete documentation, see [AGENTS.md](./AGENTS.md)**
