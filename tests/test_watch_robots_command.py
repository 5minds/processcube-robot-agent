"""
Unit tests for watch_robots_command module.

Tests the functionality of starting the robot watcher with both RCC and UV
ProjectPacker and ProjectWatcher integration.
"""

import pytest
from unittest.mock import Mock, patch, call, MagicMock
import logging

from processcube_robot_agent.watch_robots_command import start_watch_robots


class TestStartWatchRobots:
    """Test suite for start_watch_robots function."""

    @patch('processcube_robot_agent.watch_robots_command.ThreadPoolExecutor')
    @patch('processcube_robot_agent.watch_robots_command.UvProjectWatcher')
    @patch('processcube_robot_agent.watch_robots_command.RccProjectWatcher')
    @patch('processcube_robot_agent.watch_robots_command.UvProjectPacker')
    @patch('processcube_robot_agent.watch_robots_command.RccProjectPacker')
    @patch('processcube_robot_agent.watch_robots_command.ConfigAccessor')
    def test_start_watch_robots_initializes_both_packers_and_watchers(
        self,
        mock_config_accessor,
        mock_rcc_packer_class,
        mock_uv_packer_class,
        mock_rcc_watcher_class,
        mock_uv_watcher_class,
        mock_executor_class
    ):
        """Test that start_watch_robots initializes both RCC and UV packer/watcher pairs."""
        # Setup
        mock_config = Mock()
        mock_config_accessor.current.return_value = mock_config

        mock_rcc_packer = Mock()
        mock_rcc_packer_class.return_value = mock_rcc_packer

        mock_uv_packer = Mock()
        mock_uv_packer_class.return_value = mock_uv_packer

        mock_rcc_watcher = Mock()
        mock_rcc_watcher_class.return_value = mock_rcc_watcher

        mock_uv_watcher = Mock()
        mock_uv_watcher_class.return_value = mock_uv_watcher

        mock_executor = Mock()
        mock_executor_class.return_value = mock_executor

        mock_external_task_client = Mock()

        # Execute
        start_watch_robots(mock_external_task_client)

        # Verify ConfigAccessor was called
        mock_config_accessor.ensure_from_env.assert_called_once()
        mock_config_accessor.current.assert_called_once()

        # Verify both packers were initialized with config
        mock_rcc_packer_class.assert_called_once_with(mock_config)
        mock_uv_packer_class.assert_called_once_with(mock_config)

        # Verify both packers' start() were called
        mock_rcc_packer.start.assert_called_once()
        mock_uv_packer.start.assert_called_once()

        # Verify both watchers were initialized with config and client
        mock_rcc_watcher_class.assert_called_once_with(mock_config, mock_external_task_client)
        mock_uv_watcher_class.assert_called_once_with(mock_config, mock_external_task_client)

        # Verify both watchers' watch() were submitted to executor
        assert mock_executor.submit.call_count == 2

    @patch('processcube_robot_agent.watch_robots_command.ThreadPoolExecutor')
    @patch('processcube_robot_agent.watch_robots_command.UvProjectWatcher')
    @patch('processcube_robot_agent.watch_robots_command.RccProjectWatcher')
    @patch('processcube_robot_agent.watch_robots_command.UvProjectPacker')
    @patch('processcube_robot_agent.watch_robots_command.RccProjectPacker')
    @patch('processcube_robot_agent.watch_robots_command.ConfigAccessor')
    def test_start_watch_robots_calls_in_correct_order(
        self,
        mock_config_accessor,
        mock_rcc_packer_class,
        mock_uv_packer_class,
        mock_rcc_watcher_class,
        mock_uv_watcher_class,
        mock_executor_class
    ):
        """Test that packers are called before watchers."""
        # Setup
        call_order = []

        mock_config = Mock()
        mock_config_accessor.current.return_value = mock_config

        mock_rcc_packer = Mock()
        mock_rcc_packer.start.side_effect = lambda: call_order.append('rcc_packer_start')
        mock_rcc_packer_class.return_value = mock_rcc_packer

        mock_uv_packer = Mock()
        mock_uv_packer.start.side_effect = lambda: call_order.append('uv_packer_start')
        mock_uv_packer_class.return_value = mock_uv_packer

        mock_rcc_watcher = Mock()
        mock_rcc_watcher_class.return_value = mock_rcc_watcher

        mock_uv_watcher = Mock()
        mock_uv_watcher_class.return_value = mock_uv_watcher

        mock_executor = Mock()
        def submit_track(func):
            call_order.append(f'submit_{func.__name__ if hasattr(func, "__name__") else "watcher"}')
        mock_executor.submit.side_effect = submit_track
        mock_executor_class.return_value = mock_executor

        mock_external_task_client = Mock()

        # Execute
        start_watch_robots(mock_external_task_client)

        # Verify packers start before executor.submit calls
        packer_indices = [i for i, call_name in enumerate(call_order) if 'packer' in call_name]
        submit_indices = [i for i, call_name in enumerate(call_order) if 'submit' in call_name]
        assert all(p < s for p in packer_indices for s in submit_indices), \
            f"Expected all packers to run before watcher submits, got order: {call_order}"

    @patch('processcube_robot_agent.watch_robots_command.ThreadPoolExecutor')
    @patch('processcube_robot_agent.watch_robots_command.UvProjectWatcher')
    @patch('processcube_robot_agent.watch_robots_command.RccProjectWatcher')
    @patch('processcube_robot_agent.watch_robots_command.UvProjectPacker')
    @patch('processcube_robot_agent.watch_robots_command.RccProjectPacker')
    @patch('processcube_robot_agent.watch_robots_command.ConfigAccessor')
    def test_start_watch_robots_with_different_external_task_clients(
        self,
        mock_config_accessor,
        mock_rcc_packer_class,
        mock_uv_packer_class,
        mock_rcc_watcher_class,
        mock_uv_watcher_class,
        mock_executor_class
    ):
        """Test that start_watch_robots works with different external task clients."""
        # Setup
        mock_config = Mock()
        mock_config_accessor.current.return_value = mock_config

        mock_rcc_packer = Mock()
        mock_rcc_packer_class.return_value = mock_rcc_packer

        mock_uv_packer = Mock()
        mock_uv_packer_class.return_value = mock_uv_packer

        mock_rcc_watcher = Mock()
        mock_rcc_watcher_class.return_value = mock_rcc_watcher

        mock_uv_watcher = Mock()
        mock_uv_watcher_class.return_value = mock_uv_watcher

        mock_executor = Mock()
        mock_executor_class.return_value = mock_executor

        client1 = Mock()

        # Execute with first client
        start_watch_robots(client1)

        # Verify both watchers were called with client1
        rcc_call = mock_rcc_watcher_class.call_args_list[0]
        assert rcc_call[0][1] == client1

        uv_call = mock_uv_watcher_class.call_args_list[0]
        assert uv_call[0][1] == client1

    @patch('processcube_robot_agent.watch_robots_command.ThreadPoolExecutor')
    @patch('processcube_robot_agent.watch_robots_command.UvProjectWatcher')
    @patch('processcube_robot_agent.watch_robots_command.RccProjectWatcher')
    @patch('processcube_robot_agent.watch_robots_command.UvProjectPacker')
    @patch('processcube_robot_agent.watch_robots_command.RccProjectPacker')
    @patch('processcube_robot_agent.watch_robots_command.logger')
    @patch('processcube_robot_agent.watch_robots_command.ConfigAccessor')
    def test_start_watch_robots_logs_message(
        self,
        mock_config_accessor,
        mock_logger,
        mock_rcc_packer_class,
        mock_uv_packer_class,
        mock_rcc_watcher_class,
        mock_uv_watcher_class,
        mock_executor_class
    ):
        """Test that start_watch_robots logs startup messages."""
        # Setup
        mock_config = Mock()
        mock_config_accessor.current.return_value = mock_config

        mock_rcc_packer = Mock()
        mock_rcc_packer_class.return_value = mock_rcc_packer

        mock_uv_packer = Mock()
        mock_uv_packer_class.return_value = mock_uv_packer

        mock_rcc_watcher = Mock()
        mock_rcc_watcher_class.return_value = mock_rcc_watcher

        mock_uv_watcher = Mock()
        mock_uv_watcher_class.return_value = mock_uv_watcher

        mock_executor = Mock()
        mock_executor_class.return_value = mock_executor

        mock_external_task_client = Mock()

        # Execute
        start_watch_robots(mock_external_task_client)

        # Verify logger.info was called with expected messages
        assert mock_logger.info.call_count >= 2  # At least initial and final messages
        log_messages = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any('watch robots' in msg.lower() for msg in log_messages)

    @patch('processcube_robot_agent.watch_robots_command.ThreadPoolExecutor')
    @patch('processcube_robot_agent.watch_robots_command.UvProjectWatcher')
    @patch('processcube_robot_agent.watch_robots_command.RccProjectWatcher')
    @patch('processcube_robot_agent.watch_robots_command.UvProjectPacker')
    @patch('processcube_robot_agent.watch_robots_command.RccProjectPacker')
    @patch('processcube_robot_agent.watch_robots_command.ConfigAccessor')
    def test_start_watch_robots_handles_rcc_packer_error(
        self,
        mock_config_accessor,
        mock_rcc_packer_class,
        mock_uv_packer_class,
        mock_rcc_watcher_class,
        mock_uv_watcher_class,
        mock_executor_class
    ):
        """Test that RCC packer errors are handled gracefully."""
        # Setup
        mock_config = Mock()
        mock_config_accessor.current.return_value = mock_config

        mock_rcc_packer = Mock()
        mock_rcc_packer.start.side_effect = RuntimeError("RCC packing failed")
        mock_rcc_packer_class.return_value = mock_rcc_packer

        mock_uv_packer = Mock()
        mock_uv_packer_class.return_value = mock_uv_packer

        mock_rcc_watcher = Mock()
        mock_rcc_watcher_class.return_value = mock_rcc_watcher

        mock_uv_watcher = Mock()
        mock_uv_watcher_class.return_value = mock_uv_watcher

        mock_executor = Mock()
        mock_executor_class.return_value = mock_executor

        mock_external_task_client = Mock()

        # Execute - should not raise
        start_watch_robots(mock_external_task_client)

        # Verify UV packer still ran despite RCC error
        mock_uv_packer.start.assert_called_once()

        # Verify watchers were still initialized
        mock_uv_watcher_class.assert_called_once()

    @patch('processcube_robot_agent.watch_robots_command.ThreadPoolExecutor')
    @patch('processcube_robot_agent.watch_robots_command.UvProjectWatcher')
    @patch('processcube_robot_agent.watch_robots_command.RccProjectWatcher')
    @patch('processcube_robot_agent.watch_robots_command.UvProjectPacker')
    @patch('processcube_robot_agent.watch_robots_command.RccProjectPacker')
    @patch('processcube_robot_agent.watch_robots_command.ConfigAccessor')
    def test_start_watch_robots_handles_uv_packer_error(
        self,
        mock_config_accessor,
        mock_rcc_packer_class,
        mock_uv_packer_class,
        mock_rcc_watcher_class,
        mock_uv_watcher_class,
        mock_executor_class
    ):
        """Test that UV packer errors are handled gracefully."""
        # Setup
        mock_config = Mock()
        mock_config_accessor.current.return_value = mock_config

        mock_rcc_packer = Mock()
        mock_rcc_packer_class.return_value = mock_rcc_packer

        mock_uv_packer = Mock()
        mock_uv_packer.start.side_effect = RuntimeError("UV packing failed")
        mock_uv_packer_class.return_value = mock_uv_packer

        mock_rcc_watcher = Mock()
        mock_rcc_watcher_class.return_value = mock_rcc_watcher

        mock_uv_watcher = Mock()
        mock_uv_watcher_class.return_value = mock_uv_watcher

        mock_executor = Mock()
        mock_executor_class.return_value = mock_executor

        mock_external_task_client = Mock()

        # Execute - should not raise
        start_watch_robots(mock_external_task_client)

        # Verify RCC packer still ran despite UV error
        mock_rcc_packer.start.assert_called_once()

        # Verify watchers were still initialized
        mock_rcc_watcher_class.assert_called_once()