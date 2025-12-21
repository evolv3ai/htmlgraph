---
name: htmlgraph-tracker
description: HtmlGraph session tracking and documentation skill. Activated automatically at session start to ensure proper activity attribution, feature awareness, and documentation habits. Use when working with HtmlGraph-enabled projects, when drift warnings appear, or when the user asks about tracking features or sessions.
---

# HtmlGraph Tracker Skill

Use this skill when HtmlGraph is tracking the session to ensure proper activity attribution and documentation. This skill should be activated at session start via the SessionStart hook.

## When to Activate This Skill

- At the start of every session when HtmlGraph plugin is enabled
- When the user asks about tracking, features, or session management
- When drift detection warnings appear
- When the user mentions htmlgraph, features, sessions, or activity tracking
- When discussing work attribution or documentation

**Trigger keywords:** htmlgraph, feature tracking, session tracking, drift detection, activity log, work attribution, feature status, session management

---

## Core Responsibilities

### 1. **NEVER Edit .htmlgraph Files Directly** (CRITICAL)

**ABSOLUTE RULE: You must NEVER use Read, Write, or Edit tools on `.htmlgraph/` HTML files.**

This is the most important architectural principle of HtmlGraph. AI agents MUST use the SDK, API, or CLI to ensure all HTML is validated through Pydantic + justhtml.

❌ **FORBIDDEN:**
```python
# NEVER DO THIS
Write('/path/to/.htmlgraph/features/feature-123.html', ...)
Edit('/path/to/.htmlgraph/sessions/session-456.html', ...)
with open('.htmlgraph/features/feature-123.html', 'w') as f:
    f.write('<html>...</html>')
```

✅ **REQUIRED - Use SDK (recommended):**
```python
from htmlgraph import SDK

sdk = SDK(agent="claude")

# Create features
feature = sdk.features.create("Title") \
    .set_priority("high") \
    .add_steps(["Step 1", "Step 2"]) \
    .save()

# Edit features (auto-saves)
with sdk.features.edit("feature-123") as f:
    f.status = "done"
```

✅ **ALTERNATIVE - Use API/CLI:**
```bash
# API
curl -X POST localhost:8080/api/features -d '{"title": "..."}'
curl -X PATCH localhost:8080/api/features/feat-123 -d '{"status": "done"}'

# CLI
htmlgraph feature create/start/complete/step-complete
htmlgraph track new/list/spec/plan
htmlgraph session start/end
```

**Why this matters:**
- Direct file edits bypass Pydantic validation
- Bypass justhtml HTML generation (can create invalid HTML)
- Break the SQLite index sync
- Skip event logging and activity tracking
- Can corrupt graph structure and relationships

**Exception:** You MAY read `.htmlgraph/` files to view content, but NEVER write or edit them.

**Documentation:** See `AGENTS.md` for complete SDK guide and best practices.

### 2. Feature Awareness
Always be aware of which feature(s) are currently in progress:
- Check active features at session start
- Reference the current feature when discussing work
- Alert if work appears to drift from the assigned feature

### 3. Step Completion (CRITICAL)
**Mark each step complete IMMEDIATELY after finishing it:**
- Use curl PATCH to `/api/features/<id>` with `{"complete_step": index}`
- Step 0 = first step, step 1 = second step (0-based indexing)
- Do NOT wait until all steps are done - mark each one as you finish
- See "How to Mark Steps Complete" section below for exact commands

### 4. Activity Attribution
HtmlGraph automatically tracks tool usage, but you should:
- Use descriptive summaries in Bash `description` parameter
- Reference feature IDs in commit messages
- Mention the feature context when starting new tasks

### 5. Documentation Habits
For every significant piece of work:
- Summarize what was done and why
- Note any decisions made and alternatives considered
- Record blockers or dependencies discovered

## Working with Features

**RECOMMENDED:** Use the Python SDK for AI agents (cleanest, most powerful)

### Python SDK (Recommended for AI Agents)

```python
from htmlgraph import SDK

# Initialize (auto-discovers .htmlgraph)
sdk = SDK(agent="claude")

# Create a feature
feature = sdk.features.create("User Authentication") \
    .set_priority("high") \
    .add_steps([
        "Create login endpoint",
        "Add JWT middleware",
        "Write tests"
    ]) \
    .save()

# Edit a feature (auto-saves!)
with sdk.features.edit(feature.id) as f:
    f.status = "in-progress"
    f.steps[0].completed = True

# Query features
todos = sdk.features.where(status="todo", priority="high")

# Get project summary
summary = sdk.summary()
print(summary)
```

### CLI (Alternative)

**IMPORTANT:** Always use `uv run` when running htmlgraph commands to ensure the correct environment.

```bash
# Check Current Status
uv run htmlgraph status
uv run htmlgraph feature list

# Start Working on a Feature
uv run htmlgraph feature start <feature-id>

# Set Primary Feature (when multiple are active)
uv run htmlgraph feature primary <feature-id>

# Complete a Feature
uv run htmlgraph feature complete <feature-id>
```

## Feature Creation Decision Framework

**CRITICAL**: Use this framework to decide when to create a feature vs implementing directly.

### Quick Decision Rule

Create a **FEATURE** if ANY apply:
- Estimated >30 minutes of work
- Involves 3+ files
- Requires new automated tests
- Affects multiple components
- Hard to revert (schema, API changes)
- Needs user/API documentation

Implement **DIRECTLY** if ALL apply:
- Single file, obvious change
- <30 minutes work
- No cross-system impact
- Easy to revert
- No tests needed
- Internal/trivial change

### Decision Tree (Quick Reference)

