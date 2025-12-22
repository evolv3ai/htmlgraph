# HtmlGraph Development Workflow

## Definition of "Done"

A feature is considered **DONE** only when ALL of the following criteria are met:

### 1. Implementation Complete
- [ ] All implementation steps in the feature HTML file are marked as completed
- [ ] Code is written and follows project conventions
- [ ] No placeholder code or TODO comments remain
- [ ] All related files have been modified/created

### 2. Testing Complete
**Automated Tests Required:**
- [ ] **UI Changes**: Playwright test added to `tests/python/test_dashboard_ui.py`
  - Test demonstrates feature works in browser
  - Test covers primary user interaction
  - Run: `uv run pytest tests/python/test_dashboard_ui.py --headed`
- [ ] **Backend Changes**: pytest test added to `tests/python/test_*.py`
  - Unit tests for new functions/classes
  - Integration tests for API endpoints
  - Run: `uv run pytest tests/python/`
- [ ] **All Tests Pass**: `uv run pytest` exits with code 0

**Manual Testing:**
- [ ] Manual testing performed for primary use case
- [ ] Edge cases tested (if applicable)
- [ ] Integration testing with related features
- [ ] No critical bugs remaining
- [ ] Test results documented

### 3. Attribution Verified
- [ ] Feature was marked "in-progress" BEFORE implementation started
- [ ] Current session has the feature in its "worked-on" list
- [ ] Feature has events attributed to it (verify with attribution validation)
- [ ] No significant work was misattributed to other features

### 4. Documentation Updated
- [ ] API changes documented (if applicable)
- [ ] User-facing changes documented
- [ ] Code comments added for non-obvious logic
- [ ] Examples updated (if applicable)

### 5. Quality Checks Passed
- [ ] No linter errors
- [ ] No type errors (if using type checking)
- [ ] Code builds successfully
- [ ] Server starts without errors (if applicable)

### 6. Review Complete
- [ ] Self-review performed
- [ ] All acceptance criteria from feature description met
- [ ] Feature demonstrates the intended behavior

### 7. Git Commit Required
- [ ] All changes committed to git
  ```bash
  git add .
  git commit -m "feat: <feature-title>

  Implements: <feature-id>

  🤖 Generated with Claude Code
  Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
  ```
- [ ] Commit message references feature ID
- [ ] No uncommitted changes: `git status` shows clean working tree
- [ ] Changes are on appropriate branch
- [ ] **Do NOT push** until user approves (unless explicitly requested)

**Commit Message Format:**
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation
- `test:` for test additions
- `refactor:` for code improvements

---

## Feature Creation Decision Framework

### When to Create a Feature vs Direct Implementation

Not all work requires feature tracking. Use this framework to decide:

### Decision Criteria

Create a **FEATURE** if ANY of these apply:

1. **Complexity**: Involves 3+ files OR requires architectural decisions
2. **Time**: Estimated >30 minutes of implementation time
3. **Scope**: Changes affect multiple components or systems
4. **Reversibility**: Difficult to revert (database schema, API contracts)
5. **Collaboration**: Multiple sessions or agents will work on it
6. **Attribution**: Work should be tracked for progress monitoring
7. **Testing**: Requires new automated tests (UI or backend)
8. **Documentation**: Needs user-facing or API documentation

Implement **DIRECTLY** if ALL of these apply:

1. **Simple**: Single file, obvious change
2. **Quick**: <30 minutes of work
3. **Isolated**: No cross-system impact
4. **Reversible**: Easy to undo with git revert
5. **Solo**: One person, one session
6. **Trivial**: Typo fixes, minor formatting, simple config changes
7. **No tests needed**: Change is self-evident
8. **No docs needed**: Change is internal/implementation detail

### Decision Tree

