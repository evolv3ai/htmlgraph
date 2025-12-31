"""
Task Enforcer - Auto-inject HtmlGraph save instructions into Task prompts.

This module provides PreToolUse enforcement for the Task tool, ensuring that
subagent prompts include instructions to save their findings to HtmlGraph.

Architecture:
- Detects Task tool calls in PreToolUse hook
- Checks if prompt already includes save instructions
- Auto-injects SDK save template if missing
- Returns updatedInput with modified prompt

Usage:
    from htmlgraph.hooks.task_enforcer import enforce_task_saving

    result = enforce_task_saving(tool_name, tool_params)
    # Returns: {"continue": True, "hookSpecificOutput": {"updatedInput": {...}}}
"""

from typing import Any


def has_save_instructions(prompt: str) -> bool:
    """
    Check if prompt already includes HtmlGraph save instructions.

    Args:
        prompt: Task prompt to check

    Returns:
        True if save instructions are present, False otherwise
    """
    # Keywords that indicate save instructions are already present
    save_keywords = [
        "sdk",
        "htmlgraph",
        ".save()",
        "spike",
        "report results",
        "save findings",
        "track results",
    ]

    prompt_lower = prompt.lower()
    return any(keyword in prompt_lower for keyword in save_keywords)


def inject_save_instructions(prompt: str, subagent_type: str = "haiku") -> str:
    """
    Inject HtmlGraph save instructions into Task prompt.

    Args:
        prompt: Original task prompt
        subagent_type: Type of subagent (default: "haiku")

    Returns:
        Modified prompt with save instructions appended
    """
    # Template to inject
    save_template = f"""

🔴 CRITICAL - Report Results to HtmlGraph:
After completing your research/analysis, you MUST save your findings using:

```python
from htmlgraph import SDK
sdk = SDK(agent='{subagent_type}')
spike = sdk.spikes.create('Your Task Summary Here')
spike.set_findings(\'\'\'
# Your Comprehensive Findings

## Summary
[Brief overview of what you discovered]

## Key Findings
- [Finding 1]
- [Finding 2]
- [Finding 3]

## Details
[Detailed analysis, code examples, etc.]

## Recommendations
[Action items or next steps]
\'\'\')
spike.save()
```

IMPORTANT:
- Replace 'Your Task Summary Here' with a concise description of your task
- Include ALL relevant findings in the set_findings() call
- This creates a permanent record that can be referenced later
- The spike will be saved to .htmlgraph/spikes/ directory
"""

    return prompt + save_template


def enforce_task_saving(tool_name: str, tool_params: dict[str, Any]) -> dict[str, Any]:
    """
    Enforce HtmlGraph result saving for Task tool calls.

    Args:
        tool_name: Name of the tool being called
        tool_params: Tool parameters (includes "prompt" for Task)

    Returns:
        Hook response with updatedInput if modifications needed:
        {
            "continue": True,
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "updatedInput": {...},  # Modified tool_params
                "additionalContext": "..."  # Optional guidance
            }
        }
    """
    # Only process Task tool calls
    if tool_name != "Task":
        return {"continue": True}

    # Get prompt from tool params
    prompt = tool_params.get("prompt", "")
    if not prompt:
        return {"continue": True}

    # Check if save instructions already present
    if has_save_instructions(prompt):
        return {"continue": True}

    # Detect subagent type from prompt context
    prompt_lower = prompt.lower()
    if "haiku" in prompt_lower:
        subagent_type = "haiku"
    elif "sonnet" in prompt_lower:
        subagent_type = "sonnet"
    elif "opus" in prompt_lower:
        subagent_type = "opus"
    else:
        subagent_type = "haiku"  # Default to haiku for most subagents

    # Inject save instructions
    modified_prompt = inject_save_instructions(prompt, subagent_type)

    # Create updated tool params
    updated_params = tool_params.copy()
    updated_params["prompt"] = modified_prompt

    # Return response with updatedInput
    return {
        "continue": True,
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "updatedInput": updated_params,
            "additionalContext": (
                "📝 Auto-injected HtmlGraph save instructions into Task prompt. "
                "Subagent will be reminded to save findings using SDK.spikes."
            ),
        },
    }
