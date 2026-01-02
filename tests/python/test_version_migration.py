"""
Tests for documentation version tracking and migration system.
"""

from datetime import datetime
from pathlib import Path

import pytest
from htmlgraph.docs import (
    DOC_VERSIONS,
    check_docs_version,
    get_current_doc_version,
    get_migration,
    is_compatible,
)
from htmlgraph.docs.metadata import DocsMetadata
from htmlgraph.docs.migrations import V1toV2Migration


@pytest.fixture
def temp_htmlgraph_dir(tmp_path: Path) -> Path:
    """Create temporary .htmlgraph directory for testing."""
    htmlgraph_dir = tmp_path / ".htmlgraph"
    htmlgraph_dir.mkdir()
    (htmlgraph_dir / "docs").mkdir()
    return htmlgraph_dir


@pytest.fixture
def backup_dir(temp_htmlgraph_dir: Path) -> Path:
    """Create backup directory for migration tests."""
    backup_dir = temp_htmlgraph_dir / ".docs-backups"
    backup_dir.mkdir()
    return backup_dir


class TestDocVersion:
    """Tests for documentation version compatibility."""

    def test_get_current_doc_version(self):
        """Test getting current doc version."""
        version = get_current_doc_version()
        assert version == 2  # Current version

    def test_is_compatible_same_version(self):
        """Test compatibility check for same version."""
        assert is_compatible(2, 2) is True

    def test_is_compatible_n_minus_1(self):
        """Test compatibility with N-1 version (v1 user with v2 package)."""
        assert is_compatible(1, 2) is True

    def test_is_incompatible_too_old(self):
        """Test incompatibility when user version is too old."""
        assert is_compatible(0, 2) is False

    def test_doc_versions_registry(self):
        """Test DOC_VERSIONS contains expected entries."""
        assert 1 in DOC_VERSIONS
        assert 2 in DOC_VERSIONS
        assert DOC_VERSIONS[2].version == 2
        assert DOC_VERSIONS[2].package_version == "0.20.0"


class TestDocsMetadata:
    """Tests for documentation metadata management."""

    def test_create_default_metadata(self):
        """Test creating default metadata."""
        metadata = DocsMetadata()
        assert metadata.schema_version == 2
        assert isinstance(metadata.last_updated, datetime)
        assert metadata.customizations == []

    def test_load_nonexistent_metadata(self, temp_htmlgraph_dir: Path):
        """Test loading metadata when file doesn't exist returns default."""
        metadata = DocsMetadata.load(temp_htmlgraph_dir)
        assert metadata.schema_version == 2

    def test_save_and_load_metadata(self, temp_htmlgraph_dir: Path):
        """Test saving and loading metadata."""
        metadata = DocsMetadata(
            schema_version=2,
            customizations=["custom_workflows"],
            base_version_on_last_update="0.21.0",
        )
        metadata.save(temp_htmlgraph_dir)

        loaded = DocsMetadata.load(temp_htmlgraph_dir)
        assert loaded.schema_version == 2
        assert loaded.customizations == ["custom_workflows"]
        assert loaded.base_version_on_last_update == "0.21.0"

    def test_add_customization(self):
        """Test adding customization marker."""
        metadata = DocsMetadata()
        metadata.add_customization("my_section")
        assert "my_section" in metadata.customizations

    def test_add_duplicate_customization(self):
        """Test adding duplicate customization doesn't duplicate."""
        metadata = DocsMetadata()
        metadata.add_customization("my_section")
        metadata.add_customization("my_section")
        assert metadata.customizations.count("my_section") == 1

    def test_remove_customization(self):
        """Test removing customization marker."""
        metadata = DocsMetadata(customizations=["section1", "section2"])
        metadata.remove_customization("section1")
        assert "section1" not in metadata.customizations
        assert "section2" in metadata.customizations

    def test_has_customizations(self):
        """Test checking for customizations."""
        metadata = DocsMetadata()
        assert metadata.has_customizations() is False

        metadata.add_customization("test")
        assert metadata.has_customizations() is True


