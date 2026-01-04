"""Tests for HeadlessSpawner parent session context integration."""

import os
from unittest.mock import Mock, patch

import pytest
from htmlgraph.orchestration.headless_spawner import HeadlessSpawner


@pytest.fixture
def clean_env():
    """Clean environment variables before and after tests."""
    env_vars = [
        "HTMLGRAPH_PARENT_SESSION",
        "HTMLGRAPH_PARENT_AGENT",
        "HTMLGRAPH_PARENT_ACTIVITY",
        "HTMLGRAPH_NESTING_DEPTH",
    ]
    # Clean before test
    for var in env_vars:
        os.environ.pop(var, None)

    yield

    # Clean after test
    for var in env_vars:
        os.environ.pop(var, None)


def test_spawner_uses_parent_session_from_env(clean_env):
    """Test HeadlessSpawner reads parent session from environment."""
    os.environ["HTMLGRAPH_PARENT_SESSION"] = "sess-test-parent"
    os.environ["HTMLGRAPH_PARENT_AGENT"] = "orchestrator"
    os.environ["HTMLGRAPH_PARENT_ACTIVITY"] = "evt-task-123"
    os.environ["HTMLGRAPH_NESTING_DEPTH"] = "1"

    spawner = HeadlessSpawner()

    # Mock SDK to avoid requiring active session
    with patch("htmlgraph.sdk.SDK") as mock_sdk_class:
        mock_sdk_instance = Mock()
        mock_sdk_class.return_value = mock_sdk_instance

        sdk = spawner._get_sdk()

        assert sdk is not None
        # Verify SDK was instantiated with correct parameters
        mock_sdk_class.assert_called_once_with(
            agent="spawner-orchestrator",
            parent_session="sess-test-parent",
        )


def test_spawner_fallback_without_parent_session(clean_env):
    """Test HeadlessSpawner works without parent session (backward compat)."""
    # Ensure no parent session in environment
    assert "HTMLGRAPH_PARENT_SESSION" not in os.environ

    spawner = HeadlessSpawner()

    # Mock SDK to avoid requiring active session
    with patch("htmlgraph.sdk.SDK") as mock_sdk_class:
        mock_sdk_instance = Mock()
        mock_sdk_class.return_value = mock_sdk_instance

        sdk = spawner._get_sdk()

        # Should still create SDK, just without parent session
        assert sdk is not None
        mock_sdk_class.assert_called_once_with(
            agent="spawner",
            parent_session=None,
        )


def test_spawner_uses_parent_agent_in_agent_name(clean_env):
    """Test HeadlessSpawner uses parent agent name in SDK agent parameter."""
    os.environ["HTMLGRAPH_PARENT_AGENT"] = "orchestrator"

    spawner = HeadlessSpawner()

    with patch("htmlgraph.sdk.SDK") as mock_sdk_class:
        mock_sdk_instance = Mock()
        mock_sdk_class.return_value = mock_sdk_instance

        sdk = spawner._get_sdk()

        assert sdk is not None
        # Verify agent name includes parent agent
        call_args = mock_sdk_class.call_args
        assert call_args[1]["agent"] == "spawner-orchestrator"


def test_tracked_gemini_events_include_parent_context(clean_env):
    """Test tracked Gemini events include parent activity and nesting depth."""
    os.environ["HTMLGRAPH_PARENT_SESSION"] = "sess-parent"
    os.environ["HTMLGRAPH_PARENT_ACTIVITY"] = "evt-parent-task"
    os.environ["HTMLGRAPH_NESTING_DEPTH"] = "2"

    spawner = HeadlessSpawner()

    # Mock Gemini response with tool call
    mock_output = """{"type":"init"}
{"type":"tool_use","tool_name":"Bash","parameters":{"command":"ls"}}
{"type":"tool_result","status":"success","tool_id":"tool-1"}
{"type":"result","stats":{}}"""

    # Mock SDK
    mock_sdk = Mock()
    mock_sdk.track_activity = Mock()

    # Parse events (should add parent context)
    events = spawner._parse_and_track_gemini_events(mock_output, mock_sdk)

    # Verify events were parsed
    assert len(events) == 4
    assert events[1]["type"] == "tool_use"

    # Verify tracking calls included parent context
    assert mock_sdk.track_activity.called
    calls = mock_sdk.track_activity.call_args_list

    # Check tool_use tracking call
    tool_use_call = calls[0]
    payload = tool_use_call[1]["payload"]
    assert payload["parent_activity"] == "evt-parent-task"
    assert payload["nesting_depth"] == 2
    assert payload["tool_name"] == "Bash"


