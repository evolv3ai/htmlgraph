# Dogfooding Context - Using HtmlGraph to Build HtmlGraph

**THIS PROJECT USES HTMLGRAPH TO DEVELOP HTMLGRAPH.**

We are dogfooding our own tool. The `.htmlgraph/` directory in this repo tracks:
- ✅ **Features** - New capabilities we're building (e.g., strategic analytics, track planning)
- ✅ **Sessions** - Our development work (tracked automatically via hooks)
- ✅ **Tracks** - Multi-feature initiatives (e.g., "Planning Workflow")
- ✅ **Development progress** - What's done, in-progress, and planned

## What This Means for AI Agents

### 1. Dual Purpose - Examples ARE Real Usage

When you see workflows in this project:
- ✅ They're **real examples** of HtmlGraph usage
- ✅ They're **actual tracking** of HtmlGraph development
- ✅ Learn from them for YOUR projects

```python
# This IS real - we use this to track HtmlGraph development
sdk = SDK(agent="claude")
feature = sdk.features.create("Add deployment automation")  # Real feature!
```

### 2. General vs Project-Specific

**GENERAL WORKFLOWS** (package these for all users):
- ✅ Feature creation and tracking → SDK already provides this
- ✅ Track planning with TrackBuilder → SDK provides this
- ✅ Strategic analytics (recommend_next_work, find_bottlenecks) → SDK provides this
- ✅ Session management → Hooks provide this
- ⚠️ **Deployment automation** → Should package `deploy-all.sh` pattern
- ⚠️ **Memory file sync** → Should package `sync_memory_files.py` pattern

**PROJECT-SPECIFIC** (only for HtmlGraph development):
- ❌ Publishing to PyPI (specific to HtmlGraph package)
- ❌ The specific features in `.htmlgraph/features/` (our roadmap)
- ❌ Phase 1-6 implementation plan (our project structure)

### 3. Workflows to Package for Users

**TODO - Extract these into the package:**
1. **Deployment Script Pattern** - Generalize `deploy-all.sh` for any Python package
2. **Memory File Sync** - Include `sync_memory_files.py` in the package
3. **Project Initialization** - `htmlgraph init` should set up `.htmlgraph/`
4. **Pre-commit Hooks** - Package the git hooks for automatic tracking

**Current Status:**
- ✅ SDK provides feature/track/analytics workflows
- ⚠️ Deployment scripts are project-specific (need to generalize)
- ⚠️ Memory sync is project-specific (need to package)

### 4. How to Read This Codebase

When you see `.htmlgraph/` in this repo:
- **It's a live example** - This is real usage, not a demo
- **It's our roadmap** - Features here are what we're building
- **Learn from it** - Use these patterns in your projects

**Example:**
```bash
# In THIS repo
ls .htmlgraph/features/
# → feature-20251221-211348.html  # Real feature we're tracking
# → feat-5f0fca41.html            # Another real feature

# In YOUR project (after using HtmlGraph)
ls .htmlgraph/features/
# → Your features will look the same!
```
