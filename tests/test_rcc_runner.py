"""Unit tests for RccRunner class."""

import pytest
from unittest.mock import patch, MagicMock
from processcube_robot_agent.robot_agent.rcc.rcc_runner import RccRunner
from processcube_robot_agent.robot_agent.error import RobotError


class TestRccRunnerCheckRcc:
    """Tests for check_rcc method."""

    @patch('subprocess.run')
    def test_check_rcc_success(self, mock_run):
        """Test check_rcc when RCC is available."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="RCC version 12.0.0"
        )
        runner = RccRunner()

        result = runner.check_rcc()

        assert result.returncode == 0
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_check_rcc_failure(self, mock_run):
        """Test check_rcc when RCC is not available."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stderr="command not found"
        )
        runner = RccRunner()

        with pytest.raises(RobotError) as exc_info:
            runner.check_rcc()

        assert "rcc" in str(exc_info.value).lower()

    @patch('subprocess.run')
    def test_check_rcc_uses_argument_list(self, mock_run):
        """Test that check_rcc uses argument list (not shell=True)."""
        mock_run.return_value = MagicMock(returncode=0)
        runner = RccRunner()

        runner.check_rcc()

        call_args = mock_run.call_args
        # Check first argument is a list
        assert isinstance(call_args[0][0], list)
        assert call_args[0][0] == ["rcc", "version"]

    @patch('subprocess.run')
    def test_check_rcc_uses_text_mode(self, mock_run):
        """Test that check_rcc uses text=True for proper encoding."""
        mock_run.return_value = MagicMock(returncode=0)
        runner = RccRunner()

        runner.check_rcc()

        call_args = mock_run.call_args
        assert call_args[1].get("text") is True

    @patch('subprocess.run')
    def test_check_rcc_captures_output(self, mock_run):
        """Test that check_rcc captures subprocess output."""
        mock_run.return_value = MagicMock(returncode=0)
        runner = RccRunner()

        runner.check_rcc()

        call_args = mock_run.call_args
        assert call_args[1].get("capture_output") is True

    @patch('subprocess.run')
    def test_check_rcc_includes_stderr_in_error(self, mock_run):
        """Test that error message includes stderr."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stderr="RCC command not found in PATH"
        )
        runner = RccRunner()

        with pytest.raises(RobotError) as exc_info:
            runner.check_rcc()

        error_msg = str(exc_info.value)
        assert "RCC command not found in PATH" in error_msg or "Stderr" in error_msg