class TestVersionCheck:
    """Tests for version checking functionality."""

    def test_check_version_no_metadata(self, temp_htmlgraph_dir: Path):
        """Test version check when no metadata exists (uses default)."""
        compatible, message = check_docs_version(temp_htmlgraph_dir)
        assert compatible is True
        assert message is None

    def test_check_version_current(self, temp_htmlgraph_dir: Path):
        """Test version check when version is current."""
        metadata = DocsMetadata(schema_version=2)
        metadata.save(temp_htmlgraph_dir)

        compatible, message = check_docs_version(temp_htmlgraph_dir)
        assert compatible is True
        assert message is None

    def test_check_version_compatible_outdated(self, temp_htmlgraph_dir: Path):
        """Test version check when version is compatible but outdated."""
        metadata = DocsMetadata(schema_version=1)
        metadata.save(temp_htmlgraph_dir)

        compatible, message = check_docs_version(temp_htmlgraph_dir)
        assert compatible is True
        assert message is not None
        assert "supported but outdated" in message

    def test_check_version_incompatible(self, temp_htmlgraph_dir: Path):
        """Test version check when version is incompatible."""
        metadata = DocsMetadata(schema_version=0)
        metadata.save(temp_htmlgraph_dir)

        compatible, message = check_docs_version(temp_htmlgraph_dir)
        assert compatible is False
        assert message is not None
        assert "incompatible" in message


class TestV1toV2Migration:
    """Tests for v1 to v2 migration."""

    def test_migration_basic_properties(self):
        """Test migration has correct version properties."""
        migration = V1toV2Migration()
        assert migration.from_version == 1
        assert migration.to_version == 2

    def test_detect_customizations_empty(self, temp_htmlgraph_dir: Path):
        """Test detecting customizations in non-existent file."""
        migration = V1toV2Migration()
        agents_md = temp_htmlgraph_dir / "AGENTS.md"

        customizations = migration._detect_customizations(agents_md)
        assert customizations == []

    def test_detect_customizations_with_custom_sections(self, temp_htmlgraph_dir: Path):
        """Test detecting user-added custom sections."""
        migration = V1toV2Migration()
        agents_md = temp_htmlgraph_dir / "AGENTS.md"

        agents_md.write_text(
            """
# AGENTS.md

## Quick Start
Standard content

## Our Team Workflows
Custom section

## Project Conventions
Another custom section
"""
        )

        customizations = migration._detect_customizations(agents_md)
        assert "custom_workflows" in customizations
        assert "project_conventions" in customizations

    def test_backup_docs_creates_backup(
        self, temp_htmlgraph_dir: Path, backup_dir: Path
    ):
        """Test that backup creates timestamped backup directory."""
        migration = V1toV2Migration()

        # Create some docs to backup
        agents_md = temp_htmlgraph_dir / "AGENTS.md"
        agents_md.write_text("# AGENTS.md content")

        backup_path = migration.backup_docs(temp_htmlgraph_dir, backup_dir)

        assert backup_path.exists()
        assert backup_path.parent == backup_dir
        assert "v1_" in backup_path.name
        assert (backup_path / "AGENTS.md").exists()

    def test_migrate_creates_v2_docs(self, temp_htmlgraph_dir: Path, backup_dir: Path):
        """Test migration creates v2 documentation structure."""
        migration = V1toV2Migration()

        # Create v1 docs
        agents_md = temp_htmlgraph_dir / "AGENTS.md"
        agents_md.write_text("# Old v1 AGENTS.md")

        # Create metadata
        metadata = DocsMetadata(schema_version=1)
        metadata.save(temp_htmlgraph_dir)

        # Run migration
        success = migration.migrate(temp_htmlgraph_dir, backup_dir)

        assert success is True
        assert (temp_htmlgraph_dir / "AGENTS.md.v1.backup").exists()
        assert (temp_htmlgraph_dir / "docs" / "AGENTS.md").exists()

        # Check metadata updated
        updated_metadata = DocsMetadata.load(temp_htmlgraph_dir)
        assert updated_metadata.schema_version == 2

    def test_migrate_preserves_customizations(
        self, temp_htmlgraph_dir: Path, backup_dir: Path
    ):
        """Test migration preserves user customizations."""
        migration = V1toV2Migration()

        # Create v1 docs with customizations
        agents_md = temp_htmlgraph_dir / "AGENTS.md"
        agents_md.write_text(
            """
# AGENTS.md

## Our Team Workflows
Custom workflow content
"""
        )

        metadata = DocsMetadata(schema_version=1)
        metadata.save(temp_htmlgraph_dir)

        success = migration.migrate(temp_htmlgraph_dir, backup_dir)

        assert success is True

        # Check customizations recorded
        updated_metadata = DocsMetadata.load(temp_htmlgraph_dir)
        assert "custom_workflows" in updated_metadata.customizations

    def test_rollback_restores_v1(self, temp_htmlgraph_dir: Path, backup_dir: Path):
        """Test rollback restores v1 documentation."""
        migration = V1toV2Migration()

        # Create backup
        backup_subdir = backup_dir / "v1_20260102_120000"
        backup_subdir.mkdir()
        v1_agents = backup_subdir / "AGENTS.md"
        v1_agents.write_text("# Original v1 AGENTS.md")

        # Create v2 metadata
        metadata = DocsMetadata(schema_version=2)
        metadata.save(temp_htmlgraph_dir)

        # Rollback
        migration.rollback(temp_htmlgraph_dir, backup_dir)

        # Check v1 restored
        assert (temp_htmlgraph_dir / "AGENTS.md").exists()
        assert (
            temp_htmlgraph_dir / "AGENTS.md"
        ).read_text() == "# Original v1 AGENTS.md"

        # Check metadata updated
        updated_metadata = DocsMetadata.load(temp_htmlgraph_dir)
        assert updated_metadata.schema_version == 1

    def test_rollback_fails_without_backup(
        self, temp_htmlgraph_dir: Path, backup_dir: Path
    ):
        """Test rollback raises error when no backup exists."""
        migration = V1toV2Migration()

        with pytest.raises(ValueError, match="No backup found"):
            migration.rollback(temp_htmlgraph_dir, backup_dir)