def test_tracked_codex_events_include_parent_context(clean_env):
    """Test tracked Codex events include parent activity and nesting depth."""
    os.environ["HTMLGRAPH_PARENT_SESSION"] = "sess-parent"
    os.environ["HTMLGRAPH_PARENT_ACTIVITY"] = "evt-parent-task"
    os.environ["HTMLGRAPH_NESTING_DEPTH"] = "3"

    spawner = HeadlessSpawner()

    # Mock Codex JSONL response
    mock_output = """{"type":"item.started","item":{"type":"command_execution","command":"git status"}}
{"type":"item.completed","item":{"type":"agent_message","text":"Analysis complete"}}
{"type":"turn.completed","usage":{"input_tokens":100,"output_tokens":50}}"""

    # Mock SDK
    mock_sdk = Mock()
    mock_sdk.track_activity = Mock()

    # Parse events
    events = spawner._parse_and_track_codex_events(mock_output, mock_sdk)

    # Verify events were parsed
    assert len(events) == 3

    # Verify tracking calls included parent context
    assert mock_sdk.track_activity.called
    calls = mock_sdk.track_activity.call_args_list

    # Check command execution tracking call
    cmd_call = calls[0]
    payload = cmd_call[1]["payload"]
    assert payload["parent_activity"] == "evt-parent-task"
    assert payload["nesting_depth"] == 3
    assert payload["command"] == "git status"


def test_tracked_copilot_events_include_parent_context(clean_env):
    """Test tracked Copilot events include parent activity and nesting depth."""
    os.environ["HTMLGRAPH_PARENT_SESSION"] = "sess-parent"
    os.environ["HTMLGRAPH_PARENT_ACTIVITY"] = "evt-parent-task"
    os.environ["HTMLGRAPH_NESTING_DEPTH"] = "1"

    spawner = HeadlessSpawner()

    # Mock SDK
    mock_sdk = Mock()
    mock_sdk.track_activity = Mock()

    # Parse events (Copilot is synthetic)
    prompt = "Analyze this code"
    response = "Code looks good"
    events = spawner._parse_and_track_copilot_events(prompt, response, mock_sdk)

    # Verify events were created
    assert len(events) == 2

    # Verify tracking calls included parent context
    assert mock_sdk.track_activity.called
    calls = mock_sdk.track_activity.call_args_list

    # Check start tracking call
    start_call = calls[0]
    start_payload = start_call[1]["payload"]
    assert start_payload["parent_activity"] == "evt-parent-task"
    assert start_payload["nesting_depth"] == 1

    # Check result tracking call
    result_call = calls[1]
    result_payload = result_call[1]["payload"]
    assert result_payload["parent_activity"] == "evt-parent-task"
    assert result_payload["nesting_depth"] == 1


def test_nesting_depth_zero_excluded_from_payload(clean_env):
    """Test that nesting_depth=0 is excluded from payload (not included)."""
    os.environ["HTMLGRAPH_NESTING_DEPTH"] = "0"

    spawner = HeadlessSpawner()

    # Mock Gemini response
    mock_output = """{"type":"tool_use","tool_name":"Read","parameters":{}}"""

    # Mock SDK
    mock_sdk = Mock()
    mock_sdk.track_activity = Mock()

    # Parse events
    spawner._parse_and_track_gemini_events(mock_output, mock_sdk)

    # Verify nesting_depth not in payload when zero
    call_payload = mock_sdk.track_activity.call_args[1]["payload"]
    assert "nesting_depth" not in call_payload


def test_invalid_nesting_depth_defaults_to_zero(clean_env):
    """Test that invalid nesting depth defaults to 0 (excluded from payload)."""
    os.environ["HTMLGRAPH_NESTING_DEPTH"] = "invalid"

    spawner = HeadlessSpawner()

    # Mock Gemini response
    mock_output = """{"type":"tool_use","tool_name":"Read","parameters":{}}"""

    # Mock SDK
    mock_sdk = Mock()
    mock_sdk.track_activity = Mock()

    # Parse events
    spawner._parse_and_track_gemini_events(mock_output, mock_sdk)

    # Verify nesting_depth not in payload (defaults to 0)
    call_payload = mock_sdk.track_activity.call_args[1]["payload"]
    assert "nesting_depth" not in call_payload


def test_no_parent_activity_excluded_from_payload(clean_env):
    """Test that missing parent_activity is excluded from payload."""
    os.environ["HTMLGRAPH_NESTING_DEPTH"] = "2"
    # No HTMLGRAPH_PARENT_ACTIVITY set

    spawner = HeadlessSpawner()

    # Mock Gemini response
    mock_output = """{"type":"tool_use","tool_name":"Read","parameters":{}}"""

    # Mock SDK
    mock_sdk = Mock()
    mock_sdk.track_activity = Mock()

    # Parse events
    spawner._parse_and_track_gemini_events(mock_output, mock_sdk)

    # Verify parent_activity not in payload when not set
    call_payload = mock_sdk.track_activity.call_args[1]["payload"]
    assert "parent_activity" not in call_payload
    # But nesting_depth should be included
    assert call_payload["nesting_depth"] == 2


def test_sdk_creation_error_returns_none(clean_env):
    """Test that SDK creation errors are handled gracefully."""
    os.environ["HTMLGRAPH_PARENT_SESSION"] = "sess-test"

    spawner = HeadlessSpawner()

    # Mock SDK to raise exception
    with patch("htmlgraph.sdk.SDK") as mock_sdk_class:
        mock_sdk_class.side_effect = Exception("SDK unavailable")

        sdk = spawner._get_sdk()

        # Should return None on error
        assert sdk is None
