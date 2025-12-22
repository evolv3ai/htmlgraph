# HtmlGraph Tracker Skill for Codex CLI

This skill enables HtmlGraph tracking in OpenAI Codex CLI, ensuring proper activity attribution and continuous work tracking.

## Prerequisites

1. **Codex CLI** installed:
   ```bash
   npm install -g @openai/codex
   ```

2. **HtmlGraph** installed:
   ```bash
   uv pip install htmlgraph
   ```

3. **Skills enabled** in Codex:
   ```bash
   codex --enable skills
   ```

## Installation

### Option 1: Clone and Link (Recommended for Development)

```bash
# Clone the HtmlGraph repository
git clone https://github.com/Shakes-tzd/htmlgraph.git
cd htmlgraph

# Link the skill to Codex
codex skills link packages/codex-skill
```

### Option 2: Copy to Codex Skills Directory

```bash
# Create skills directory if it doesn't exist
mkdir -p ~/.codex/skills

# Copy the skill
cp -r packages/codex-skill ~/.codex/skills/htmlgraph-tracker
```

### Option 3: Install from GitHub

```bash
codex skills install https://github.com/Shakes-tzd/htmlgraph/tree/main/packages/codex-skill
```

## Usage

Once installed, Codex will automatically use this skill when working on HtmlGraph-tracked projects.

### Initialize HtmlGraph in Your Project

```bash
cd your-project
uv run htmlgraph init --install-hooks
```

### Start a Codex Session

```bash
codex
```

Codex will:
1. Detect the `.htmlgraph` directory
2. Load the htmlgraph-tracker skill
3. Remind you to check status and start features
4. Track your work continuously

### Manual Skill Invocation

You can also invoke the skill manually:

```bash
codex --skill htmlgraph-tracker
```

## What This Skill Does

The htmlgraph-tracker skill ensures Codex:

- ✅ Uses the **Python SDK** for all HtmlGraph operations (never direct file edits)
- ✅ **Checks status** at session start
- ✅ **Tracks all work** continuously, not just at the end
- ✅ **Marks steps complete** immediately after finishing them
- ✅ **Creates features** for non-trivial work using the decision framework
- ✅ **Verifies completion** before marking features done

## Key Features

### 1. SDK-First Approach
All operations use the HtmlGraph SDK via Bash:

```python
uv run python -c "
from htmlgraph import SDK
sdk = SDK(agent='codex')
with sdk.features.edit('feat-123') as f:
    f.steps[0].completed = True
"
```

### 2. Feature Creation Decision Framework
Automatic guidance on when to create features:
- >30 minutes? → Create feature
- 3+ files? → Create feature
- Needs tests? → Create feature
- Simple fix? → Direct commit OK

### 3. Continuous Tracking
Reminds you to:
- Start features before coding
- Mark steps complete as you finish them
- Update progress in real-time
- Complete features only when all steps are done

## Configuration

The skill works out of the box, but you can customize behavior by modifying `SKILL.md`:

```bash
# Edit the skill
code ~/.codex/skills/htmlgraph-tracker/SKILL.md
```

## Troubleshooting

### Skill Not Loading

Check if skills are enabled:
```bash
codex --enable skills
codex skills list
```

### HtmlGraph Not Found

Ensure HtmlGraph is installed in your environment:
```bash
uv pip install htmlgraph
uv run htmlgraph --version
```

### Skill Not Activating

Verify the skill is in the correct location:
```bash
ls ~/.codex/skills/htmlgraph-tracker/SKILL.md
```

## Differences from Claude Code Plugin

The Codex skill is similar to the Claude Code plugin but:
- Uses `agent='codex'` instead of `agent='claude'`
- No plugin hooks (uses manual skill invocation)
- Relies on Codex's skill system instead of Claude's hooks
- Same SDK, same workflow, same benefits!

## Documentation

- **HtmlGraph SDK Guide**: https://github.com/Shakes-tzd/htmlgraph/blob/main/docs/SDK_FOR_AI_AGENTS.md
- **HtmlGraph Project**: https://github.com/Shakes-tzd/htmlgraph
- **Codex CLI Docs**: https://developers.openai.com/codex/cli
- **Codex Skills**: https://developers.openai.com/codex/skills/

## Support

For issues or questions:
- **HtmlGraph Issues**: https://github.com/Shakes-tzd/htmlgraph/issues
- **Codex Issues**: https://github.com/openai/codex/issues

## License

MIT - Same as HtmlGraph

## Contributing

Contributions welcome! Please ensure any changes:
1. Follow the SDK-first principle
2. Maintain the decision framework
3. Keep skill focused on tracking (not implementation)
4. Test with actual Codex CLI

---

**Note**: This skill follows the dogfooding principle - we use HtmlGraph to track HtmlGraph development, so this skill represents our actual workflow.
