# Code Hygiene - Mandatory Quality Standards

**CRITICAL: Always fix ALL errors with every commit, regardless of when they were introduced.**

## Philosophy

Maintaining clean, error-free code is non-negotiable. Every commit should reduce technical debt, not accumulate it.

## Rules

1. **Fix All Errors Before Committing**
   - Run all linters (ruff, mypy) before every commit
   - Fix ALL errors, even pre-existing ones from previous sessions
   - Never commit with unresolved type errors, lint warnings, or test failures

2. **No "I'll Fix It Later" Mentality**
   - Errors compound over time
   - Pre-existing errors are YOUR responsibility when you touch related code
   - Clean as you go - leave code better than you found it

3. **Deployment Blockers**
   - The `deploy-all.sh` script blocks on:
     - Mypy type errors
     - Ruff lint errors
     - Test failures
   - This is intentional - maintain quality gates

4. **Why This Matters**
   - **Prevents Error Accumulation** - Small issues don't become large problems
   - **Better Code Hygiene** - Clean code is easier to maintain
   - **Faster Development** - No time wasted debugging old errors
   - **Professional Standards** - Production-grade code quality

## Workflow

```bash
# Before every commit:
1. uv run ruff check --fix
2. uv run ruff format
3. uv run mypy src/
4. uv run pytest

# Only commit when ALL checks pass
git commit -m "..."
```

**Remember: Fixing errors immediately is faster than letting them accumulate.**
