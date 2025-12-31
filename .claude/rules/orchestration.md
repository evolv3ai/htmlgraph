# Orchestration Rules - Delegation Over Direct Execution

**CRITICAL: When operating in orchestrator mode, you MUST delegate ALL operations except a minimal set of strategic activities.**

## Core Philosophy

**You don't know the outcome before running a tool.** What looks like "one bash call" often becomes 2, 3, 4+ calls when handling failures, conflicts, hooks, or errors. Delegation preserves strategic context by isolating tactical execution in subagent threads.

## Operations You MUST Delegate

**ALL operations EXCEPT:**
- `Task()` - Delegation itself
- `AskUserQuestion()` - Clarifying requirements with user
- `TodoWrite()` - Tracking work items
- SDK operations - Creating features, spikes, bugs, analytics

**Everything else MUST be delegated**, including:

### 1. Git Operations - ALWAYS DELEGATE
- ❌ NEVER run git commands directly (add, commit, push, branch, merge)
- ✅ ALWAYS delegate to subagent with error handling

**Why?** Git operations cascade unpredictably:
- Commit hooks may fail (need fix + retry)
- Conflicts may occur (need resolution + retry)
- Push may fail (need pull + merge + retry)
- Tests may fail in hooks (need fix + retry)

**Context cost comparison:**
```
Direct execution: 7+ tool calls
  git add → commit fails (hook) → fix code → commit → push fails → pull → push

Delegation: 2 tool calls
  Task(delegate git workflow) → Read result
```

**Delegation pattern:**
```python
Task(
    prompt="""
    Commit and push changes:
    Files: CLAUDE.md, SKILL.md, git-commit-push.sh
    Message: "docs: enforce strict git delegation in orchestrator directives"

    Steps:
    1. git add [files]
    2. git commit -m "message"
    3. git push origin main
    4. Handle any errors (pre-commit hooks, conflicts, etc)

    🔴 CRITICAL - Report Results to HtmlGraph:
    [include SDK save pattern here]
    """,
    subagent_type="general-purpose"
)
```

### 2. Code Changes - DELEGATE Unless Trivial
- ❌ Multi-file edits
- ❌ Implementation requiring research
- ❌ Changes with testing requirements
- ✅ Single-line typo fixes (OK to do directly)

### 3. Research & Exploration - ALWAYS DELEGATE
- ❌ Large codebase searches (multiple Grep/Glob calls)
- ❌ Understanding unfamiliar systems
- ❌ Documentation research
- ✅ Single file quick lookup (OK to do directly)

### 4. Testing & Validation - ALWAYS DELEGATE
- ❌ Running test suites
- ❌ Debugging test failures
- ❌ Quality gate validation
- ✅ Checking test command exists (OK to do directly)

### 5. Build & Deployment - ALWAYS DELEGATE
- ❌ Build processes
- ❌ Package publishing
- ❌ Environment setup
- ✅ Checking deployment script exists (OK to do directly)

### 6. File Operations - DELEGATE Complex Operations
- ❌ Batch file operations (multiple files)
- ❌ Large file reading/writing
- ❌ Complex file transformations
- ✅ Reading single config file (OK to do directly)
- ✅ Writing single small file (OK to do directly)

### 7. Analysis & Computation - DELEGATE Heavy Work
- ❌ Performance profiling
- ❌ Large-scale analysis
- ❌ Complex calculations
- ✅ Simple status checks (OK to do directly)

## Why Strict Delegation Matters

**1. Context Preservation**
- Each tool call consumes tokens
- Failed operations consume MORE tokens
- Cascading failures consume MOST tokens
- Delegation isolates failure to subagent context

**2. Parallel Efficiency**
- Multiple subagents can work simultaneously
- Orchestrator stays available for decisions
- Higher throughput on independent tasks

**3. Error Isolation**
- Subagent handles retries and recovery
- Orchestrator receives clean success/failure
- No pollution of strategic context

**4. Cognitive Clarity**
- Orchestrator maintains high-level view
- Subagents handle tactical details
- Clear separation of concerns

## Decision Framework

Ask yourself:
1. **Will this likely be one tool call?**
   - If uncertain → DELEGATE
   - If certain → MAY do directly

2. **Does this require error handling?**
   - If yes → DELEGATE

3. **Could this cascade into multiple operations?**
   - If yes → DELEGATE

4. **Is this strategic (decisions) or tactical (execution)?**
   - Strategic → Do directly
   - Tactical → DELEGATE

## Orchestrator Reflection System

When orchestrator mode is enabled (strict), you'll receive reflections after direct tool execution:

