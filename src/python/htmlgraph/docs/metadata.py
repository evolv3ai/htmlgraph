"""
Documentation metadata storage and management.
"""

from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field


class DocsMetadata(BaseModel):
    """Metadata for project documentation."""

    schema_version: int = 2
    last_updated: datetime = Field(default_factory=datetime.now)
    customizations: list[str] = []  # List of user-customized sections
    base_version_on_last_update: str = "0.21.0"

    @classmethod
    def load(cls, htmlgraph_dir: Path) -> "DocsMetadata":
        """Load metadata from .docs-metadata.json.

        Args:
            htmlgraph_dir: Path to .htmlgraph directory

        Returns:
            DocsMetadata instance (default if file doesn't exist)
        """
        import json

        metadata_file = htmlgraph_dir / ".docs-metadata.json"
        if metadata_file.exists():
            data = json.loads(metadata_file.read_text())
            return cls(**data)
        return cls()  # Default

    def save(self, htmlgraph_dir: Path) -> None:
        """Save metadata to .docs-metadata.json.

        Args:
            htmlgraph_dir: Path to .htmlgraph directory
        """
        metadata_file = htmlgraph_dir / ".docs-metadata.json"
        metadata_file.write_text(self.model_dump_json(indent=2))

    @classmethod
    def create_initial(
        cls, htmlgraph_dir: Path, schema_version: int = 2
    ) -> "DocsMetadata":
        """Create initial metadata file.

        Args:
            htmlgraph_dir: Path to .htmlgraph directory
            schema_version: Documentation schema version

        Returns:
            New DocsMetadata instance
        """
        from htmlgraph import __version__

        metadata = cls(
            schema_version=schema_version,
            base_version_on_last_update=__version__,
            customizations=[],
        )
        metadata.save(htmlgraph_dir)
        return metadata

    def add_customization(self, section_name: str) -> None:
        """Mark a section as customized.

        Args:
            section_name: Name of the customized section
        """
        if section_name not in self.customizations:
            self.customizations.append(section_name)

    def remove_customization(self, section_name: str) -> None:
        """Remove a customization marker.

        Args:
            section_name: Name of the section to unmark
        """
        if section_name in self.customizations:
            self.customizations.remove(section_name)

    def has_customizations(self) -> bool:
        """Check if any customizations exist.

        Returns:
            True if user has customized documentation
        """
        return len(self.customizations) > 0
