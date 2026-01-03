"""Tests for Jinja2-based template system with user customization."""

import pytest
from htmlgraph.docs import get_agents_md, sync_docs_to_file
from htmlgraph.docs.template_engine import DocTemplateEngine


@pytest.fixture
def tmp_htmlgraph_dir(tmp_path):
    """Create temporary .htmlgraph directory."""
    htmlgraph_dir = tmp_path / ".htmlgraph"
    htmlgraph_dir.mkdir()
    return htmlgraph_dir


@pytest.fixture
def user_templates_dir(tmp_htmlgraph_dir):
    """Create user templates directory."""
    templates_dir = tmp_htmlgraph_dir / "docs" / "templates"
    templates_dir.mkdir(parents=True)
    return templates_dir


def test_base_template_renders(tmp_htmlgraph_dir):
    """Test that base template renders without user overrides."""
    engine = DocTemplateEngine(tmp_htmlgraph_dir)
    result = engine.render_agents_md("0.21.0", "claude")

    # Check basic structure
    assert "HtmlGraph Agent Documentation" in result
    assert "0.21.0" in result
    assert "claude" in result
    assert "Quick Start" in result
    assert "Core Concepts" in result
    assert "SDK Reference" in result


def test_template_includes_all_sections(tmp_htmlgraph_dir):
    """Test that all expected sections are present."""
    engine = DocTemplateEngine(tmp_htmlgraph_dir)
    result = engine.render_agents_md("0.21.0", "claude")

    # Check all major sections
    expected_sections = [
        "Introduction",
        "Quick Start",
        "Core Concepts",
        "SDK Reference",
        "CLI Reference",
        "Deployment",
    ]

    for section in expected_sections:
        assert section in result, f"Missing section: {section}"


def test_template_includes_code_examples(tmp_htmlgraph_dir):
    """Test that code examples are included."""
    engine = DocTemplateEngine(tmp_htmlgraph_dir)
    result = engine.render_agents_md("0.21.0", "claude")

    # Check for code blocks
    assert "```python" in result
    assert "from htmlgraph import SDK" in result
    assert "sdk = SDK(agent=" in result


def test_user_override_header(user_templates_dir, tmp_htmlgraph_dir):
    """Test that user can override header block."""
    # Create user override template
    user_template = user_templates_dir / "agents.md.j2"
    user_template.write_text("""
{% extends "base_agents.md.j2" %}
{% block header %}
# 🤖 {{ platform|title }} Agent - Custom Header
{% endblock %}
    """)

    engine = DocTemplateEngine(tmp_htmlgraph_dir)
    result = engine.render_agents_md("0.21.0", "claude")

    # User header should be present
    assert "Custom Header" in result
    assert "🤖 Claude Agent - Custom Header" in result

    # Original header should NOT be present
    assert "HtmlGraph Agent Documentation" not in result


def test_user_override_preserves_base_sections(user_templates_dir, tmp_htmlgraph_dir):
    """Test that user override preserves base sections."""
    # User overrides only header
    user_template = user_templates_dir / "agents.md.j2"
    user_template.write_text("""
{% extends "base_agents.md.j2" %}
{% block header %}
# Custom Header
{% endblock %}
    """)

    engine = DocTemplateEngine(tmp_htmlgraph_dir)
    result = engine.render_agents_md("0.21.0", "claude")

    # Custom header present
    assert "Custom Header" in result

    # Base sections still present
    assert "SDK Reference" in result
    assert "Core Concepts" in result
    assert "Quick Start" in result


def test_user_custom_workflows_block(user_templates_dir, tmp_htmlgraph_dir):
    """Test that user can add custom workflows."""
    user_template = user_templates_dir / "agents.md.j2"
    user_template.write_text("""
{% extends "base_agents.md.j2" %}
{% block custom_workflows %}
## Our Team Conventions

1. **Morning Standup** - Review `sdk.summary()`
2. **Daily Feature** - Use template: `feat-{YYYYMMDD}-{desc}`
3. **End of Day** - Commit with `git-commit-push.sh`
{% endblock %}
    """)

    engine = DocTemplateEngine(tmp_htmlgraph_dir)
    result = engine.render_agents_md("0.21.0", "claude")

    # Custom workflows should be present
    assert "Our Team Conventions" in result
    assert "Morning Standup" in result
    assert "Daily Feature" in result
    assert "End of Day" in result


def test_multiple_user_overrides(user_templates_dir, tmp_htmlgraph_dir):
    """Test that user can override multiple blocks."""
    user_template = user_templates_dir / "agents.md.j2"
    user_template.write_text("""
{% extends "base_agents.md.j2" %}

{% block header %}
# 🚀 Custom Documentation
{% endblock %}

{% block introduction %}
## Welcome to Our Project

This is our custom introduction.
{% endblock %}

{% block custom_workflows %}
## Team Workflows

- Morning sync
- Evening commit
{% endblock %}
    """)

    engine = DocTemplateEngine(tmp_htmlgraph_dir)
    result = engine.render_agents_md("0.21.0", "claude")

    # All custom blocks should be present
    assert "🚀 Custom Documentation" in result
    assert "Welcome to Our Project" in result
    assert "Team Workflows" in result
    assert "Morning sync" in result

    # Original content should NOT be present
    assert "HtmlGraph Agent Documentation" not in result


