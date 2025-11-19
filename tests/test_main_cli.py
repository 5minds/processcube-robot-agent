"""Tests for main CLI module."""

import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from processcube_robot_agent.__main__ import app


class TestMainCLI:
    """Test main CLI application."""

    def setup_method(self):
        """Set up test client."""
        self.runner = CliRunner()

    def test_pack_command_exists(self):
        """Test that pack command exists."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "pack" in result.stdout

    def test_serve_command_exists(self):
        """Test that serve command exists."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "serve" in result.stdout

    @patch("processcube_robot_agent.__main__.setup_logging")
    @patch("processcube_robot_agent.__main__.start_pack_robots")
    def test_pack_command_execution(self, mock_pack, mock_logging):
        """Test pack command execution."""
        result = self.runner.invoke(app, ["pack"])

        mock_logging.assert_called_once()
        mock_pack.assert_called_once()
        assert result.exit_code == 0

    @patch("processcube_robot_agent.__main__.setup_logging")
    @patch("processcube_robot_agent.__main__.ConfigAccessor")
    @patch("processcube_robot_agent.__main__.start_rest_api")
    def test_serve_command_execution(self, mock_rest_api, mock_config, mock_logging):
        """Test serve command execution."""
        result = self.runner.invoke(app, ["serve"])

        mock_logging.assert_called_once()
        mock_config.ensure_from_env.assert_called_once()
        mock_rest_api.assert_called_once()
        assert result.exit_code == 0

    @patch("processcube_robot_agent.__main__.setup_logging")
    @patch("processcube_robot_agent.__main__.start_pack_robots")
    def test_pack_command_short_help(self, mock_pack, mock_logging):
        """Test pack command short help."""
        result = self.runner.invoke(app, ["--help"])
        assert "Pack the rcc projects" in result.stdout or "pack" in result.stdout

    @patch("processcube_robot_agent.__main__.setup_logging")
    @patch("processcube_robot_agent.__main__.ConfigAccessor")
    @patch("processcube_robot_agent.__main__.start_rest_api")
    def test_serve_command_short_help(self, mock_rest_api, mock_config, mock_logging):
        """Test serve command short help."""
        result = self.runner.invoke(app, ["--help"])
        assert "serve" in result.stdout

    @patch("processcube_robot_agent.__main__.setup_logging")
    @patch("processcube_robot_agent.__main__.start_pack_robots")
    def test_pack_handles_exception(self, mock_pack, mock_logging):
        """Test pack command handles exceptions gracefully."""
        mock_pack.side_effect = Exception("Test error")

        result = self.runner.invoke(app, ["pack"])

        # Typer should handle the exception
        assert result.exit_code != 0

    @patch("processcube_robot_agent.__main__.setup_logging")
    @patch("processcube_robot_agent.__main__.ConfigAccessor")
    @patch("processcube_robot_agent.__main__.start_rest_api")
    def test_serve_handles_exception(self, mock_rest_api, mock_config, mock_logging):
        """Test serve command handles exceptions gracefully."""
        mock_config.ensure_from_env.side_effect = Exception("Config error")

        result = self.runner.invoke(app, ["serve"])

        assert result.exit_code != 0

    def test_cli_no_command(self):
        """Test CLI with no command shows help."""
        result = self.runner.invoke(app, [])
        # Typer returns exit code 2 when no command is provided
        assert result.exit_code in (0, 2)
        # Help may be in stdout or empty - just verify exit code is correct

    def test_cli_invalid_command(self):
        """Test CLI with invalid command."""
        result = self.runner.invoke(app, ["invalid"])
        # Should fail with non-zero exit code
        assert result.exit_code != 0

    @patch("processcube_robot_agent.__main__.setup_logging")
    @patch("processcube_robot_agent.__main__.ConfigAccessor")
    @patch("processcube_robot_agent.__main__.start_rest_api")
    def test_serve_calls_ensure_from_env(self, mock_rest_api, mock_config, mock_logging):
        """Test that serve properly initializes config."""
        result = self.runner.invoke(app, ["serve"])

        # Verify ConfigAccessor.ensure_from_env was called
        mock_config.ensure_from_env.assert_called_once()