```
START: Received user request
  │
  ├─ Is this a bug in existing feature?
  │  ├─ YES → See "Bug Fix Workflow" below
  │  └─ NO → Continue
  │
  ├─ Will this take >30 minutes?
  │  ├─ YES → CREATE FEATURE
  │  └─ NO → Continue
  │
  ├─ Does this involve 3+ files?
  │  ├─ YES → CREATE FEATURE
  │  └─ NO → Continue
  │
  ├─ Requires new tests?
  │  ├─ YES → CREATE FEATURE
  │  └─ NO → Continue
  │
  ├─ Affects multiple systems/components?
  │  ├─ YES → CREATE FEATURE
  │  └─ NO → Continue
  │
  ├─ Hard to revert (schema, API)?
  │  ├─ YES → CREATE FEATURE
  │  └─ NO → Continue
  │
  ├─ Requires user documentation?
  │  ├─ YES → CREATE FEATURE
  │  └─ NO → IMPLEMENT DIRECTLY
```

### Examples

#### ✅ CREATE FEATURE:

1. **"Add user authentication"**
   - Why: Multi-file, >30min, tests needed, affects API, needs docs

2. **"Implement session comparison view"**
   - Why: New UI component, multiple files, Playwright tests needed

3. **"Add SQLite indexing for full-text search"**
   - Why: Architectural decision, database schema, multiple components

4. **"Fix attribution drift detection algorithm"**
   - Why: Complex logic, affects multiple systems, needs backend tests

5. **"Create pre-commit hook for workflow validation"**
   - Why: New tool integration, affects development workflow, needs docs

6. **"Refactor graph traversal performance"**
   - Why: Affects core system, needs benchmarks/tests, risk of regression

#### ❌ IMPLEMENT DIRECTLY:

1. **"Fix typo in README.md"**
   - Why: Single file, <5min, trivial, easily reversible

2. **"Add console.log for debugging"**
   - Why: Temporary, single line, no tests needed

3. **"Update CSS color value"**
   - Why: Single file, visual tweak, quick, easily reversible

4. **"Bump dependency version in pyproject.toml"**
   - Why: Single file, routine maintenance, no logic changes

5. **"Add missing import statement"**
   - Why: Obvious fix, single line, no architectural impact

6. **"Reformat code with Black"**
   - Why: Automated tool, no logic changes, easily reversible

### Thresholds Reference

| Criterion | Feature Required | Direct OK |
|-----------|------------------|-----------|
| **Time** | >30 minutes | <30 minutes |
| **Files** | 3+ files | 1-2 files |
| **Complexity** | Architectural decisions | Obvious changes |
| **Testing** | New tests needed | No new tests |
| **Documentation** | User/API docs needed | Internal only |
| **Reversibility** | Hard to revert | Easy git revert |
| **Sessions** | Multi-session work | Single session |
| **Impact** | Cross-component | Single component |

### Edge Cases

**When in doubt, CREATE A FEATURE.** Over-tracking is better than losing attribution.

**Special cases:**
- **Research tasks**: Create feature if >1 hour or affects decisions
- **Bug investigations**: Create feature if root cause unclear
- **Refactoring**: Create feature if touches >3 files or changes architecture
- **Dependency updates**: Direct if patch/minor, feature if major version
- **Configuration changes**: Direct if single value, feature if affects behavior

### Quick Decision Guide

Ask yourself:
1. "Would I want to track progress on this?" → Feature
2. "Will this take multiple attempts to get right?" → Feature
3. "Could someone else need to continue this work?" → Feature
4. "Is this a one-liner fix?" → Direct
5. "Am I unsure?" → Feature (default to tracking)

---

## Pre-Commit Hook

HtmlGraph includes an optional pre-commit hook that reminds developers to create/start features for non-trivial work.

### Installation

The pre-commit hook is automatically installed at `.git/hooks/pre-commit` when you first set up the project. To install it manually:

```bash
# The hook is already at .git/hooks/pre-commit
# Just ensure it's executable
chmod +x .git/hooks/pre-commit
```

### Behavior

The hook runs before every commit and:

1. **Checks if HtmlGraph is initialized** - Skips if `.htmlgraph/` doesn't exist
2. **Checks for active features** - Runs `htmlgraph feature list --status in-progress`
3. **Shows appropriate message:**
   - If features are active: Displays list of active features
   - If no features are active: Shows reminder to create/start a feature
4. **Always allows the commit** - This is a reminder, not enforcement

