"""
Task Validator - Validate that Task results were saved to HtmlGraph.

This module provides PostToolUse validation for the Task tool, checking that
subagents actually saved their findings to HtmlGraph as instructed.

Architecture:
- Detects Task tool calls in PostToolUse hook
- Checks tool response for evidence of saving
- Scans .htmlgraph/ directory for recent file modifications
- Provides warning if no evidence found (non-blocking)

Usage:
    from htmlgraph.hooks.task_validator import validate_task_results

    result = validate_task_results(tool_name, tool_response)
    # Returns: {"continue": True, "hookSpecificOutput": {...}}
"""

import re
import time
from pathlib import Path
from typing import Any


def has_save_evidence_in_text(text: str) -> bool:
    """
    Check if text contains evidence of HtmlGraph save operations.

    Args:
        text: Tool response text to check

    Returns:
        True if save evidence found, False otherwise
    """
    # Keywords that indicate saving occurred
    save_patterns = [
        r"\.save\(\)",  # .save() method call
        r"spike.*saved",  # "spike saved" or similar
        r"saved.*spike",  # "saved spike" or similar
        r"htmlgraph",  # Mentions htmlgraph
        r"sdk\.spikes",  # SDK usage
        r"\.htmlgraph/spikes/",  # File path mentions
        r"spk-[a-f0-9]{8}",  # Spike ID pattern
        r"findings.*saved",  # "findings saved"
        r"saved.*findings",  # "saved findings"
    ]

    text_lower = text.lower()
    return any(re.search(pattern, text_lower) for pattern in save_patterns)


def find_recent_htmlgraph_files(max_age_seconds: int = 60) -> list[Path]:
    """
    Find recently modified files in .htmlgraph/ directory.

    Args:
        max_age_seconds: Maximum age of files to consider (default: 60)

    Returns:
        List of recently modified file paths
    """
    htmlgraph_dir = Path.cwd() / ".htmlgraph"
    if not htmlgraph_dir.exists():
        return []

    recent_files = []
    current_time = time.time()

    # Check spikes, sessions, and events directories
    for subdir in ["spikes", "sessions", "events"]:
        dir_path = htmlgraph_dir / subdir
        if not dir_path.exists():
            continue

        for file_path in dir_path.rglob("*"):
            if not file_path.is_file():
                continue

            # Check file modification time
            mtime = file_path.stat().st_mtime
            age = current_time - mtime

            if age <= max_age_seconds:
                recent_files.append(file_path)

    return recent_files


def validate_task_results(
    tool_name: str, tool_response: dict[str, Any]
) -> dict[str, Any]:
    """
    Validate that Task tool results were saved to HtmlGraph.

    Args:
        tool_name: Name of the tool that was executed
        tool_response: Tool response data

    Returns:
        Hook response with warning if no save evidence found:
        {
            "continue": True,  # Never blocks
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "systemMessage": "..."  # Warning if applicable
            }
        }
    """
    # Only process Task tool calls
    if tool_name != "Task":
        return {"continue": True}

    # Extract response text
    result_text = ""
    if isinstance(tool_response, dict):
        result_text = tool_response.get("result", "")
        if not result_text:
            # Try alternative keys
            result_text = str(tool_response.get("output", ""))
    else:
        result_text = str(tool_response)

    # Check for save evidence in response text
    has_text_evidence = has_save_evidence_in_text(result_text)

    # Check for recently modified files
    recent_files = find_recent_htmlgraph_files(max_age_seconds=60)
    has_file_evidence = len(recent_files) > 0

    # If evidence found, all good
    if has_text_evidence or has_file_evidence:
        evidence_details = []
        if has_text_evidence:
            evidence_details.append("text mentions saving")
        if has_file_evidence:
            evidence_details.append(
                f"{len(recent_files)} recent file(s) in .htmlgraph/"
            )

        return {
            "continue": True,
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": (
                    f"✅ Task results appear to be saved to HtmlGraph "
                    f"({', '.join(evidence_details)})"
                ),
            },
        }

    # No evidence found - provide warning (but don't block)
    warning_message = """
⚠️  Task Validation Warning - No HtmlGraph Save Evidence Detected

The Task tool completed, but there's no evidence that results were saved to HtmlGraph.

What to check:
1. Did the subagent call SDK.spikes.create() and .save()?
2. Are there any recent files in .htmlgraph/spikes/?
3. Did the subagent encounter errors when trying to save?

Recommendations:
- Review the Task output above for save confirmation
- Check .htmlgraph/spikes/ directory manually
- Consider re-running with explicit save instructions

Note: This is a warning, not a blocker. The Task has completed.
"""

    return {
        "continue": True,  # Never block on PostToolUse
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "systemMessage": warning_message.strip(),
        },
    }
