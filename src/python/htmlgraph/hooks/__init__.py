"""
HtmlGraph hooks package.

This package contains the hook logic for HtmlGraph tracking integration
with Claude Code and other AI coding assistants.

All hooks use a unified architecture:
- Logic lives in package modules (not scripts)
- Parallel execution where possible (asyncio.gather)
- Unified error handling and response format
- Easy testing via direct imports
- Deployed via package updates
"""

from htmlgraph.hooks.posttooluse import posttooluse_hook
from htmlgraph.hooks.pretooluse import pretooluse_hook

# Git hooks that can be installed
AVAILABLE_HOOKS = [
    "pre-commit",
    "post-commit",
    "pre-push",
    "post-checkout",
    "post-merge",
]

__all__ = [
    "pretooluse_hook",
    "posttooluse_hook",
    "AVAILABLE_HOOKS",
]