### Example Output

**With active features:**
```
✓ HtmlGraph: 2 active feature(s)

ID                        Status       Priority   Title
================================================================================
feature-auth              in-progress  high       User Authentication
feature-dashboard         in-progress  medium     Dashboard UI
```

**Without active features:**
```
⚠️  HtmlGraph Feature Reminder
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
No active features found. Did you forget to start one?

For non-trivial work, consider:
  1. Create feature: (use Python API or dashboard)
  2. Start feature: htmlgraph feature start <feature-id>

Quick decision:
  • >30 min work? → Create feature
  • 3+ files? → Create feature
  • Needs tests? → Create feature
  • Simple fix? → Direct commit OK

To disable this reminder: git config htmlgraph.precommit false
To bypass once: git commit --no-verify
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Proceeding with commit...
```

### Configuration

**Disable the hook permanently:**
```bash
git config htmlgraph.precommit false
```

**Re-enable the hook:**
```bash
git config --unset htmlgraph.precommit
```

**Bypass for a single commit:**
```bash
git commit --no-verify -m "your message"
```

### Philosophy

The pre-commit hook is designed as a **gentle reminder**, not enforcement:

- ✅ Educates developers about the feature workflow
- ✅ Surfaces the decision framework at the right time
- ✅ Shows what features are currently active
- ✅ Always allows commits (never blocks)
- ❌ Not a strict gatekeeper
- ❌ Doesn't prevent direct commits for trivial work

The hook respects developer judgment - if you're making a quick fix or trivial change, you can proceed with the commit. For non-trivial work, the reminder helps ensure proper attribution and tracking.

---

## Claude Code Session Checklist

Use this checklist to ensure consistent workflow quality and proper attribution throughout your session.

### 🚀 Session Startup Checklist

**Run IMMEDIATELY at session start:**

- [ ] **Activate htmlgraph-tracker skill** - Use Skill tool to activate (mandatory)
- [ ] **Check project status** - Run `htmlgraph status`
- [ ] **Review active features** - Run `htmlgraph feature list --status in-progress`
- [ ] **Read session context** - Review previous session summary if provided
- [ ] **Verify tracking** - Confirm HtmlGraph is tracking (check `.htmlgraph/` exists)
- [ ] **Greet user** - Provide brief status update and ask what to work on

**Commands to run:**
```bash
# 1. Check status
htmlgraph status

# 2. List active features
htmlgraph feature list --status in-progress

# 3. View sessions
htmlgraph session list
```

**Decision point:** Should this request become a feature?
- Use the Feature Creation Decision Framework above
- **When in doubt, CREATE A FEATURE**
- If creating feature: Use Python API or create via API endpoint
- If starting existing feature: `htmlgraph feature start <feature-id>`

---

### 💻 During Work Checklist

**Throughout the session:**

- [ ] **Feature is started** - Verify `htmlgraph feature list` shows feature as "in-progress"
- [ ] **Mark steps complete** - Update feature steps via API as you complete them
- [ ] **Document decisions** - Record architectural decisions and tradeoffs
- [ ] **Test incrementally** - Don't wait until the end to test
- [ ] **Watch for drift** - If drift warning appears, assess if feature scope is correct
- [ ] **Use descriptive tool descriptions** - All Bash commands should have clear descriptions
- [ ] **Keep user informed** - Provide progress updates, explain what you're doing

**When making significant decisions:**
```bash
# Track decision with context
htmlgraph track "Decision" "Chose X over Y because Z"
```

**If work drifts to different scope:**
- Consider if current feature scope is correct
- May need to create a new related feature
- Use `htmlgraph feature primary <id>` to change attribution

**Progress tracking:**
- Mark feature steps complete via API as you finish them
- Don't batch step completions - mark immediately
- Document blockers or dependencies in feature content

---

### ✅ Session Ending Checklist

**Before marking feature complete or ending session:**

