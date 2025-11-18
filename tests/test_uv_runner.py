"""Unit tests for UvRunner class."""

import pytest
from unittest.mock import patch, MagicMock
from processcube_robot_agent.robot_agent.uv.uv_runner import UvRunner
from processcube_robot_agent.robot_agent.error import RobotError


class TestUvRunnerCheckUv:
    """Tests for check_uv method."""

    @patch('subprocess.run')
    def test_check_uv_success(self, mock_run):
        """Test check_uv when UV is available."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="uv 0.1.0"
        )
        runner = UvRunner()

        result = runner.check_uv()

        assert result.returncode == 0
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_check_uv_failure(self, mock_run):
        """Test check_uv when UV is not available."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stderr="command not found"
        )
        runner = UvRunner()

        with pytest.raises(RobotError) as exc_info:
            runner.check_uv()

        assert "uv" in str(exc_info.value).lower()

    @patch('subprocess.run')
    def test_check_uv_uses_argument_list(self, mock_run):
        """Test that check_uv uses argument list (not shell=True)."""
        mock_run.return_value = MagicMock(returncode=0)
        runner = UvRunner()

        runner.check_uv()

        call_args = mock_run.call_args
        # Check first argument is a list
        assert isinstance(call_args[0][0], list)
        assert call_args[0][0] == ["uv", "self", "version"]

    @patch('subprocess.run')
    def test_check_uv_uses_text_mode(self, mock_run):
        """Test that check_uv uses text=True for proper encoding."""
        mock_run.return_value = MagicMock(returncode=0)
        runner = UvRunner()

        runner.check_uv()

        call_args = mock_run.call_args
        assert call_args[1].get("text") is True

    @patch('subprocess.run')
    def test_check_uv_captures_output(self, mock_run):
        """Test that check_uv captures subprocess output."""
        mock_run.return_value = MagicMock(returncode=0)
        runner = UvRunner()

        runner.check_uv()

        call_args = mock_run.call_args
        assert call_args[1].get("capture_output") is True

    @patch('subprocess.run')
    def test_check_uv_includes_stderr_in_error(self, mock_run):
        """Test that error message includes stderr."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stderr="UV command not found in PATH"
        )
        runner = UvRunner()

        with pytest.raises(RobotError) as exc_info:
            runner.check_uv()

        error_msg = str(exc_info.value)
        assert "UV command not found in PATH" in error_msg or "Stderr" in error_msg
