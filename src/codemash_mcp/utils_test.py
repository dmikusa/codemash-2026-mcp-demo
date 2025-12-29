from logging import LogRecord
from unittest.mock import Mock, patch

from codemash_mcp.utils import JsonFormatter, McpRunner


class TestJsonFormatter:
    @patch("time.time_ns", return_value=1756322648754000000)
    def test_should_format_log_record_as_json(self, mock_time_ns):
        f = JsonFormatter()
        assert (
            f.format(
                LogRecord(
                    "test-name",
                    2,
                    "test-path",
                    123,
                    "foo %s",
                    ("bar",),
                    None,
                    None,
                    None,
                )
            )
            == '{"timestamp": "2025-08-27 19:24:08,754", "level": "Level 2", "message": "foo bar", "module": "test-path", "name": "test-name", "mcp": {}}'
        )

    @patch.object(JsonFormatter, "formatException", return_value="formatted exception")
    @patch("time.time_ns", return_value=1756322648754000000)
    def test_should_format_log_record_with_exception_as_json(
        self, mock_time_ns, mock_format_exception
    ):
        f = JsonFormatter()
        exc_info = (ZeroDivisionError, ZeroDivisionError("test"), None)
        assert (
            f.format(
                LogRecord(
                    "test-name",
                    2,
                    "test-path",
                    123,
                    "foo %s",
                    ("bar",),
                    exc_info,
                    None,
                    None,
                )
            )
            == '{"timestamp": "2025-08-27 19:24:08,754", "level": "Level 2", "message": "foo bar", "module": "test-path", "name": "test-name", "mcp": {}, "exception": "formatted exception"}'
        )
        mock_format_exception.assert_called_once_with(exc_info)


class TestMcpRunner:
    def test_should_call_test_and_return_mcp(self):
        mock_fastmcp = Mock()
        runner = McpRunner(mock_fastmcp)
        assert runner.test() == mock_fastmcp

    def test_should_call_run_on_mcp_server(self):
        mock_fastmcp = Mock()
        mock_fastmcp.run = Mock()

        runner = McpRunner(mock_fastmcp)
        runner.run()

        mock_fastmcp.run.assert_called_once_with(transport="streamable-http")

    def test_should_call_app_mcp_server(self):
        mock_fastmcp = Mock()
        mock_fastmcp.run = Mock()

        runner = McpRunner(mock_fastmcp)
        runner.host()

        mock_fastmcp.http_app.assert_called_once_with(transport="streamable-http")
