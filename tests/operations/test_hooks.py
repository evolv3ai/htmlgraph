"""Tests for hooks operations module."""

import json
from pathlib import Path

import pytest
from htmlgraph.operations.hooks import (
    HookConfigError,
    HookInstallError,
    HookInstallResult,
    HookListResult,
    HookValidationResult,
    install_hooks,
    list_hooks,
    validate_hook_config,
)


@pytest.fixture
def mock_project(tmp_path: Path) -> Path:
    """Create a mock project with git and htmlgraph directories."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    # Create .git directory
    git_dir = project_dir / ".git"
    git_dir.mkdir()
    git_hooks_dir = git_dir / "hooks"
    git_hooks_dir.mkdir()

    # Create .htmlgraph directory
    htmlgraph_dir = project_dir / ".htmlgraph"
    htmlgraph_dir.mkdir()

    return project_dir


@pytest.fixture
def mock_project_with_config(mock_project: Path) -> Path:
    """Create a mock project with hook configuration."""
    config_path = mock_project / ".htmlgraph" / "hooks-config.json"
    config = {
        "enabled_hooks": ["post-commit", "pre-push"],
        "use_symlinks": True,
        "backup_existing": True,
        "chain_existing": True,
    }
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    return mock_project


@pytest.fixture
def mock_hook_template(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create mock hook templates."""
    hooks_dir = tmp_path / "mock_hooks"
    hooks_dir.mkdir()

    # Create mock hook scripts
    for hook_name in ["post-commit", "pre-push", "post-checkout", "post-merge"]:
        hook_file = hooks_dir / f"{hook_name}.sh"
        hook_file.write_text("#!/bin/bash\necho 'Test hook'\n", encoding="utf-8")
        hook_file.chmod(0o755)

    # Patch HOOKS_DIR
    import htmlgraph.hooks

    monkeypatch.setattr(htmlgraph.hooks, "HOOKS_DIR", hooks_dir)

    return hooks_dir


class TestInstallHooks:
    """Tests for install_hooks()."""

    def test_install_hooks_success(
        self, mock_project: Path, mock_hook_template: Path
    ) -> None:
        """Test successful hook installation."""
        result = install_hooks(project_dir=mock_project)

        assert isinstance(result, HookInstallResult)
        assert len(result.installed) > 0
        assert len(result.skipped) == 0
        assert isinstance(result.config_used, dict)

        # Verify hooks were actually installed
        git_hooks_dir = mock_project / ".git" / "hooks"
        for hook_name in result.installed:
            hook_path = git_hooks_dir / hook_name
            assert hook_path.exists() or hook_path.is_symlink()

    def test_install_hooks_not_git_repo(self, tmp_path: Path) -> None:
        """Test installation fails without git repo."""
        project_dir = tmp_path / "not_a_repo"
        project_dir.mkdir()
        (project_dir / ".htmlgraph").mkdir()

        with pytest.raises(HookInstallError, match="Not a git repository"):
            install_hooks(project_dir=project_dir)

    def test_install_hooks_not_initialized(self, tmp_path: Path) -> None:
        """Test installation fails without HtmlGraph initialization."""
        project_dir = tmp_path / "not_initialized"
        project_dir.mkdir()
        (project_dir / ".git").mkdir()

        with pytest.raises(HookInstallError, match="HtmlGraph not initialized"):
            install_hooks(project_dir=project_dir)

    def test_install_hooks_with_copy(
        self, mock_project: Path, mock_hook_template: Path
    ) -> None:
        """Test hook installation with copy instead of symlink."""
        result = install_hooks(project_dir=mock_project, use_copy=True)

        assert len(result.installed) > 0

        # Verify hooks are actual files, not symlinks
        git_hooks_dir = mock_project / ".git" / "hooks"
        for hook_name in result.installed:
            hook_path = git_hooks_dir / hook_name
            assert hook_path.exists()
            assert not hook_path.is_symlink()

    def test_install_hooks_with_existing(
        self, mock_project: Path, mock_hook_template: Path
    ) -> None:
        """Test installation with existing hooks."""
        # Create existing hook
        git_hooks_dir = mock_project / ".git" / "hooks"
        existing_hook = git_hooks_dir / "post-commit"
        existing_hook.write_text(
            "#!/bin/bash\necho 'Existing hook'\n", encoding="utf-8"
        )
        existing_hook.chmod(0o755)

        install_hooks(project_dir=mock_project)

        # Should create backup and chain
        backup_path = existing_hook.with_suffix(".backup")
        assert backup_path.exists()

    def test_install_hooks_with_custom_config(
        self, mock_project_with_config: Path, mock_hook_template: Path
    ) -> None:
        """Test installation respects custom configuration."""
        result = install_hooks(project_dir=mock_project_with_config)

        # Should only install hooks listed in config
        assert "post-commit" in result.installed
        assert "pre-push" in result.installed