```
User request received
  ├─ Bug in existing feature? → See Bug Fix Workflow in WORKFLOW.md
  ├─ >30 minutes? → CREATE FEATURE
  ├─ 3+ files? → CREATE FEATURE
  ├─ New tests needed? → CREATE FEATURE
  ├─ Multi-component impact? → CREATE FEATURE
  ├─ Hard to revert? → CREATE FEATURE
  └─ Otherwise → IMPLEMENT DIRECTLY
```

### Examples

**✅ CREATE FEATURE:**
- "Add user authentication" (multi-file, tests, docs)
- "Implement session comparison view" (new UI, Playwright tests)
- "Fix attribution drift algorithm" (complex, backend tests)

**❌ IMPLEMENT DIRECTLY:**
- "Fix typo in README" (single file, trivial)
- "Update CSS color" (single file, quick, reversible)
- "Add missing import" (obvious fix, no impact)

### Default Rule

**When in doubt, CREATE A FEATURE.** Over-tracking is better than losing attribution.

See `docs/WORKFLOW.md` for the complete decision framework with detailed criteria, thresholds, and edge cases.

## Session Workflow Checklist

**Use this checklist for EVERY session to ensure quality and proper attribution.**

### Session Start
- [ ] Activate this skill (done)
- [ ] Check status: `uv run htmlgraph status`
- [ ] Review active features
- [ ] Greet user with status update
- [ ] Decide: Create feature or implement directly? (use decision framework)
- [ ] Start feature: `uv run htmlgraph feature start <id>`

### During Work
- [ ] Feature marked "in-progress" before coding
- [ ] **CRITICAL: Mark each step complete IMMEDIATELY after finishing it** (see below)
- [ ] Document decisions with `uv run htmlgraph track`
- [ ] Test incrementally
- [ ] Watch for drift warnings

#### How to Mark Steps Complete

**IMPORTANT:** After finishing each step, mark it complete using curl:

```bash
# Mark step 0 (first step) as complete
curl -X PATCH http://localhost:8080/api/features/<feature-id> \
  -H "Content-Type: application/json" \
  -d '{"complete_step": 0}'

# Mark step 1 (second step) as complete
curl -X PATCH http://localhost:8080/api/features/<feature-id> \
  -H "Content-Type: application/json" \
  -d '{"complete_step": 1}'
```

**Step numbering is 0-based** (first step = 0, second step = 1, etc.)

**When to mark complete:**
- ✅ IMMEDIATELY after finishing a step
- ✅ Even if you continue working on the feature
- ✅ Before moving to the next step
- ❌ NOT at the end when all steps are done (too late!)

**Example workflow:**
1. Start feature: `uv run htmlgraph feature start feature-123`
2. Work on step 0 (e.g., "Design models")
3. **MARK STEP 0 COMPLETE** → `curl -X PATCH ...`
4. Work on step 1 (e.g., "Create templates")
5. **MARK STEP 1 COMPLETE** → `curl -X PATCH ...`
6. Continue until all steps done
7. Complete feature: `uv run htmlgraph feature complete feature-123`

### Session End (Before Completion)
- [ ] All tests pass: `uv run pytest`
- [ ] Validate attribution: `uv run htmlgraph session validate-attribution <feature-id>`
- [ ] All feature steps complete
- [ ] No debug code or TODOs
- [ ] Commit with feature ID
- [ ] Mark feature complete: `uv run htmlgraph feature complete <id>`
- [ ] Update epic step (if applicable)

**Full checklist:** See `docs/WORKFLOW.md` → "Claude Code Session Checklist"

## Handling Drift Warnings

When you see a drift warning like:
> Drift detected (0.74): Activity may not align with feature-self-tracking

Consider:
1. **Is this expected?** Sometimes work naturally spans multiple features
2. **Should you switch features?** Use `uv run htmlgraph feature primary <id>` to change attribution
3. **Is the feature scope wrong?** The feature's file patterns or keywords may need updating

## Session Continuity

At the start of each session:
1. Review previous session summary (if provided)
2. Note current feature progress
3. Identify what remains to be done
4. Ask the user what they'd like to work on

At the end of each session:
1. The SessionEnd hook will generate a summary
2. All activities are preserved in `.htmlgraph/sessions/`
3. Feature progress is updated automatically

## Best Practices

### Commit Messages
Include feature context:
```
feat(feature-id): Description of the change

- Details about what was done
- Why this approach was chosen

🤖 Generated with Claude Code
```

### Task Descriptions
When using Bash tool, always provide a description:
```bash
# Good - descriptive
Bash(description="Install dependencies for auth feature")

# Bad - no context
Bash(command="npm install")
```

### Decision Documentation
When making architectural decisions:

1. Track with `uv run htmlgraph track "Decision" "Chose X over Y because Z"`
2. Or note in the feature's HTML file under activity log

## Dashboard Access

View progress visually:
```bash
uv run htmlgraph serve
# Open http://localhost:8080
```

The dashboard shows:
- Kanban board with feature status
- Session history with activity logs
- Graph visualization of dependencies

## Key Files

- `.htmlgraph/features/` - Feature HTML files (the graph nodes)
- `.htmlgraph/sessions/` - Session HTML files with activity logs
- `index.html` - Dashboard (open in browser)

## Integration Points

HtmlGraph hooks track:
- **SessionStart**: Creates session, provides feature context
- **PostToolUse**: Logs every tool call with attribution
- **UserPromptSubmit**: Logs user queries
- **SessionEnd**: Finalizes session with summary

All data is stored as HTML files - human-readable, git-friendly, browser-viewable.
