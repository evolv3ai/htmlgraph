"""
Documentation migration system.

Handles version migrations with automatic customization preservation.
"""

import shutil
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

from htmlgraph.docs.metadata import DocsMetadata


class MigrationScript(ABC):
    """Base class for documentation migrations."""

    from_version: int
    to_version: int

    @abstractmethod
    def migrate(self, htmlgraph_dir: Path, backup_dir: Path) -> bool:
        """Execute migration. Returns True if successful.

        Args:
            htmlgraph_dir: Path to .htmlgraph directory
            backup_dir: Path to backup directory

        Returns:
            True if migration successful
        """
        pass

    @abstractmethod
    def rollback(self, htmlgraph_dir: Path, backup_dir: Path) -> None:
        """Rollback migration to previous state.

        Args:
            htmlgraph_dir: Path to .htmlgraph directory
            backup_dir: Path to backup directory
        """
        pass

    def backup_docs(self, htmlgraph_dir: Path, backup_dir: Path) -> Path:
        """Backup current documentation before migration.

        Args:
            htmlgraph_dir: Path to .htmlgraph directory
            backup_dir: Path to backup directory

        Returns:
            Path to created backup subdirectory
        """
        backup_subdir = (
            backup_dir / f"v{self.from_version}_{datetime.now():%Y%m%d_%H%M%S}"
        )
        backup_subdir.mkdir(parents=True, exist_ok=True)

        # Backup all docs
        docs_dir = htmlgraph_dir / "docs"
        if docs_dir.exists():
            for doc_file in docs_dir.glob("*.md"):
                shutil.copy2(doc_file, backup_subdir / doc_file.name)

        # Also backup root-level docs (legacy)
        for doc_file in htmlgraph_dir.glob("*.md"):
            shutil.copy2(doc_file, backup_subdir / doc_file.name)

        return backup_subdir


class V1toV2Migration(MigrationScript):
    """Migrate from v1 (root-level docs) to v2 (template-based docs)."""

    from_version = 1
    to_version = 2

    def migrate(self, htmlgraph_dir: Path, backup_dir: Path) -> bool:
        """Migrate v1 docs to v2 template structure.

        Args:
            htmlgraph_dir: Path to .htmlgraph directory
            backup_dir: Path to backup directory

        Returns:
            True if migration successful
        """
        # Backup first
        backup_path = self.backup_docs(htmlgraph_dir, backup_dir)
        print(f"✅ Backed up to {backup_path}")

        # Detect user customizations in old AGENTS.md
        customizations = self._detect_customizations(htmlgraph_dir / "AGENTS.md")
        if customizations:
            print(f"📝 Detected customizations: {', '.join(customizations)}")

        # Move old docs to archive
        old_agents_md = htmlgraph_dir / "AGENTS.md"
        if old_agents_md.exists():
            old_agents_md.rename(htmlgraph_dir / "AGENTS.md.v1.backup")
            print("📦 Archived old AGENTS.md")

        # Generate new v2 docs with customizations preserved
        self._generate_v2_docs(htmlgraph_dir, customizations)
        print("✨ Generated v2 documentation")

        # Update metadata
        metadata = DocsMetadata.load(htmlgraph_dir)
        metadata.schema_version = 2
        metadata.customizations = customizations
        metadata.save(htmlgraph_dir)
        print("💾 Updated metadata")

        return True

    def _detect_customizations(self, agents_md_path: Path) -> list[str]:
        """Detect user-customized sections in old AGENTS.md.

        Args:
            agents_md_path: Path to AGENTS.md file

        Returns:
            List of customized section names
        """
        if not agents_md_path.exists():
            return []

        content = agents_md_path.read_text()
        customizations = []

        # Simple heuristic: sections not in base template
        if "## Our Team" in content:
            customizations.append("custom_workflows")
        if "## Project Conventions" in content:
            customizations.append("project_conventions")
        if "## Custom Workflows" in content:
            customizations.append("custom_workflows")

        return customizations

    def _generate_v2_docs(self, htmlgraph_dir: Path, customizations: list[str]) -> None:
        """Generate v2 template-based docs with customizations.

        Args:
            htmlgraph_dir: Path to .htmlgraph directory
            customizations: List of customized sections to preserve
        """
        # NOTE: This would integrate with sync_docs.py
        # For now, just create placeholder
        docs_dir = htmlgraph_dir / "docs"
        docs_dir.mkdir(exist_ok=True)

        placeholder = docs_dir / "AGENTS.md"
        placeholder.write_text(
            """# HtmlGraph Agent Documentation (v2)

This file was migrated from v1 to v2.

Run `uv run htmlgraph sync-docs` to regenerate from templates.
"""
        )

        # Inject customizations as template overrides if needed
        if customizations:
            self._create_override_template(htmlgraph_dir, customizations)

    def _create_override_template(
        self, htmlgraph_dir: Path, customizations: list[str]
    ) -> None:
        """Create template overrides for customizations.

        Args:
            htmlgraph_dir: Path to .htmlgraph directory
            customizations: List of customizations to preserve
        """
        overrides_file = htmlgraph_dir / "docs" / "overrides.md"
        overrides_file.write_text(
            f"""# Documentation Customizations

The following sections were customized in v1:

{chr(10).join(f"- {c}" for c in customizations)}

To preserve these customizations, add them back manually after running sync-docs.
"""
        )

    def rollback(self, htmlgraph_dir: Path, backup_dir: Path) -> None:
        """Rollback to v1 docs from backup.

        Args:
            htmlgraph_dir: Path to .htmlgraph directory
            backup_dir: Path to backup directory
        """
        # Find latest backup
        backups = sorted(backup_dir.glob("v1_*"))
        if not backups:
            raise ValueError("No backup found for rollback")

        latest_backup = backups[-1]
        print(f"🔄 Rolling back from {latest_backup}")

        # Restore old AGENTS.md
        backup_agents = latest_backup / "AGENTS.md"
        if backup_agents.exists():
            shutil.copy2(backup_agents, htmlgraph_dir / "AGENTS.md")
            print("✅ Restored AGENTS.md")

        # Update metadata
        metadata = DocsMetadata.load(htmlgraph_dir)
        metadata.schema_version = 1
        metadata.save(htmlgraph_dir)
        print("💾 Updated metadata to v1")


# Migration registry
MIGRATIONS: dict[tuple[int, int], MigrationScript] = {
    (1, 2): V1toV2Migration(),
}


def get_migration(from_version: int, to_version: int) -> MigrationScript | None:
    """Get migration script for version transition.

    Args:
        from_version: Source schema version
        to_version: Target schema version

    Returns:
        MigrationScript instance or None if no migration exists
    """
    return MIGRATIONS.get((from_version, to_version))