class TestMigrationRegistry:
    """Tests for migration registry and lookup."""

    def test_get_migration_v1_to_v2(self):
        """Test getting v1 to v2 migration."""
        migration = get_migration(1, 2)
        assert migration is not None
        assert isinstance(migration, V1toV2Migration)

    def test_get_migration_nonexistent(self):
        """Test getting non-existent migration returns None."""
        migration = get_migration(2, 3)
        assert migration is None

    def test_get_migration_reverse_direction(self):
        """Test getting migration in reverse direction."""
        migration = get_migration(2, 1)
        assert migration is None  # No reverse migrations defined


class TestIntegration:
    """Integration tests for complete migration workflows."""

    def test_full_migration_workflow(self, temp_htmlgraph_dir: Path):
        """Test complete migration workflow from v1 to v2."""
        # Setup: Create v1 environment
        agents_md = temp_htmlgraph_dir / "AGENTS.md"
        agents_md.write_text("# v1 AGENTS.md\n\n## Our Team\nCustom content")

        metadata = DocsMetadata(schema_version=1)
        metadata.save(temp_htmlgraph_dir)

        # Step 1: Check version (should be compatible but outdated)
        compatible, message = check_docs_version(temp_htmlgraph_dir)
        assert compatible is True
        assert "outdated" in message

        # Step 2: Get migration
        migration = get_migration(1, 2)
        assert migration is not None

        # Step 3: Run migration
        backup_dir = temp_htmlgraph_dir / ".docs-backups"
        backup_dir.mkdir()

        success = migration.migrate(temp_htmlgraph_dir, backup_dir)
        assert success is True

        # Step 4: Verify migration completed
        new_metadata = DocsMetadata.load(temp_htmlgraph_dir)
        assert new_metadata.schema_version == 2

        # Step 5: Check version again (should be current)
        compatible, message = check_docs_version(temp_htmlgraph_dir)
        assert compatible is True
        assert message is None

    def test_rollback_after_migration(self, temp_htmlgraph_dir: Path):
        """Test rollback workflow after migration."""
        # Setup: v1 docs
        agents_md = temp_htmlgraph_dir / "AGENTS.md"
        original_content = "# Original v1 AGENTS.md"
        agents_md.write_text(original_content)

        metadata = DocsMetadata(schema_version=1)
        metadata.save(temp_htmlgraph_dir)

        # Migrate to v2
        migration = get_migration(1, 2)
        backup_dir = temp_htmlgraph_dir / ".docs-backups"
        backup_dir.mkdir()

        migration.migrate(temp_htmlgraph_dir, backup_dir)

        # Verify v2
        assert DocsMetadata.load(temp_htmlgraph_dir).schema_version == 2

        # Rollback to v1
        migration.rollback(temp_htmlgraph_dir, backup_dir)

        # Verify v1 restored
        assert DocsMetadata.load(temp_htmlgraph_dir).schema_version == 1
        assert (temp_htmlgraph_dir / "AGENTS.md").exists()
