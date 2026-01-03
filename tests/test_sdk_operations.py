"""Tests for SDK wrapper methods for operations layer."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from htmlgraph import SDK


@pytest.fixture
def sdk(tmp_path: Path) -> SDK:
    """Create SDK instance with temporary directory."""
    graph_dir = tmp_path / ".htmlgraph"
    graph_dir.mkdir(parents=True)
    (graph_dir / "features").mkdir()
    (graph_dir / "sessions").mkdir()
    (graph_dir / "events").mkdir()

    return SDK(directory=str(graph_dir), agent="test-agent")


class TestServerOperations:
    """Test server operation wrappers."""

    @patch("htmlgraph.operations.server.start_server")
    def test_start_server(self, mock_start: MagicMock, sdk: SDK) -> None:
        """Test start_server wrapper calls operations layer."""
        from htmlgraph.operations.server import ServerHandle, ServerStartResult

        mock_handle = ServerHandle(
            url="http://localhost:8080",
            port=8080,
            host="localhost",
            server=None,
        )
        mock_start.return_value = ServerStartResult(
            handle=mock_handle,
            warnings=[],
            config_used={"port": 8080},
        )

        result = sdk.start_server(port=8080, watch=True)

        assert result.handle.url == "http://localhost:8080"
        mock_start.assert_called_once()
        call_kwargs = mock_start.call_args[1]
        assert call_kwargs["port"] == 8080
        assert call_kwargs["watch"] is True
        assert call_kwargs["graph_dir"] == sdk._directory

    @patch("htmlgraph.operations.server.stop_server")
    def test_stop_server(self, mock_stop: MagicMock, sdk: SDK) -> None:
        """Test stop_server wrapper calls operations layer."""
        from htmlgraph.operations.server import ServerHandle

        mock_handle = ServerHandle(
            url="http://localhost:8080",
            port=8080,
            host="localhost",
            server=None,
        )

        sdk.stop_server(mock_handle)

        mock_stop.assert_called_once_with(mock_handle)

    @patch("htmlgraph.operations.server.get_server_status")
    def test_get_server_status(self, mock_status: MagicMock, sdk: SDK) -> None:
        """Test get_server_status wrapper calls operations layer."""
        from htmlgraph.operations.server import ServerHandle, ServerStatus

        mock_handle = ServerHandle(
            url="http://localhost:8080",
            port=8080,
            host="localhost",
            server=None,
        )
        mock_status.return_value = ServerStatus(
            running=True,
            url="http://localhost:8080",
            port=8080,
            host="localhost",
        )

        result = sdk.get_server_status(mock_handle)

        assert result.running is True
        assert result.url == "http://localhost:8080"
        mock_status.assert_called_once_with(mock_handle)


class TestHookOperations:
    """Test hook operation wrappers."""

    @patch("htmlgraph.operations.hooks.install_hooks")
    def test_install_hooks(self, mock_install: MagicMock, sdk: SDK) -> None:
        """Test install_hooks wrapper calls operations layer."""
        from htmlgraph.operations.hooks import HookInstallResult

        mock_install.return_value = HookInstallResult(
            installed=["post-commit", "post-checkout"],
            skipped=[],
            warnings=[],
            config_used={"use_symlinks": True},
        )

        result = sdk.install_hooks(use_copy=False)

        assert "post-commit" in result.installed
        assert "post-checkout" in result.installed
        mock_install.assert_called_once()
        call_kwargs = mock_install.call_args[1]
        assert call_kwargs["project_dir"] == sdk._directory.parent
        assert call_kwargs["use_copy"] is False

    @patch("htmlgraph.operations.hooks.list_hooks")
    def test_list_hooks(self, mock_list: MagicMock, sdk: SDK) -> None:
        """Test list_hooks wrapper calls operations layer."""
        from htmlgraph.operations.hooks import HookListResult

        mock_list.return_value = HookListResult(
            enabled=["post-commit"],
            disabled=["pre-push"],
            missing=["post-checkout"],
        )

        result = sdk.list_hooks()

        assert "post-commit" in result.enabled
        assert "pre-push" in result.disabled
        assert "post-checkout" in result.missing
        mock_list.assert_called_once()
        call_kwargs = mock_list.call_args[1]
        assert call_kwargs["project_dir"] == sdk._directory.parent

    @patch("htmlgraph.operations.hooks.validate_hook_config")
    def test_validate_hook_config(self, mock_validate: MagicMock, sdk: SDK) -> None:
        """Test validate_hook_config wrapper calls operations layer."""
        from htmlgraph.operations.hooks import HookValidationResult

        mock_validate.return_value = HookValidationResult(
            valid=True,
            errors=[],
            warnings=["Unknown hook 'custom-hook'"],
        )

        result = sdk.validate_hook_config()

        assert result.valid is True
        assert len(result.warnings) == 1
        mock_validate.assert_called_once()
        call_kwargs = mock_validate.call_args[1]
        assert call_kwargs["project_dir"] == sdk._directory.parent


class TestEventOperations:
    """Test event operation wrappers."""

    @patch("htmlgraph.operations.events.export_sessions")
    def test_export_sessions(self, mock_export: MagicMock, sdk: SDK) -> None:
        """Test export_sessions wrapper calls operations layer."""
        from htmlgraph.operations.events import EventExportResult

        mock_export.return_value = EventExportResult(
            written=10,
            skipped=2,
            failed=0,
        )

        result = sdk.export_sessions(overwrite=True)

        assert result.written == 10
        assert result.skipped == 2
        assert result.failed == 0
        mock_export.assert_called_once()
        call_kwargs = mock_export.call_args[1]
        assert call_kwargs["graph_dir"] == sdk._directory
        assert call_kwargs["overwrite"] is True

    @patch("htmlgraph.operations.events.rebuild_index")
    def test_rebuild_event_index(self, mock_rebuild: MagicMock, sdk: SDK) -> None:
        """Test rebuild_event_index wrapper calls operations layer."""
        from htmlgraph.operations.events import EventRebuildResult

        mock_rebuild.return_value = EventRebuildResult(
            db_path=sdk._directory / "index.sqlite",
            inserted=100,
            skipped=5,
        )

        result = sdk.rebuild_event_index()

        assert result.inserted == 100
        assert result.skipped == 5
        mock_rebuild.assert_called_once()
        call_kwargs = mock_rebuild.call_args[1]
        assert call_kwargs["graph_dir"] == sdk._directory

    @patch("htmlgraph.operations.events.query_events")
    def test_query_events(self, mock_query: MagicMock, sdk: SDK) -> None:
        """Test query_events wrapper calls operations layer."""
        from htmlgraph.operations.events import EventQueryResult

        mock_events = [
            {
                "session_id": "sess-1",
                "tool": "Bash",
                "timestamp": "2025-01-01T12:00:00Z",
            },
            {
                "session_id": "sess-1",
                "tool": "Edit",
                "timestamp": "2025-01-01T12:05:00Z",
            },
        ]
        mock_query.return_value = EventQueryResult(
            events=mock_events,
            total=2,
        )

        result = sdk.query_events(
            session_id="sess-1",
            tool="Bash",
            limit=10,
        )

        assert result.total == 2
        assert len(result.events) == 2
        mock_query.assert_called_once()
        call_kwargs = mock_query.call_args[1]
        assert call_kwargs["graph_dir"] == sdk._directory
        assert call_kwargs["session_id"] == "sess-1"
        assert call_kwargs["tool"] == "Bash"
        assert call_kwargs["limit"] == 10

    @patch("htmlgraph.operations.events.get_event_stats")
    def test_get_event_stats(self, mock_stats: MagicMock, sdk: SDK) -> None:
        """Test get_event_stats wrapper calls operations layer."""
        from htmlgraph.operations.events import EventStats

        mock_stats.return_value = EventStats(
            total_events=150,
            session_count=10,
            file_count=5,
        )

        result = sdk.get_event_stats()

        assert result.total_events == 150
        assert result.session_count == 10
        assert result.file_count == 5
        mock_stats.assert_called_once()
        call_kwargs = mock_stats.call_args[1]
        assert call_kwargs["graph_dir"] == sdk._directory


class TestAnalyticsOperations:
    """Test analytics operation wrappers."""

    @patch("htmlgraph.operations.analytics.analyze_session")
    def test_analyze_session(self, mock_analyze: MagicMock, sdk: SDK) -> None:
        """Test analyze_session wrapper calls operations layer."""
        from htmlgraph.operations.analytics import AnalyticsSessionResult

        mock_analyze.return_value = AnalyticsSessionResult(
            session_id="sess-123",
            metrics={
                "primary_work_type": "feature",
                "total_events": 50,
                "work_distribution": {"feature": 30, "spike": 20},
            },
            warnings=[],
        )

        result = sdk.analyze_session("sess-123")

        assert result.session_id == "sess-123"
        assert result.metrics["primary_work_type"] == "feature"
        assert result.metrics["total_events"] == 50
        mock_analyze.assert_called_once()
        call_kwargs = mock_analyze.call_args[1]
        assert call_kwargs["graph_dir"] == sdk._directory
        assert call_kwargs["session_id"] == "sess-123"

    @patch("htmlgraph.operations.analytics.analyze_project")
    def test_analyze_project(self, mock_analyze: MagicMock, sdk: SDK) -> None:
        """Test analyze_project wrapper calls operations layer."""
        from htmlgraph.operations.analytics import AnalyticsProjectResult

        mock_analyze.return_value = AnalyticsProjectResult(
            metrics={
                "total_sessions": 20,
                "work_distribution": {"feature": 100, "spike": 50, "maintenance": 30},
                "spike_to_feature_ratio": 0.5,
            },
            warnings=[],
        )

        result = sdk.analyze_project()

        assert result.metrics["total_sessions"] == 20
        assert result.metrics["spike_to_feature_ratio"] == 0.5
        mock_analyze.assert_called_once()
        call_kwargs = mock_analyze.call_args[1]
        assert call_kwargs["graph_dir"] == sdk._directory

    @patch("htmlgraph.operations.analytics.get_recommendations")
    def test_get_work_recommendations(self, mock_recs: MagicMock, sdk: SDK) -> None:
        """Test get_work_recommendations wrapper calls operations layer."""
        from htmlgraph.operations.analytics import RecommendationsResult

        mock_recs.return_value = RecommendationsResult(
            recommendations=[
                {
                    "id": "feat-001",
                    "title": "Implement auth",
                    "score": 0.95,
                    "reasons": ["High priority", "Blocks 5 tasks"],
                }
            ],
            reasoning={"recommendation_count": 1},
            warnings=[],
        )

        result = sdk.get_work_recommendations()

        assert len(result.recommendations) == 1
        assert result.recommendations[0]["id"] == "feat-001"
        assert result.reasoning["recommendation_count"] == 1
        mock_recs.assert_called_once()
        call_kwargs = mock_recs.call_args[1]
        assert call_kwargs["graph_dir"] == sdk._directory


class TestSDKIntegration:
    """Test SDK methods are properly exposed and typed."""

    def test_sdk_has_all_operation_methods(self, sdk: SDK) -> None:
        """Test SDK has all expected operation methods."""
        # Server operations
        assert hasattr(sdk, "start_server")
        assert hasattr(sdk, "stop_server")
        assert hasattr(sdk, "get_server_status")

        # Hook operations
        assert hasattr(sdk, "install_hooks")
        assert hasattr(sdk, "list_hooks")
        assert hasattr(sdk, "validate_hook_config")

        # Event operations
        assert hasattr(sdk, "export_sessions")
        assert hasattr(sdk, "rebuild_event_index")
        assert hasattr(sdk, "query_events")
        assert hasattr(sdk, "get_event_stats")

        # Analytics operations
        assert hasattr(sdk, "analyze_session")
        assert hasattr(sdk, "analyze_project")
        assert hasattr(sdk, "get_work_recommendations")

    def test_operations_in_help(self, sdk: SDK) -> None:
        """Test operations appear in help text."""
        help_text = sdk.help()
        assert "OPERATIONS" in help_text
        assert "start_server" in help_text
        assert "install_hooks" in help_text
        assert "export_sessions" in help_text
        assert "analyze_project" in help_text

    def test_operations_help_topic(self, sdk: SDK) -> None:
        """Test operations help topic."""
        help_text = sdk.help("operations")
        assert "SERVER OPERATIONS" in help_text
        assert "HOOK OPERATIONS" in help_text
        assert "EVENT OPERATIONS" in help_text
        assert "ANALYTICS OPERATIONS" in help_text

    def test_operations_in_dir(self, sdk: SDK) -> None:
        """Test operations appear in __dir__ output."""
        dir_output = dir(sdk)

        # Check priority methods appear early
        assert "start_server" in dir_output
        assert "install_hooks" in dir_output
        assert "export_sessions" in dir_output
        assert "analyze_project" in dir_output