class TestListHooks:
    """Tests for list_hooks()."""

    def test_list_hooks_empty(self, mock_project: Path) -> None:
        """Test listing hooks when none are installed."""
        result = list_hooks(project_dir=mock_project)

        assert isinstance(result, HookListResult)
        assert len(result.enabled) == 0
        # Default config has 4 enabled hooks, but none installed yet
        assert len(result.missing) > 0
        assert len(result.disabled) >= 0

    def test_list_hooks_after_install(
        self, mock_project: Path, mock_hook_template: Path
    ) -> None:
        """Test listing hooks after installation."""
        # Install hooks first
        install_result = install_hooks(project_dir=mock_project)

        # Now list them
        result = list_hooks(project_dir=mock_project)

        assert len(result.enabled) == len(install_result.installed)
        assert len(result.missing) == 0

    def test_list_hooks_mixed_state(
        self, mock_project_with_config: Path, mock_hook_template: Path
    ) -> None:
        """Test listing hooks in mixed state."""
        # Install only some hooks
        git_hooks_dir = mock_project_with_config / ".git" / "hooks"
        (git_hooks_dir / "post-commit").write_text("#!/bin/bash\n", encoding="utf-8")
        (git_hooks_dir / "post-commit").chmod(0o755)

        result = list_hooks(project_dir=mock_project_with_config)

        assert "post-commit" in result.enabled
        assert "pre-push" in result.missing


class TestValidateHookConfig:
    """Tests for validate_hook_config()."""

    def test_validate_success(
        self, mock_project_with_config: Path, mock_hook_template: Path
    ) -> None:
        """Test successful validation."""
        result = validate_hook_config(project_dir=mock_project_with_config)

        assert isinstance(result, HookValidationResult)
        assert result.valid is True
        assert len(result.errors) == 0

    def test_validate_not_git_repo(self, tmp_path: Path) -> None:
        """Test validation fails for non-git repo."""
        project_dir = tmp_path / "not_a_repo"
        project_dir.mkdir()
        (project_dir / ".htmlgraph").mkdir()

        result = validate_hook_config(project_dir=project_dir)

        assert result.valid is False
        assert any("Not a git repository" in error for error in result.errors)

    def test_validate_not_initialized(self, tmp_path: Path) -> None:
        """Test validation fails without initialization."""
        project_dir = tmp_path / "not_initialized"
        project_dir.mkdir()
        (project_dir / ".git").mkdir()

        result = validate_hook_config(project_dir=project_dir)

        assert result.valid is False
        assert any("not initialized" in error for error in result.errors)

    def test_validate_invalid_config(self, mock_project: Path) -> None:
        """Test validation detects invalid configuration."""
        # Create invalid config
        config_path = mock_project / ".htmlgraph" / "hooks-config.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump({"enabled_hooks": "not-a-list"}, f)

        result = validate_hook_config(project_dir=mock_project)

        assert result.valid is False
        assert any("must be a list" in error for error in result.errors)

    def test_validate_unknown_hooks(self, mock_project: Path) -> None:
        """Test validation warns about unknown hooks."""
        # Create config with unknown hook
        config_path = mock_project / ".htmlgraph" / "hooks-config.json"
        config = {
            "enabled_hooks": ["post-commit", "unknown-hook"],
        }
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        result = validate_hook_config(project_dir=mock_project)

        assert result.valid is True  # Warnings don't invalidate
        assert any("Unknown hook" in warning for warning in result.warnings)

    def test_validate_invalid_boolean_options(self, mock_project: Path) -> None:
        """Test validation detects invalid boolean options."""
        # Create config with invalid boolean
        config_path = mock_project / ".htmlgraph" / "hooks-config.json"
        config = {
            "enabled_hooks": ["post-commit"],
            "use_symlinks": "not-a-boolean",
        }
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        result = validate_hook_config(project_dir=mock_project)

        assert result.valid is False
        assert any("must be a boolean" in error for error in result.errors)


class TestHookConfigError:
    """Tests for HookConfigError exception."""

    def test_hook_config_error_raised(self, mock_project: Path) -> None:
        """Test HookConfigError is raised for invalid JSON."""
        # Create malformed JSON
        config_path = mock_project / ".htmlgraph" / "hooks-config.json"
        config_path.write_text("{invalid json", encoding="utf-8")

        with pytest.raises(HookConfigError, match="Failed to load hook config"):
            install_hooks(project_dir=mock_project)


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_install_hooks_creates_git_hooks_dir(
        self, tmp_path: Path, mock_hook_template: Path
    ) -> None:
        """Test installation creates .git/hooks if missing."""
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()

        git_dir = project_dir / ".git"
        git_dir.mkdir()
        # Don't create hooks directory

        htmlgraph_dir = project_dir / ".htmlgraph"
        htmlgraph_dir.mkdir()

        result = install_hooks(project_dir=project_dir)

        # Should succeed and create directory
        assert len(result.installed) > 0
        assert (git_dir / "hooks").exists()

    def test_install_hooks_with_symlink_existing(
        self, mock_project: Path, mock_hook_template: Path
    ) -> None:
        """Test installation handles existing symlinks."""
        # Create existing symlink
        git_hooks_dir = mock_project / ".git" / "hooks"
        existing_hook = git_hooks_dir / "post-commit"
        target = mock_project / "some_other_hook.sh"
        target.write_text("#!/bin/bash\n", encoding="utf-8")
        existing_hook.symlink_to(target)

        result = install_hooks(project_dir=mock_project)

        # Should replace symlink
        assert "post-commit" in result.installed or "post-commit" in result.skipped

    def test_list_hooks_with_missing_config(self, mock_project: Path) -> None:
        """Test list_hooks handles missing config gracefully."""
        result = list_hooks(project_dir=mock_project)

        # Should use defaults and not crash
        assert isinstance(result, HookListResult)
