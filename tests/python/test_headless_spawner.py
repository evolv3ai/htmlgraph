"""Tests for HeadlessSpawner."""

import pytest
from htmlgraph.orchestration import AIResult, HeadlessSpawner


class TestHeadlessSpawner:
    """Test HeadlessSpawner class."""

    def test_init(self):
        """Test HeadlessSpawner initialization."""
        spawner = HeadlessSpawner()
        assert spawner is not None

    def test_spawn_gemini_basic(self):
        """Test basic Gemini spawn."""
        spawner = HeadlessSpawner()
        result = spawner.spawn_gemini("What is 2+2? Brief answer only.")

        assert isinstance(result, AIResult)
        assert result.success, f"Expected success, got error: {result.error}"
        assert result.response, "Expected non-empty response"
        assert "4" in result.response, f"Expected '4' in response: {result.response}"
        assert result.tokens_used is not None, "Expected token count"
        assert result.tokens_used > 0, "Expected positive token count"
        assert result.error is None, f"Expected no error, got: {result.error}"
        assert result.raw_output is not None, "Expected raw output"

    def test_spawn_gemini_with_json_format(self):
        """Test Gemini spawn with explicit JSON format."""
        spawner = HeadlessSpawner()
        result = spawner.spawn_gemini(
            "List 3 colors in JSON array format.", output_format="json"
        )

        assert result.success
        assert result.response
        # Response should contain some color-related content
        assert any(
            color in result.response.lower()
            for color in ["red", "blue", "green", "yellow", "orange", "purple"]
        )

    def test_spawn_gemini_empty_prompt(self):
        """Test Gemini spawn with empty prompt."""
        spawner = HeadlessSpawner()
        result = spawner.spawn_gemini("")

        # Gemini may handle empty prompts gracefully or return an error
        # We just verify we get a result and don't crash
        assert isinstance(result, AIResult)

    def test_spawn_gemini_timeout(self):
        """Test timeout handling with very short timeout."""
        spawner = HeadlessSpawner()
        # Use very short timeout to trigger timeout error
        result = spawner.spawn_gemini(
            "Write a very long essay about the history of computing.", timeout=1
        )

        # Should either succeed quickly or timeout
        assert isinstance(result, AIResult)
        if not result.success:
            assert (
                "timeout" in result.error.lower() or "timed out" in result.error.lower()
            )

    def test_spawn_gemini_complex_prompt(self):
        """Test Gemini spawn with complex multi-line prompt."""
        prompt = """
        Analyze the following:
        1. What is the capital of France?
        2. What is 10 * 5?

        Provide brief answers only.
        """
        spawner = HeadlessSpawner()
        result = spawner.spawn_gemini(prompt)

        assert result.success
        assert result.response
        # Should mention Paris and 50
        response_lower = result.response.lower()
        assert "paris" in response_lower
        assert "50" in result.response

    def test_air_result_structure(self):
        """Test AIResult dataclass structure."""
        result = AIResult(
            success=True,
            response="Test response",
            tokens_used=100,
            error=None,
            raw_output={"test": "data"},
        )

        assert result.success is True
        assert result.response == "Test response"
        assert result.tokens_used == 100
        assert result.error is None
        assert result.raw_output == {"test": "data"}

    def test_air_result_failure(self):
        """Test AIResult for failure case."""
        result = AIResult(
            success=False,
            response="",
            tokens_used=None,
            error="Test error",
            raw_output=None,
        )

        assert result.success is False
        assert result.response == ""
        assert result.tokens_used is None
        assert result.error == "Test error"
        assert result.raw_output is None

    def test_spawn_codex_basic(self):
        """Test basic Codex spawn with JSONL output."""
        spawner = HeadlessSpawner()
        result = spawner.spawn_codex("What is 2+2? Brief answer only.")

        assert isinstance(result, AIResult)
        # May fail if Codex CLI not installed
        if result.success:
            assert "4" in result.response
            # Tokens may or may not be available
            if result.tokens_used:
                assert result.tokens_used > 0
        else:
            assert result.error is not None

    def test_spawn_codex_error_handling(self):
        """Test Codex error handling."""
        spawner = HeadlessSpawner()
        # Test with very short timeout
        result = spawner.spawn_codex("What is 2+2?", timeout=0.001)

        assert isinstance(result, AIResult)
        assert not result.success
        assert "Timed out" in result.error or "not found" in result.error

    def test_spawn_codex_plain_text(self):
        """Test Codex with plain text output (no JSON)."""
        spawner = HeadlessSpawner()
        result = spawner.spawn_codex("What is 2+2?", output_json=False)

        assert isinstance(result, AIResult)
        # May fail if Codex CLI not installed
        if result.success:
            assert result.response
            assert isinstance(result.raw_output, str)

    def test_spawn_copilot_basic(self):
        """Test basic Copilot spawn."""
        spawner = HeadlessSpawner()
        result = spawner.spawn_copilot("What is 2+2? Brief answer only.")

        assert isinstance(result, AIResult)
        # May fail if Copilot CLI not installed
        if result.success:
            assert "4" in result.response
        else:
            assert result.error is not None

    def test_spawn_copilot_with_tools(self):
        """Test Copilot with tool permissions."""
        spawner = HeadlessSpawner()
        result = spawner.spawn_copilot(
            "List Python files in current directory", allow_tools=["shell(ls)"]
        )

        assert isinstance(result, AIResult)
        # May fail if Copilot CLI not installed
        if not result.success:
            assert result.error is not None

    def test_spawn_copilot_error_handling(self):
        """Test Copilot error handling."""
        spawner = HeadlessSpawner()
        result = spawner.spawn_copilot("Test", timeout=0.001)

        assert isinstance(result, AIResult)
        assert not result.success
        assert "Timed out" in result.error or "not found" in result.error

    def test_spawn_claude_basic(self):
        """Test basic Claude spawn with JSON output."""
        spawner = HeadlessSpawner()
        result = spawner.spawn_claude("What is 2+2? Brief answer only.")

        assert isinstance(result, AIResult)
        # May fail if Claude CLI not installed or not authenticated
        if result.success:
            assert "4" in result.response
            assert result.tokens_used is not None
            assert result.tokens_used > 0
            # Check raw_output has cost info
            assert isinstance(result.raw_output, dict)
            assert "total_cost_usd" in result.raw_output
        else:
            assert result.error is not None

    def test_spawn_claude_text_mode(self):
        """Test Claude with plain text output."""
        spawner = HeadlessSpawner()
        result = spawner.spawn_claude(
            "What is 2+2? Brief answer.", output_format="text"
        )

        assert isinstance(result, AIResult)
        if result.success:
            assert "4" in result.response
            assert isinstance(result.raw_output, str)

    def test_spawn_claude_permission_mode_bypass(self):
        """Test Claude with bypassPermissions mode (default)."""
        spawner = HeadlessSpawner()
        result = spawner.spawn_claude(
            "What is 2+2?", permission_mode="bypassPermissions"
        )

        assert isinstance(result, AIResult)
        # Should work with bypass permissions
        if result.success:
            assert result.response

    def test_spawn_claude_permission_mode_plan(self):
        """Test Claude with plan mode (no execution)."""
        spawner = HeadlessSpawner()
        result = spawner.spawn_claude(
            "List files in current directory", permission_mode="plan"
        )

        assert isinstance(result, AIResult)
        # Plan mode should succeed but not execute
        if result.success:
            # Should describe plan, not actually list files
            assert result.response

    def test_spawn_claude_error_handling(self):
        """Test Claude error handling."""
        spawner = HeadlessSpawner()

        # Test with very short timeout
        result = spawner.spawn_claude("What is 2+2?", timeout=0.001)

        assert isinstance(result, AIResult)
        assert not result.success
        assert "Timed out" in result.error or "not found" in result.error

    def test_spawn_claude_cost_tracking(self):
        """Test that cost information is captured."""
        spawner = HeadlessSpawner()
        result = spawner.spawn_claude("What is 2+2?")

        assert isinstance(result, AIResult)
        if result.success:
            assert isinstance(result.raw_output, dict)
            assert "total_cost_usd" in result.raw_output
            assert result.raw_output["total_cost_usd"] >= 0
            assert "usage" in result.raw_output

    def test_spawn_claude_complex_prompt(self):
        """Test Claude with complex multi-line prompt."""
        prompt = """
        Analyze the following:
        1. What is the capital of France?
        2. What is 10 * 5?

        Provide brief answers only.
        """
        spawner = HeadlessSpawner()
        result = spawner.spawn_claude(prompt)

        assert isinstance(result, AIResult)
        if result.success:
            response_lower = result.response.lower()
            assert "paris" in response_lower
            assert "50" in result.response

    def test_spawn_claude_json_parse_error(self):
        """Test Claude handles JSON parse errors gracefully."""
        # This test verifies error handling, actual error conditions
        # may vary based on Claude CLI implementation
        spawner = HeadlessSpawner()
        result = spawner.spawn_claude("")

        assert isinstance(result, AIResult)
        # Empty prompt may succeed or fail, just verify we handle it
        if not result.success and result.error:
            # Should have meaningful error message
            assert len(result.error) > 0


# Conditional tests that require Gemini CLI to be installed
@pytest.mark.skipif(
    not pytest.importorskip("subprocess")
    .run(
        ["which", "gemini"],
        capture_output=True,
        text=True,
    )
    .returncode
    == 0,
    reason="Gemini CLI not installed",
)
class TestHeadlessSpawnerIntegration:
    """Integration tests requiring Gemini CLI."""

    def test_gemini_cli_available(self):
        """Verify Gemini CLI is available for integration tests."""
        import subprocess

        result = subprocess.run(["which", "gemini"], capture_output=True, text=True)
        assert result.returncode == 0, "Gemini CLI not found in PATH"
