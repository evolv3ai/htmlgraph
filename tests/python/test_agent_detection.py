"""
Tests for agent detection utilities.
"""

from unittest.mock import Mock

from htmlgraph.agent_detection import detect_agent_name, get_agent_display_name


class TestAgentDetection:
    """Test agent detection functionality."""

    def test_detect_agent_with_explicit_override(self, monkeypatch):
        """Test explicit HTMLGRAPH_AGENT environment variable override."""
        monkeypatch.setenv("HTMLGRAPH_AGENT", "my-custom-agent")
        assert detect_agent_name() == "my-custom-agent"

    def test_detect_agent_with_claude_code_env(self, monkeypatch):
        """Test Claude Code detection via environment variable."""
        monkeypatch.delenv("HTMLGRAPH_AGENT", raising=False)
        monkeypatch.setenv("CLAUDE_CODE_VERSION", "1.0.0")
        assert detect_agent_name() == "claude"

    def test_detect_agent_with_claude_api_key(self, monkeypatch):
        """Test Claude detection via API key."""
        monkeypatch.delenv("HTMLGRAPH_AGENT", raising=False)
        monkeypatch.delenv("CLAUDE_CODE_VERSION", raising=False)
        monkeypatch.setenv("CLAUDE_API_KEY", "sk-test-123")
        assert detect_agent_name() == "claude"

    def test_detect_agent_with_gemini(self, monkeypatch, tmp_path):
        """Test Gemini detection."""
        monkeypatch.delenv("HTMLGRAPH_AGENT", raising=False)
        monkeypatch.delenv("CLAUDE_CODE_VERSION", raising=False)
        monkeypatch.delenv("CLAUDE_API_KEY", raising=False)
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        monkeypatch.setenv(
            "HOME", str(tmp_path)
        )  # Fake home to avoid .claude detection
        assert detect_agent_name() == "gemini"

    def test_detect_agent_with_opencode_version(self, monkeypatch):
        """Test OpenCode detection via version environment variable."""
        # Import the module to patch its internals
        import htmlgraph.agent_detection as ad_module

        # Mock psutil to prevent Claude Code parent process detection
        mock_psutil = Mock()
        mock_process = Mock()
        mock_process.parent.return_value = None  # No parent process
        mock_psutil.Process.return_value = mock_process
        monkeypatch.setattr(ad_module, "psutil", mock_psutil)

        # Mock Path.home() to hide .claude directory
        mock_home = Mock()
        mock_home.exists.return_value = False
        mock_path_home = Mock(return_value=mock_home)
        monkeypatch.setattr(ad_module.Path, "home", mock_path_home)

        # Clear all agent detection vars
        monkeypatch.delenv("HTMLGRAPH_AGENT", raising=False)
        monkeypatch.delenv("CLAUDE_CODE_VERSION", raising=False)
        monkeypatch.delenv("CLAUDE_API_KEY", raising=False)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("CLAUDE_SESSION_ID", raising=False)

        monkeypatch.setenv("OPENCODE_VERSION", "1.0.0")
        assert detect_agent_name() == "opencode"

    def test_detect_agent_with_opencode_api_key(self, monkeypatch):
        """Test OpenCode detection via API key."""
        monkeypatch.delenv("HTMLGRAPH_AGENT", raising=False)
        monkeypatch.delenv("CLAUDE_CODE_VERSION", raising=False)
        monkeypatch.delenv("CLAUDE_API_KEY", raising=False)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        # Also clear potential Claude detection from parent process
        monkeypatch.delenv("CLAUDE_SESSION_ID", raising=False)
        monkeypatch.setenv("OPENCODE_API_KEY", "sk-test-123")
        assert detect_agent_name() == "opencode"

    def test_detect_agent_with_opencode_session_id(self, monkeypatch):
        """Test OpenCode detection via session ID."""
        monkeypatch.delenv("HTMLGRAPH_AGENT", raising=False)
        monkeypatch.delenv("CLAUDE_CODE_VERSION", raising=False)
        monkeypatch.delenv("CLAUDE_API_KEY", raising=False)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        # Also clear potential Claude detection from parent process
        monkeypatch.delenv("CLAUDE_SESSION_ID", raising=False)
        monkeypatch.setenv("OPENCODE_SESSION_ID", "session-abc123")
        assert detect_agent_name() == "opencode"

    def test_detect_agent_defaults_to_cli(self, monkeypatch):
        """Test fallback to CLI when no specific environment detected."""
        # Clear all environment variables
        monkeypatch.delenv("HTMLGRAPH_AGENT", raising=False)
        monkeypatch.delenv("CLAUDE_CODE_VERSION", raising=False)
        monkeypatch.delenv("CLAUDE_API_KEY", raising=False)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)

        # Should default to CLI
        result = detect_agent_name()
        # Could be "claude" if running in Claude Code or "cli" otherwise
        assert result in ["claude", "cli"]


class TestAgentDisplayNames:
    """Test agent display name formatting."""

    def test_get_display_name_claude(self):
        """Test Claude display name."""
        assert get_agent_display_name("claude") == "Claude"
        assert get_agent_display_name("claude-code") == "Claude"

    def test_get_display_name_opencode(self):
        """Test OpenCode display name."""
        assert get_agent_display_name("opencode") == "OpenCode"

    def test_get_display_name_gemini(self):
        """Test Gemini display name."""
        assert get_agent_display_name("gemini") == "Gemini"

    def test_get_display_name_cli(self):
        """Test CLI display name."""
        assert get_agent_display_name("cli") == "CLI"

    def test_get_display_name_models(self):
        """Test model display names."""
        assert get_agent_display_name("haiku") == "Haiku"
        assert get_agent_display_name("opus") == "Opus"
        assert get_agent_display_name("sonnet") == "Sonnet"

    def test_get_display_name_unknown(self):
        """Test unknown agent defaults to title case."""
        assert get_agent_display_name("my-custom-agent") == "My-Custom-Agent"
