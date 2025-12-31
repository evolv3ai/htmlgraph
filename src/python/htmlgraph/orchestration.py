"""
Orchestration helpers for reliable parallel task coordination.

Provides Task ID pattern for retrieving results from parallel delegations.
"""

import time
import uuid
from datetime import datetime, timedelta
from typing import Any

from htmlgraph.sdk import SDK


def generate_task_id() -> str:
    """
    Generate unique task ID for traceability.

    Returns:
        Unique task ID (e.g., "task-a3f8b29c")
    """
    return f"task-{uuid.uuid4().hex[:8]}"


def delegate_with_id(
    description: str,
    prompt: str,
    subagent_type: str = "general-purpose",
) -> tuple[str, str]:
    """
    Delegate task with unique ID for result retrieval.

    Args:
        description: Human-readable task description
        prompt: Task instructions for subagent
        subagent_type: Type of subagent to use

    Returns:
        tuple[task_id, enhanced_prompt]: Unique identifier and enhanced prompt

    Example:
        task_id, enhanced_prompt = delegate_with_id(
            "Implement authentication",
            "Add JWT auth to API...",
            "general-purpose"
        )
        # Orchestrator calls: Task(prompt=enhanced_prompt, ...)
        results = get_results_by_task_id(sdk, task_id)
    """
    task_id = generate_task_id()

    # Inject task ID and reporting instructions into prompt
    enhanced_prompt = f"""
TASK_ID: {task_id}
TASK_DESCRIPTION: {description}

{prompt}

🔴 CRITICAL - Report Results with Task ID:
After completing the task, save your findings to HtmlGraph with the task ID in the title:

```python
from htmlgraph import SDK
import os

# Set agent name for proper attribution
os.environ['HTMLGRAPH_AGENT'] = '{subagent_type}'
sdk = SDK(agent='{subagent_type}')

# Create spike with task ID in title
spike = sdk.spikes.create('Results: {task_id} - {description}')
spike.set_findings(\"\"\"
# Task: {description}
# Task ID: {task_id}

## Summary
[Brief overview of what was accomplished]

## Details
[Detailed findings, changes made, etc.]

## Files Modified
[List of files changed]

## Status
[Success/Partial/Failed with explanation]
\"\"\").save()

print(f"✅ Results saved with task ID: {task_id}")
```
"""

    # Note: Actual Task() tool call should be done by orchestrator
    # This function just prepares the prompt and returns the task_id
    # The orchestrator will call: Task(prompt=enhanced_prompt, description=f"{task_id}: {description}")

    return task_id, enhanced_prompt


def get_results_by_task_id(
    sdk: SDK,
    task_id: str,
    timeout: int = 60,
    poll_interval: int = 2,
) -> dict[str, Any]:
    """
    Retrieve task results by task ID with polling.

    Polls HtmlGraph spikes for results with task ID in title.
    Works with parallel tasks - each has unique ID.

    Args:
        sdk: HtmlGraph SDK instance
        task_id: Task ID returned by delegate_with_id()
        timeout: Maximum seconds to wait for results
        poll_interval: Seconds between polling attempts

    Returns:
        Results dict with:
        - success: bool
        - task_id: str
        - spike_id: str (if found)
        - findings: str (if found)
        - error: str (if not found)

    Example:
        results = get_results_by_task_id(sdk, "task-a3f8b29c", timeout=120)
        if results["success"]:
            print(results["findings"])
    """
    deadline = datetime.utcnow() + timedelta(seconds=timeout)
    attempts = 0

    while datetime.utcnow() < deadline:
        attempts += 1

        # Get all spikes and search for task ID in title
        spikes = sdk.spikes.all()
        matching = [s for s in spikes if task_id in s.title]

        if matching:
            spike = matching[0]
            # Access findings attribute (available on Spike nodes)
            findings = getattr(spike, "findings", None)
            return {
                "success": True,
                "task_id": task_id,
                "spike_id": spike.id,
                "title": spike.title,
                "findings": findings,
                "attempts": attempts,
            }

        # Wait before next poll
        time.sleep(poll_interval)

    # Timeout - no results found
    return {
        "success": False,
        "task_id": task_id,
        "error": f"No results found for task {task_id} within {timeout}s",
        "attempts": attempts,
    }


def parallel_delegate(
    sdk: SDK,
    tasks: list[dict[str, str]],
    timeout: int = 120,
) -> dict[str, dict[str, Any]]:
    """
    Coordinate multiple parallel tasks with result retrieval.

    Args:
        sdk: HtmlGraph SDK instance
        tasks: List of task dicts with keys: description, prompt, subagent_type
        timeout: Maximum seconds to wait for all results

    Returns:
        Dict mapping task_id to results for each task

    Example:
        results = parallel_delegate(sdk, [
            {"description": "Implement auth", "prompt": "...", "subagent_type": "general-purpose"},
            {"description": "Write tests", "prompt": "...", "subagent_type": "general-purpose"},
            {"description": "Update docs", "prompt": "...", "subagent_type": "general-purpose"},
        ])

        for task_id, result in results.items():
            print(f"{task_id}: {result['findings']}")
    """
    # Generate task IDs and enhanced prompts
    task_mapping = {}
    for task in tasks:
        task_id, enhanced_prompt = delegate_with_id(
            task["description"],
            task["prompt"],
            task.get("subagent_type", "general-purpose"),
        )
        task_mapping[task_id] = {
            "description": task["description"],
            "prompt": enhanced_prompt,
            "subagent_type": task.get("subagent_type", "general-purpose"),
        }

    # Note: Orchestrator should spawn all Task() calls here in parallel
    # This function returns the mapping for orchestrator to use

    # Wait for all results
    results = {}
    for task_id in task_mapping:
        results[task_id] = get_results_by_task_id(sdk, task_id, timeout=timeout)

    return results