```
ORCHESTRATOR REFLECTION: You executed code directly.

Ask yourself:
- Could this have been delegated to a subagent?
- Would parallel Task() calls have been faster?
- Is a work item tracking this effort?
- What if this operation fails - how many retries will consume context?
```

Use these reflections to adjust your delegation habits.

## Integration with HtmlGraph SDK

Always use SDK to track orchestration activities:

```python
from htmlgraph import SDK
sdk = SDK(agent='orchestrator')

# Track what you delegate
feature = sdk.features.create("Implement authentication") \
    .set_priority("high") \
    .add_steps([
        "Research existing auth patterns (delegated to explorer)",
        "Implement OAuth flow (delegated to coder)",
        "Add tests (delegated to test-runner)",
        "Commit changes (delegated to general-purpose)"
    ]) \
    .save()

# Spawn subagents with tracked context
explorer = sdk.spawn_explorer(
    task="Find all auth-related code",
    scope="src/",
    questions=["What library is used?", "Where is validation?"]
)

Task(
    prompt=explorer["prompt"],
    description=explorer["description"],
    subagent_type=explorer["subagent_type"]
)
```

**See:** `packages/claude-plugin/skills/htmlgraph-orchestrator/SKILL.md` for complete orchestrator patterns

## Task ID Pattern for Parallel Coordination

**Problem:** Timestamp-based lookup cannot distinguish parallel task results.

**Solution:** Generate unique task ID for each delegation.

### Helper Functions

HtmlGraph provides orchestration helpers in `htmlgraph.orchestration`:

```python
from htmlgraph.orchestration import delegate_with_id, get_results_by_task_id

# Generate task ID and enhanced prompt
task_id, prompt = delegate_with_id(
    "Implement authentication",
    "Add JWT auth to API endpoints...",
    "general-purpose"
)

# Delegate (orchestrator calls Task tool)
Task(
    prompt=prompt,
    description=f"{task_id}: Implement authentication",
    subagent_type="general-purpose"
)

# Retrieve results by task ID
results = get_results_by_task_id(sdk, task_id, timeout=120)
if results["success"]:
    print(results["findings"])
```

### Parallel Task Coordination

```python
from htmlgraph.orchestration import delegate_with_id, get_results_by_task_id

# Spawn 3 parallel tasks
auth_id, auth_prompt = delegate_with_id("Implement auth", "...", "general-purpose")
test_id, test_prompt = delegate_with_id("Write tests", "...", "general-purpose")
docs_id, docs_prompt = delegate_with_id("Update docs", "...", "general-purpose")

# Delegate all in parallel (single message, multiple Task calls)
Task(prompt=auth_prompt, description=f"{auth_id}: Implement auth")
Task(prompt=test_prompt, description=f"{test_id}: Write tests")
Task(prompt=docs_prompt, description=f"{docs_id}: Update docs")

# Retrieve results independently (order doesn't matter)
auth_results = get_results_by_task_id(sdk, auth_id)
test_results = get_results_by_task_id(sdk, test_id)
docs_results = get_results_by_task_id(sdk, docs_id)
```

**Benefits:**
- Works with parallel delegations
- Full traceability (Task → task_id → spike → findings)
- Timeout handling with polling
- Independent result retrieval

## Git Workflow Patterns

### Orchestrator Pattern (REQUIRED)

When operating as orchestrator, delegate ALL git operations:

```python
# ✅ CORRECT - Delegate git workflow to subagent
Task(
    prompt="""
    Commit and push changes to git:

    Files to commit: [list files or use 'all changes']
    Commit message: "chore: update session tracking"

    Steps:
    1. Run ./scripts/git-commit-push.sh "chore: update session tracking" --no-confirm
    2. If that script doesn't exist, use manual git workflow:
       - git add [files]
       - git commit -m "message"
       - git push origin main
    3. Handle any errors (pre-commit hooks, conflicts, push failures)
    4. Retry with fixes if needed

    Report final status: success or failure with details.

    🔴 CRITICAL - Track in HtmlGraph:
    After successful commit, update the active feature/spike with completion status.
    """,
    subagent_type="general-purpose"
)

# Then read subagent result and continue orchestration
```

**Why delegate?** Git operations cascade unpredictably:
- Pre-commit hooks may fail → need code fix → retry commit
- Push may fail due to conflicts → need pull → merge → retry push
- Tests may fail in hooks → need debugging → fix → retry

**Context cost:**
- Direct execution: 5-10+ tool calls (with failures and retries)
- Delegation: 2 tool calls (Task + result review)