#### 1. Testing & Validation
- [ ] **Run all tests** - `uv run pytest` exits with code 0
- [ ] **UI tests pass** (if UI changes) - `uv run pytest tests/python/test_dashboard_ui.py`
- [ ] **Backend tests pass** (if backend changes) - `uv run pytest tests/python/`
- [ ] **Manual testing done** - Primary use case works as expected
- [ ] **No errors in console** - Check for warnings/errors
- [ ] **Server starts cleanly** (if applicable) - `htmlgraph serve`

#### 2. Attribution Validation
- [ ] **Feature started before work** - Verify feature was "in-progress" during implementation
- [ ] **Attribution validated** - Run `htmlgraph session validate-attribution <feature-id>`
- [ ] **No suspicious drift** - Check drift warnings were addressed
- [ ] **Session linked** - Feature should appear in session's "worked-on" list

#### 3. Code Quality
- [ ] **All feature steps complete** - Check via dashboard or API
- [ ] **No TODO comments** - Remove or track as follow-up
- [ ] **No debug code** - Remove console.logs, debug prints
- [ ] **Linter passes** - Run project linter if available
- [ ] **Type checks pass** (if applicable) - Run type checker

#### 4. Documentation
- [ ] **Code comments added** - For non-obvious logic
- [ ] **API changes documented** - Update docs if API changed
- [ ] **Examples updated** (if applicable) - Keep examples current
- [ ] **User-facing docs** (if applicable) - README, WORKFLOW, etc.

#### 5. Git Commit
- [ ] **All changes staged** - `git add .`
- [ ] **Proper commit message** - Follow format (see below)
- [ ] **Feature ID in message** - `Implements: <feature-id>`
- [ ] **Clean working tree** - `git status` shows nothing uncommitted
- [ ] **DO NOT push** - Unless user explicitly requests it

**Commit message format:**
```bash
git commit -m "$(cat <<'EOF'
<type>: <title>

Implements: <feature-id>

<description of what was done>

🤖 Generated with Claude Code
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

Types: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`

#### 6. Feature Completion
- [ ] **Mark feature complete** - `htmlgraph feature complete <feature-id>`
- [ ] **Update epic steps** (if part of epic) - Mark epic step complete via API
- [ ] **Verify in dashboard** - Open http://localhost:8080 and check status

#### 7. Final Verification
- [ ] **Read feature description** - Confirm everything implemented
- [ ] **Check acceptance criteria** - All criteria met
- [ ] **Review modified files** - No unintended changes
- [ ] **Feature demonstrates behavior** - Works as intended

---

### 📋 Quick Reference Card

**START → WORK → END**

**START:**
1. Activate skill
2. Check status
3. Start feature
4. Decide: create feature or direct?

**WORK:**
1. Track progress (mark steps)
2. Document decisions
3. Test incrementally
4. Watch for drift

**END:**
1. Run tests (all pass)
2. Validate attribution
3. Commit with feature ID
4. Mark feature complete
5. Update epic (if applicable)

**REMEMBER:**
- Feature started BEFORE coding
- Tests BEFORE marking done
- Commit BEFORE completing
- Push ONLY if user requests

---

## Bug Fix Workflow for "Done" Features

When a bug is found in a feature that was previously marked "done":

### Step 1: Assess Impact
- Is this a critical bug that breaks core functionality? → **High priority**
- Is this a minor issue or edge case? → **Medium/Low priority**
- Does this require reopening the original feature or creating a new bug?

### Step 2: Decision Tree

**If bug was found within same session:**
1. Keep feature as "in-progress"
2. Fix the bug
3. Re-test completely
4. Don't mark "done" until ALL criteria met

**If bug was found in a later session:**
1. Create a new bug item: `htmlgraph feature create --type bug`
2. Link bug to original feature using edge relationships
3. Start the bug: `htmlgraph feature start <bug-id>`
4. Fix and test
5. Complete the bug: `htmlgraph feature complete <bug-id>`
6. Original feature stays "done" (history preserved)

**If bug reveals incomplete implementation:**
1. Re-open the original feature:
   ```bash
   curl -X PATCH http://localhost:8080/api/features/<feature-id> \
     -H "Content-Type: application/json" \
     -d '{"status": "in-progress"}'
   ```