def test_platform_variable_in_template(tmp_htmlgraph_dir):
    """Test that platform variable is correctly passed to template."""
    engine = DocTemplateEngine(tmp_htmlgraph_dir)

    # Test with claude
    result_claude = engine.render_agents_md("0.21.0", "claude")
    assert 'agent="claude"' in result_claude

    # Test with gemini
    result_gemini = engine.render_agents_md("0.21.0", "gemini")
    assert 'agent="gemini"' in result_gemini


def test_version_in_template(tmp_htmlgraph_dir):
    """Test that version is correctly rendered."""
    engine = DocTemplateEngine(tmp_htmlgraph_dir)
    result = engine.render_agents_md("0.21.0", "claude")

    # Check version in frontmatter
    assert 'version: "0.21.0"' in result

    # Check version in footer
    assert "HtmlGraph v0.21.0" in result


def test_get_agents_md_function(tmp_htmlgraph_dir):
    """Test the get_agents_md convenience function."""
    result = get_agents_md(tmp_htmlgraph_dir, "claude")

    assert isinstance(result, str)
    assert len(result) > 0
    assert "HtmlGraph Agent Documentation" in result


def test_sync_docs_to_file(tmp_htmlgraph_dir, tmp_path):
    """Test syncing documentation to file."""
    output_file = tmp_path / "AGENTS.md"

    # Sync docs
    result_path = sync_docs_to_file(tmp_htmlgraph_dir, output_file, "claude")

    # Check file was created
    assert result_path == output_file
    assert output_file.exists()

    # Check content
    content = output_file.read_text()
    assert "HtmlGraph Agent Documentation" in content


def test_format_date_filter(tmp_htmlgraph_dir):
    """Test custom date formatting filter."""
    engine = DocTemplateEngine(tmp_htmlgraph_dir)

    # Test date filter
    template_content = "{{ date|format_date }}"
    template = engine.env.from_string(template_content)
    result = template.render(date="2026-01-02T12:30:00")

    assert "2026-01-02" in result


def test_highlight_code_filter(tmp_htmlgraph_dir):
    """Test code highlighting filter."""
    engine = DocTemplateEngine(tmp_htmlgraph_dir)

    # Test highlight filter
    template_content = "{{ code|highlight_code('python') }}"
    template = engine.env.from_string(template_content)
    result = template.render(code="print('hello')")

    assert "```python" in result
    assert "print('hello')" in result
    assert "```" in result


def test_template_with_missing_user_dir(tmp_htmlgraph_dir):
    """Test that template works even without user templates directory."""
    # Don't create user templates directory
    engine = DocTemplateEngine(tmp_htmlgraph_dir)
    result = engine.render_agents_md("0.21.0", "claude")

    # Should still render base template
    assert "HtmlGraph Agent Documentation" in result


def test_section_templates_are_included(tmp_htmlgraph_dir):
    """Test that section templates are properly included."""
    engine = DocTemplateEngine(tmp_htmlgraph_dir)
    result = engine.render_agents_md("0.21.0", "claude")

    # Check content from section templates
    assert "Graph Structure" in result  # from core_concepts.md.j2
    assert "Features API" in result  # from sdk_basics.md.j2
    assert "Installation" in result  # from cli_reference.md.j2


def test_user_can_override_section_template(user_templates_dir, tmp_htmlgraph_dir):
    """Test that user can override section templates."""
    # Create user override for core concepts
    sections_dir = user_templates_dir / "_sections"
    sections_dir.mkdir()

    custom_section = sections_dir / "core_concepts.md.j2"
    custom_section.write_text("""
## Our Custom Concepts

This is our team's understanding of the core concepts.
    """)

    engine = DocTemplateEngine(tmp_htmlgraph_dir)
    result = engine.render_agents_md("0.21.0", "claude")

    # Custom section should be present
    assert "Our Custom Concepts" in result
    assert "team's understanding" in result

    # Original section should NOT be present
    assert "Graph Structure" not in result


def test_template_with_invalid_date(tmp_htmlgraph_dir):
    """Test date filter handles invalid dates gracefully."""
    engine = DocTemplateEngine(tmp_htmlgraph_dir)

    template_content = "{{ date|format_date }}"
    template = engine.env.from_string(template_content)

    # Should return original value for invalid date
    result = template.render(date="not-a-date")
    assert "not-a-date" in result


def test_generated_timestamp_in_output(tmp_htmlgraph_dir):
    """Test that generated timestamp is included in output."""
    engine = DocTemplateEngine(tmp_htmlgraph_dir)
    result = engine.render_agents_md("0.21.0", "claude")

    # Check for generated timestamp in frontmatter
    assert "generated:" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
