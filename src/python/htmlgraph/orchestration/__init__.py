"""Orchestration utilities for multi-agent coordination."""

from .headless_spawner import AIResult, HeadlessSpawner
from .task_coordination import (
    delegate_with_id,
    generate_task_id,
    get_results_by_task_id,
    parallel_delegate,
    save_task_results,
    validate_and_save,
)

__all__ = [
    # Headless AI spawning
    "HeadlessSpawner",
    "AIResult",
    # Task coordination
    "delegate_with_id",
    "generate_task_id",
    "get_results_by_task_id",
    "parallel_delegate",
    "save_task_results",
    "validate_and_save",
]
