"""
Unit tests for watch_robots_command module.

Tests the functionality of starting the robot watcher with ProjectPacker
and ProjectWatcher integration.
"""

import pytest
from unittest.mock import Mock, patch, call, MagicMock
import logging

from processcube_robot_agent.watch_robots_command import start_watch_robots


class TestStartWatchRobots:
    """Test suite for start_watch_robots function."""

    @patch('processcube_robot_agent.watch_robots_command.ProjectWatcher')
    @patch('processcube_robot_agent.watch_robots_command.ProjectPacker')
    @patch('processcube_robot_agent.watch_robots_command.ConfigAccessor')
    def test_start_watch_robots_initializes_packer_and_watcher(
        self,
        mock_config_accessor,
        mock_project_packer_class,
        mock_project_watcher_class
    ):
        """Test that start_watch_robots initializes both ProjectPacker and ProjectWatcher."""
        # Setup
        mock_config = Mock()
        mock_config_accessor.current.return_value = mock_config

        mock_packer = Mock()
        mock_project_packer_class.return_value = mock_packer

        mock_watcher = Mock()
        mock_project_watcher_class.return_value = mock_watcher

        mock_external_task_client = Mock()

        # Execute
        start_watch_robots(mock_external_task_client)

        # Verify ConfigAccessor was called
        mock_config_accessor.ensure_from_env.assert_called_once()
        mock_config_accessor.current.assert_called_once()

        # Verify ProjectPacker was initialized with config
        mock_project_packer_class.assert_called_once_with(mock_config)

        # Verify ProjectPacker.start() was called
        mock_packer.start.assert_called_once()

        # Verify ProjectWatcher was initialized with config and client
        mock_project_watcher_class.assert_called_once_with(
            mock_config,
            mock_external_task_client
        )

        # Verify ProjectWatcher.watch() was called
        mock_watcher.watch.assert_called_once()

    @patch('processcube_robot_agent.watch_robots_command.ProjectWatcher')
    @patch('processcube_robot_agent.watch_robots_command.ProjectPacker')
    @patch('processcube_robot_agent.watch_robots_command.ConfigAccessor')
    def test_start_watch_robots_calls_in_correct_order(
        self,
        mock_config_accessor,
        mock_project_packer_class,
        mock_project_watcher_class
    ):
        """Test that ProjectPacker.start() is called before ProjectWatcher.watch()."""
        # Setup
        call_order = []

        mock_config = Mock()
        mock_config_accessor.current.return_value = mock_config

        mock_packer = Mock()
        mock_packer.start.side_effect = lambda: call_order.append('packer_start')
        mock_project_packer_class.return_value = mock_packer

        mock_watcher = Mock()
        mock_watcher.watch.side_effect = lambda: call_order.append('watcher_watch')
        mock_project_watcher_class.return_value = mock_watcher

        mock_external_task_client = Mock()

        # Execute
        start_watch_robots(mock_external_task_client)

        # Verify correct order
        assert call_order == ['packer_start', 'watcher_watch']

    @patch('processcube_robot_agent.watch_robots_command.ProjectWatcher')
    @patch('processcube_robot_agent.watch_robots_command.ProjectPacker')
    @patch('processcube_robot_agent.watch_robots_command.ConfigAccessor')
    def test_start_watch_robots_with_different_external_task_clients(
        self,
        mock_config_accessor,
        mock_project_packer_class,
        mock_project_watcher_class
    ):
        """Test that start_watch_robots works with different external task clients."""
        # Setup
        mock_config = Mock()
        mock_config_accessor.current.return_value = mock_config

        mock_packer = Mock()
        mock_project_packer_class.return_value = mock_packer

        mock_watcher = Mock()
        mock_project_watcher_class.return_value = mock_watcher

        # Create different mock clients
        client1 = Mock()
        client2 = Mock()

        # Execute with first client
        start_watch_robots(client1)

        # Verify first client was passed
        call_args_1 = mock_project_watcher_class.call_args_list[0]
        assert call_args_1[0][1] == client1

        # Reset and execute with second client
        mock_project_watcher_class.reset_mock()
        mock_packer.reset_mock()
        mock_packer.start.return_value = None
        mock_project_watcher_class.return_value = mock_watcher

        start_watch_robots(client2)

        # Verify second client was passed
        call_args_2 = mock_project_watcher_class.call_args_list[0]
        assert call_args_2[0][1] == client2

    @patch('processcube_robot_agent.watch_robots_command.logger')
    @patch('processcube_robot_agent.watch_robots_command.ProjectWatcher')
    @patch('processcube_robot_agent.watch_robots_command.ProjectPacker')
    @patch('processcube_robot_agent.watch_robots_command.ConfigAccessor')
    def test_start_watch_robots_logs_message(
        self,
        mock_config_accessor,
        mock_project_packer_class,
        mock_project_watcher_class,
        mock_logger
    ):
        """Test that start_watch_robots logs the startup message."""
        # Setup
        mock_config = Mock()
        mock_config_accessor.current.return_value = mock_config

        mock_packer = Mock()
        mock_project_packer_class.return_value = mock_packer

        mock_watcher = Mock()
        mock_project_watcher_class.return_value = mock_watcher

        mock_external_task_client = Mock()

        # Execute
        start_watch_robots(mock_external_task_client)

        # Verify logger was called
        mock_logger.info.assert_called_once()
        log_message = mock_logger.info.call_args[0][0]
        assert 'watch robots' in log_message.lower()
        assert 'pack' in log_message.lower()

    @patch('processcube_robot_agent.watch_robots_command.ProjectWatcher')
    @patch('processcube_robot_agent.watch_robots_command.ProjectPacker')
    @patch('processcube_robot_agent.watch_robots_command.ConfigAccessor')
    def test_start_watch_robots_with_config_accessor_error(
        self,
        mock_config_accessor,
        mock_project_packer_class,
        mock_project_watcher_class
    ):
        """Test that start_watch_robots handles ConfigAccessor errors gracefully."""
        # Setup - ConfigAccessor raises error
        mock_config_accessor.ensure_from_env.side_effect = RuntimeError("Config not found")

        mock_external_task_client = Mock()

        # Execute and verify error is raised
        with pytest.raises(RuntimeError, match="Config not found"):
            start_watch_robots(mock_external_task_client)

        # Verify ProjectPacker and ProjectWatcher were not called
        mock_project_packer_class.assert_not_called()
        mock_project_watcher_class.assert_not_called()

    @patch('processcube_robot_agent.watch_robots_command.ProjectWatcher')
    @patch('processcube_robot_agent.watch_robots_command.ProjectPacker')
    @patch('processcube_robot_agent.watch_robots_command.ConfigAccessor')
    def test_start_watch_robots_with_packer_error(
        self,
        mock_config_accessor,
        mock_project_packer_class,
        mock_project_watcher_class
    ):
        """Test that start_watch_robots handles ProjectPacker errors."""
        # Setup
        mock_config = Mock()
        mock_config_accessor.current.return_value = mock_config

        mock_packer = Mock()
        mock_packer.start.side_effect = RuntimeError("Packing failed")
        mock_project_packer_class.return_value = mock_packer

        mock_external_task_client = Mock()

        # Execute and verify error is raised
        with pytest.raises(RuntimeError, match="Packing failed"):
            start_watch_robots(mock_external_task_client)

        # Verify ProjectWatcher was not called
        mock_project_watcher_class.assert_not_called()

    @patch('processcube_robot_agent.watch_robots_command.ProjectWatcher')
    @patch('processcube_robot_agent.watch_robots_command.ProjectPacker')
    @patch('processcube_robot_agent.watch_robots_command.ConfigAccessor')
    def test_start_watch_robots_with_watcher_error(
        self,
        mock_config_accessor,
        mock_project_packer_class,
        mock_project_watcher_class
    ):
        """Test that start_watch_robots handles ProjectWatcher errors."""
        # Setup
        mock_config = Mock()
        mock_config_accessor.current.return_value = mock_config

        mock_packer = Mock()
        mock_project_packer_class.return_value = mock_packer

        mock_watcher = Mock()
        mock_watcher.watch.side_effect = RuntimeError("Watching failed")
        mock_project_watcher_class.return_value = mock_watcher

        mock_external_task_client = Mock()

        # Execute and verify error is raised
        with pytest.raises(RuntimeError, match="Watching failed"):
            start_watch_robots(mock_external_task_client)

        # Verify packer was started before the error
        mock_packer.start.assert_called_once()