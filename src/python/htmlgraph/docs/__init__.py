"""
Documentation version tracking and migration system with template-based user customization.
"""

from pathlib import Path

from htmlgraph import __version__
from htmlgraph.docs.docs_version import (
    DOC_VERSIONS,
    DocVersion,
    get_current_doc_version,
    is_compatible,
)
from htmlgraph.docs.metadata import DocsMetadata
from htmlgraph.docs.migrations import MIGRATIONS, MigrationScript, get_migration
from htmlgraph.docs.template_engine import DocTemplateEngine
from htmlgraph.docs.version_check import check_docs_version, upgrade_docs_interactive

__all__ = [
    "DOC_VERSIONS",
    "DocVersion",
    "get_current_doc_version",
    "is_compatible",
    "DocsMetadata",
    "MigrationScript",
    "MIGRATIONS",
    "get_migration",
    "check_docs_version",
    "upgrade_docs_interactive",
    "DocTemplateEngine",
    "get_agents_md",
    "sync_docs_to_file",
]


def get_agents_md(htmlgraph_dir: Path, platform: str = "claude") -> str:
    """Get AGENTS.md content with user customizations merged.

    Args:
        htmlgraph_dir: Path to .htmlgraph directory
        platform: Platform name (claude, gemini, etc.)

    Returns:
        Merged documentation content

    Example:
        >>> from pathlib import Path
        >>> content = get_agents_md(Path(".htmlgraph"), "claude")
    """
    engine = DocTemplateEngine(htmlgraph_dir)
    return engine.render_agents_md(__version__, platform)


def sync_docs_to_file(
    htmlgraph_dir: Path, output_file: Path, platform: str = "claude"
) -> Path:
    """Generate and write documentation to file.

    Args:
        htmlgraph_dir: Path to .htmlgraph directory
        output_file: Path where documentation should be written
        platform: Platform name (claude, gemini, etc.)

    Returns:
        Path to written file

    Example:
        >>> from pathlib import Path
        >>> sync_docs_to_file(
        ...     Path(".htmlgraph"),
        ...     Path("AGENTS.md"),
        ...     "claude"
        ... )
    """
    content = get_agents_md(htmlgraph_dir, platform)
    output_file.write_text(content)
    return output_file