2. Document why it's being reopened in activity log
3. Fix the issue
4. Re-complete with full done criteria

---

## Pre-Completion Checklist

Before running `htmlgraph feature complete <feature-id>`, verify:

```bash
# 1. Check attribution
htmlgraph session validate-attribution <feature-id>

# 2. Verify all steps completed
curl http://localhost:8080/api/features/<feature-id> | grep '"completed": false'
# Should return no results

# 3. Check for linter errors
# (Run project-specific lint command)

# 4. Verify server/tests pass
# (Run project-specific test command)

# 5. Review the feature in dashboard
# Open http://localhost:8080 and inspect the feature
```

**Manual checklist:**
- [ ] Read through the feature description - is everything implemented?
- [ ] Review all modified files - any debug code left behind?
- [ ] Check git status - any uncommitted changes?
- [ ] Test the primary use case - does it work as expected?
- [ ] Test error cases - does it fail gracefully?
- [ ] Review session activity log - is work properly attributed?

---

## Attribution Validation

Attribution validation ensures work is correctly tracked:

### Command: `htmlgraph session validate-attribution <feature-id>`

**What it checks:**
1. Feature is linked to at least one session
2. Feature has activity events attributed to it
3. Recent work on feature files is attributed correctly
4. No suspicious drift patterns (all work going to other features)

**Example output:**
```
✓ Feature 'feature-server-auto-reload' validation:
  - Linked to 1 session(s)
  - 156 events attributed
  - Last activity: 2025-12-17 04:15:42
  - Attribution health: GOOD

⚠ Potential issues:
  - 3 file modifications had drift score > 0.8 (may be misattributed)
```

---

## Workflow Best Practices

### Starting Work
1. **Always start features before implementation:**
   ```bash
   htmlgraph feature start <feature-id>
   ```
2. This ensures automatic attribution works correctly
3. If you forget, use `session link` retroactively

### During Work
1. Keep feature descriptions updated
2. Mark steps as complete incrementally
3. Document decisions in activity log
4. Test frequently, not just at the end

### Completing Work
1. Run pre-completion checklist
2. Verify all done criteria
3. Use API to mark complete (triggers validation)
4. Verify attribution before moving on

### Post-Completion
1. If bugs found, follow bug fix workflow
2. Don't reopen features lightly - create bugs instead
3. Preserve historical accuracy of sessions

---

## Common Pitfalls

### ❌ **Don't:**
- Mark features "done" without testing
- Start coding without marking feature "in-progress"
- Skip attribution validation
- Reopen features for minor bugs (create bug items instead)
- Work on features outside of session tracking

### ✅ **Do:**
- Follow the complete done criteria
- Start features properly before coding
- Create separate bug items for post-release issues
- Document workflow deviations
- Use attribution validation regularly

---

## Command Reference

```bash
# Feature lifecycle
htmlgraph feature create <title>            # Create new feature
htmlgraph feature start <feature-id>        # Mark in-progress (before coding!)
htmlgraph feature complete <feature-id>     # Mark done (after checklist)

# Attribution management
htmlgraph session link <session-id> <feature-id> --bidirectional
htmlgraph session validate-attribution <feature-id>

# Debugging attribution
htmlgraph session list                      # See all sessions
htmlgraph feature list --status in-progress # Check WIP
htmlgraph status                           # Overall status
```

---

## Example Workflow

```bash
# 1. Start working on a feature
$ htmlgraph feature start feature-xyz

# 2. Implement the feature
$ # ... write code, test, iterate ...

# 3. Pre-completion check
$ htmlgraph session validate-attribution feature-xyz
✓ Attribution looks good

$ curl http://localhost:8080/api/features/feature-xyz | jq '.steps[] | select(.completed == false)'
# No incomplete steps

# 4. Mark complete
$ htmlgraph feature complete feature-xyz

# 5. Later: Bug found
$ htmlgraph feature create "Bug: XYZ edge case" --type bug --links feature-xyz
$ htmlgraph feature start bug-xyz-edge-case
$ # ... fix bug ...
$ htmlgraph feature complete bug-xyz-edge-case
```

---

Last updated: 2025-12-17
