"""
Documentation schema version management.

This module defines version compatibility rules for HtmlGraph documentation files.
"""

from dataclasses import dataclass


@dataclass
class DocVersion:
    """Documentation schema version."""

    version: int  # Schema version (1, 2, 3)
    package_version: str  # Minimum package version (e.g., "0.20.0")
    breaking_changes: list[str]
    migration_required: bool = False


# Version compatibility matrix
DOC_VERSIONS = {
    1: DocVersion(
        version=1,
        package_version="0.1.0",
        breaking_changes=[],
        migration_required=False,
    ),
    2: DocVersion(
        version=2,
        package_version="0.20.0",
        breaking_changes=[
            "AGENTS.md structure changed to use Jinja2 templates",
            "Removed root-level CLAUDE.md/GEMINI.md (moved to .htmlgraph/docs/)",
        ],
        migration_required=True,
    ),
}


def get_current_doc_version() -> int:
    """Get current documentation schema version for this package."""
    return 2  # Current version


def is_compatible(user_version: int, package_version: int) -> bool:
    """Check if user's doc version is compatible with package.

    Args:
        user_version: User's documentation schema version
        package_version: Package's required documentation schema version

    Returns:
        True if compatible (supports N-1 versions)
    """
    return user_version >= package_version - 1  # Support N-1 versions
