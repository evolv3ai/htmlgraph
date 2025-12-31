"""
Unified PostToolUse Hook - Parallel Event Tracking + Orchestrator Reflection

This module provides a unified PostToolUse hook that runs both event tracking
and orchestrator reflection in parallel using asyncio.

Architecture:
- Runs event tracking and orchestrator reflection simultaneously
- Event tracking logs tool usage to session events
- Orchestrator reflection provides delegation suggestions
- Returns combined response with all feedback

Performance:
- ~40-50% faster than sequential execution
- Single Python process (no subprocess overhead)
- Parallel execution via asyncio.gather()
"""

import asyncio
import json
import os
import sys
from typing import Any

from htmlgraph.hooks.event_tracker import track_event
from htmlgraph.hooks.orchestrator_reflector import orchestrator_reflect


async def run_event_tracking(
    hook_type: str, hook_input: dict[str, Any]
) -> dict[str, Any]:
    """
    Run event tracking (async wrapper).

    Args:
        hook_type: "PostToolUse" or "Stop"
        hook_input: Hook input with tool execution details

    Returns:
        Event tracking response: {"continue": True, "hookSpecificOutput": {...}}
    """
    try:
        loop = asyncio.get_event_loop()

        # Run in thread pool since it involves I/O
        return await loop.run_in_executor(
            None,
            track_event,
            hook_type,
            hook_input,
        )
    except Exception:
        # Graceful degradation - allow on error
        return {"continue": True}


async def run_orchestrator_reflection(hook_input: dict[str, Any]) -> dict[str, Any]:
    """
    Run orchestrator reflection (async wrapper).

    Args:
        hook_input: Hook input with tool execution details

    Returns:
        Reflection response: {"continue": True, "hookSpecificOutput": {...}}
    """
    try:
        loop = asyncio.get_event_loop()

        # Run in thread pool
        return await loop.run_in_executor(
            None,
            orchestrator_reflect,
            hook_input,
        )
    except Exception:
        # Graceful degradation - allow on error
        return {"continue": True}


async def posttooluse_hook(
    hook_type: str, hook_input: dict[str, Any]
) -> dict[str, Any]:
    """
    Unified PostToolUse hook - runs both tracking and reflection in parallel.

    Args:
        hook_type: "PostToolUse" or "Stop"
        hook_input: Hook input with tool execution details

    Returns:
        Claude Code standard format:
        {
            "continue": True,
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": "Combined feedback"
            }
        }
    """
    # Run both in parallel using asyncio.gather
    event_response, reflection_response = await asyncio.gather(
        run_event_tracking(hook_type, hook_input),
        run_orchestrator_reflection(hook_input),
    )

    # Combine responses (both should return continue=True)
    # Event tracking is async and shouldn't block
    # Reflection provides optional guidance

    # Collect all guidance
    guidance_parts = []

    # Event tracking guidance (e.g., drift warnings)
    if "hookSpecificOutput" in event_response:
        ctx = event_response["hookSpecificOutput"].get("additionalContext", "")
        if ctx:
            guidance_parts.append(ctx)

    # Orchestrator reflection
    if "hookSpecificOutput" in reflection_response:
        ctx = reflection_response["hookSpecificOutput"].get("additionalContext", "")
        if ctx:
            guidance_parts.append(ctx)

    # Build unified response
    response: dict[str, Any] = {"continue": True}  # PostToolUse never blocks

    if guidance_parts:
        response["hookSpecificOutput"] = {
            "hookEventName": "PostToolUse",
            "additionalContext": "\n".join(guidance_parts),
        }

    return response


def main() -> None:
    """Hook entry point for script wrapper."""
    # Check environment override
    if os.environ.get("HTMLGRAPH_DISABLE_TRACKING") == "1":
        print(json.dumps({"continue": True}))
        sys.exit(0)

    # Determine hook type from environment
    hook_type = os.environ.get("HTMLGRAPH_HOOK_TYPE", "PostToolUse")

    # Read tool input from stdin
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError:
        hook_input = {}

    # Run hook with parallel execution
    result = asyncio.run(posttooluse_hook(hook_type, hook_input))

    # Output response
    print(json.dumps(result))
    sys.exit(0)


if __name__ == "__main__":
    main()
