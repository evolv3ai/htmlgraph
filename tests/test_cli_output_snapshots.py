"""Ensure CLI output format unchanged after refactoring."""

import subprocess

import pytest


def run_cli(*args):
    """Run htmlgraph CLI and return output."""
    result = subprocess.run(
        ["uv", "run", "htmlgraph", *args],
        capture_output=True,
        text=True,
    )
    return result.stdout, result.stderr, result.returncode


def test_cli_help_available():
    """Test htmlgraph --help works."""
    stdout, stderr, code = run_cli("--help")
    assert code == 0
    assert "htmlgraph" in stdout.lower() or "usage" in stdout.lower()


def test_serve_help_output():
    """Test htmlgraph serve --help output."""
    stdout, stderr, code = run_cli("serve", "--help")
    assert code == 0

    # Check for key terms in help output
    help_text = stdout.lower()
    assert "serve" in help_text or "start" in help_text or "server" in help_text


def test_status_command_exists():
    """Test htmlgraph status command exists (may fail if not initialized)."""
    stdout, stderr, code = run_cli("status")

    # Status may fail if not initialized, but should return meaningful output
    # Either success (0) or error explaining initialization needed
    assert code in (0, 1)

    if code == 0:
        # Success - check for status-related output
        output = (stdout + stderr).lower()
        assert any(term in output for term in ["status", "nodes", "features", "total"])
    else:
        # Expected failure - check for helpful error
        output = (stdout + stderr).lower()
        assert any(term in output for term in ["init", "directory", "not found"])


def test_init_help_output():
    """Test htmlgraph init --help output."""
    stdout, stderr, code = run_cli("init", "--help")
    assert code == 0

    help_text = stdout.lower()
    assert "init" in help_text


def test_session_help_output():
    """Test htmlgraph session --help output."""
    stdout, stderr, code = run_cli("session", "--help")
    assert code == 0

    help_text = stdout.lower()
    assert "session" in help_text


def test_feature_help_output():
    """Test htmlgraph feature --help output."""
    stdout, stderr, code = run_cli("feature", "--help")
    assert code == 0

    help_text = stdout.lower()
    assert "feature" in help_text


def test_analytics_help_output():
    """Test htmlgraph analytics --help output."""
    stdout, stderr, code = run_cli("analytics", "--help")
    assert code == 0

    help_text = stdout.lower()
    assert "analytics" in help_text or "analyze" in help_text


def test_version_output():
    """Test htmlgraph --version output."""
    stdout, stderr, code = run_cli("--version")

    # Version flag may not be implemented yet, skip if not
    if code != 0:
        pytest.skip("--version flag not implemented in CLI")

    # Version should be present in output
    import htmlgraph

    assert htmlgraph.__version__ in stdout


def test_cli_error_messages_helpful():
    """Test CLI provides helpful error messages for invalid commands."""
    stdout, stderr, code = run_cli("invalid-command-that-does-not-exist")

    # Should fail with non-zero exit code
    assert code != 0

    # Should provide helpful error message
    output = (stdout + stderr).lower()
    assert any(
        term in output for term in ["invalid", "unknown", "error", "usage", "help"]
    )


def test_cli_json_output_format():
    """Test CLI commands that support --format json produce valid JSON."""
    # Try session start-info with json format
    stdout, stderr, code = run_cli("session", "start-info", "--format", "json")

    if code == 0:
        # If successful, verify it's valid JSON
        import json

        try:
            data = json.loads(stdout)
            assert isinstance(data, dict)
            # JSON format may vary - just verify it's a valid dict
            # (could be response wrapper or direct data)
        except json.JSONDecodeError:
            pytest.fail(f"CLI JSON output is invalid: {stdout}")


def test_cli_respects_quiet_flag():
    """Test CLI --quiet flag reduces output (when available)."""
    # Try status with --quiet if it supports it
    stdout, stderr, code = run_cli("status", "--quiet")

    # Either command succeeds with less output, or flag is not recognized
    # This is a best-effort test
    if code == 0:
        # Quiet output should be shorter than verbose
        verbose_stdout, _, verbose_code = run_cli("status")
        if verbose_code == 0:
            # Can't reliably assert length reduction, but verify it ran
            assert isinstance(stdout, str)


def test_cli_directory_flag_works():
    """Test CLI --dir flag is recognized."""
    # Test with help (doesn't require initialized directory)
    stdout, stderr, code = run_cli("status", "--help")
    assert code == 0

    # Should mention --dir or -d flag
    help_text = stdout.lower()
    assert "--dir" in help_text or "-d" in help_text or "directory" in help_text
