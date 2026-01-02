"""Jinja2-based template engine for documentation with user customization."""

from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import ChoiceLoader, Environment, FileSystemLoader


class DocTemplateEngine:
    """Renders documentation templates with user customization support.

    Template Priority:
    1. User templates in .htmlgraph/docs/templates/ (highest priority)
    2. Package templates in htmlgraph/docs/templates/ (fallback)

    Example:
        >>> engine = DocTemplateEngine(Path(".htmlgraph"))
        >>> content = engine.render_agents_md("0.21.0", "claude")
        >>> print(content)
    """

    def __init__(self, htmlgraph_dir: Path):
        """Initialize template engine with multi-loader.

        Args:
            htmlgraph_dir: Path to .htmlgraph directory
        """
        # Package templates (bundled with pip install)
        package_templates = Path(__file__).parent / "templates"

        # User templates (project-specific customizations)
        user_templates = htmlgraph_dir / "docs" / "templates"

        # Multi-loader: User templates have priority over package templates
        loaders = []
        if user_templates.exists():
            loaders.append(FileSystemLoader(str(user_templates)))
        loaders.append(FileSystemLoader(str(package_templates)))

        self.env = Environment(loader=ChoiceLoader(loaders))

        # Add custom filters
        self.env.filters["format_date"] = self._format_date
        self.env.filters["highlight_code"] = self._highlight_code

    def render(self, template_name: str, context: dict[str, Any]) -> str:
        """Render template with context, merging user overrides.

        Args:
            template_name: Name of template file (e.g., "agents.md.j2")
            context: Template variables

        Returns:
            Rendered content with user customizations applied

        Example:
            >>> engine.render("agents.md.j2", {"platform": "claude"})
        """
        template = self.env.get_template(template_name)
        return template.render(**context)

    def render_agents_md(self, sdk_version: str, platform: str = "claude") -> str:
        """Render AGENTS.md with platform-specific customizations.

        Args:
            sdk_version: HtmlGraph SDK version (e.g., "0.21.0")
            platform: Platform name (claude, gemini, api, etc.)

        Returns:
            Rendered AGENTS.md content

        Example:
            >>> content = engine.render_agents_md("0.21.0", "claude")
        """
        context = {
            "sdk_version": sdk_version,
            "platform": platform,
            "features_enabled": self._get_enabled_features(),
            "custom_workflows": self._load_custom_workflows(),
            "generated_at": datetime.now().isoformat(),
        }
        # User templates should extend "base_agents.md.j2" to avoid recursion
        # Priority: agents.md.j2 (user override) → base_agents.md.j2 (package default)
        template_name = "agents.md.j2"
        try:
            # Try to get user template first (will succeed if it exists in user dir)
            self.env.get_template(template_name)
            return self.render(template_name, context)
        except:  # noqa
            # Fall back to base template (always exists in package)
            return self.render("base_agents.md.j2", context)

    def _format_date(self, value: str) -> str:
        """Format ISO date string for display.

        Args:
            value: ISO 8601 date string

        Returns:
            Formatted date string
        """
        try:
            dt = datetime.fromisoformat(value)
            return dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, AttributeError):
            return value

    def _highlight_code(self, code: str, language: str = "python") -> str:
        """Add markdown code fence with syntax highlighting.

        Args:
            code: Code snippet
            language: Programming language for syntax highlighting

        Returns:
            Markdown code block
        """
        return f"```{language}\n{code}\n```"

    def _get_enabled_features(self) -> dict[str, bool]:
        """Get enabled features for this installation.

        Returns:
            Dictionary of feature flags
        """
        # TODO: Read from config or detect dynamically
        return {
            "sessions": True,
            "tracks": True,
            "analytics": True,
            "mcp": True,
            "cli": True,
        }

    def _load_custom_workflows(self) -> str | None:
        """Load custom workflows from user template.

        Returns:
            Custom workflow markdown or None
        """
        # TODO: Load from .htmlgraph/docs/workflows.md if exists
        return None
