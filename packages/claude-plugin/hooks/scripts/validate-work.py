#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "htmlgraph",
# ]
# ///
"""
Pre-Work Validation Hook (GUIDANCE MODE)

Provides guidance for HtmlGraph workflow - NEVER blocks tool execution.

Core Principles:
1. SDK is the ONLY interface to .htmlgraph/ - never direct Write/Edit
2. ALL spikes (auto-generated and manual) are for planning only
3. Features/bugs/chores are for code implementation

Philosophy:
- Hooks GUIDE agents with suggestions, they do NOT block
- Agents decide how to proceed based on guidance
- Trust the agent to make good decisions
- Blocking breaks flow and frustrates users

Hook Input (stdin): JSON with tool call details
Hook Output (stdout): JSON with guidance {"decision": "allow", "guidance": "...", "suggestion": "..."}
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Optional


def load_validation_config() -> dict:
    """Load validation config with defaults."""
    config_path = Path(__file__).parent.parent.parent / "config" / "validation-config.json"

    if config_path.exists():
        try:
            with open(config_path) as f:
                return json.load(f)
        except Exception:
            pass

    # Minimal fallback config
    return {
        "always_allow": {
            "tools": ["Read", "Glob", "Grep", "LSP"],
            "bash_patterns": ["^git status", "^git diff", "^ls", "^cat"]
        },
        "sdk_commands": {
            "patterns": ["^uv run htmlgraph ", "^htmlgraph "]
        }
    }


def is_always_allowed(tool: str, params: dict, config: dict) -> bool:
    """Check if tool is always allowed (read-only operations)."""
    # Always-allow tools
    if tool in config.get("always_allow", {}).get("tools", []):
        return True

    # Read-only Bash patterns
    if tool == "Bash":
        command = params.get("command", "")
        for pattern in config.get("always_allow", {}).get("bash_patterns", []):
            if re.match(pattern, command):
                return True

    return False


def is_direct_htmlgraph_write(tool: str, params: dict) -> tuple[bool, str]:
    """Check if attempting direct write to .htmlgraph/ (always denied)."""
    if tool not in ["Write", "Edit", "Delete", "NotebookEdit"]:
        return False, ""

    file_path = params.get("file_path", "")
    if ".htmlgraph/" in file_path or file_path.startswith(".htmlgraph/"):
        return True, file_path

    return False, ""


def is_sdk_command(tool: str, params: dict, config: dict) -> bool:
    """Check if Bash command is an SDK command."""
    if tool != "Bash":
        return False

    command = params.get("command", "")
    for pattern in config.get("sdk_commands", {}).get("patterns", []):
        if re.match(pattern, command):
            return True

    return False


def is_code_operation(tool: str, params: dict, config: dict) -> bool:
    """Check if operation modifies code."""
    # Direct file operations
    if tool in config.get("code_operations", {}).get("tools", []):
        return True

    # Code-modifying Bash commands
    if tool == "Bash":
        command = params.get("command", "")
        for pattern in config.get("code_operations", {}).get("bash_patterns", []):
            if re.match(pattern, command):
                return True

    return False


def get_active_work_item() -> Optional[dict]:
    """Get active work item using SDK."""
    try:
        from htmlgraph import SDK

        sdk = SDK()
        active = sdk.get_active_work_item()
        return active
    except Exception:
        # If SDK fails, assume no active work item
        return None


def validate_tool_call(tool: str, params: dict, config: dict) -> dict:
    """
    Validate tool call and return GUIDANCE (never blocks).

    Returns:
        dict: {"decision": "allow", "guidance": "...", "suggestion": "..."}
              All operations are ALLOWED - guidance is informational only.
    """
    # Step 1: Read-only tools - no guidance needed
    if is_always_allowed(tool, params, config):
        return {
            "decision": "allow",
            "guidance": None
        }

    # Step 2: Direct writes to .htmlgraph/ - provide SDK guidance
    is_htmlgraph_write, file_path = is_direct_htmlgraph_write(tool, params)
    if is_htmlgraph_write:
        return {
            "decision": "allow",
            "guidance": "Direct writes to .htmlgraph/ bypass the SDK. Consider using SDK commands instead.",
            "suggestion": "Use SDK: uv run htmlgraph feature create"
        }

    # Step 3: Classify operation
    is_sdk_cmd = is_sdk_command(tool, params, config)
    is_code_op = is_code_operation(tool, params, config)

    # Step 4: Get active work item
    active = get_active_work_item()

    # Step 5: No active work item
    if active is None:
        if is_sdk_cmd:
            return {
                "decision": "allow",
                "guidance": "Creating work item via SDK"
            }

        if is_code_op or tool in ["Write", "Edit", "Delete"]:
            # Guide: suggest creating work item (but allow)
            return {
                "decision": "allow",
                "guidance": "No active work item. Consider creating one to track this work.",
                "suggestion": "uv run htmlgraph feature create 'Feature title'"
            }

        return {
            "decision": "allow",
            "guidance": None
        }

    # Step 6: Active work is a spike (planning phase)
    if active.get("type") == "spike":
        spike_id = active.get("id")

        if is_sdk_cmd:
            return {
                "decision": "allow",
                "guidance": f"Planning with spike {spike_id}"
            }

        if tool in ["Write", "Edit", "Delete", "NotebookEdit"] or is_code_op:
            # Guide: suggest creating feature (but allow)
            return {
                "decision": "allow",
                "guidance": f"Active spike ({spike_id}) is for planning. Consider creating a feature for implementation.",
                "suggestion": "uv run htmlgraph feature create 'Feature title'"
            }

        return {
            "decision": "allow",
            "guidance": None
        }

    # Step 7: Active work is feature/bug/chore - all good
    work_item_id = active.get("id")
    return {
        "decision": "allow",
        "guidance": f"Working on {work_item_id}"
    }


def main():
    """Main entry point."""
    try:
        # Read tool input from stdin
        tool_input = json.load(sys.stdin)

        tool = tool_input.get("tool", "")
        params = tool_input.get("params", {})

        # Load config
        config = load_validation_config()

        # Get guidance (never blocks)
        result = validate_tool_call(tool, params, config)

        # Output JSON with guidance
        print(json.dumps(result))

        # ALWAYS exit 0 - guidance mode never blocks
        sys.exit(0)

    except Exception as e:
        # Graceful degradation - allow on error
        print(json.dumps({
            "decision": "allow",
            "guidance": f"Validation hook error: {e}"
        }))
        sys.exit(0)


if __name__ == "__main__":
    main()
