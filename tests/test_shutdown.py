"""Tests for graceful shutdown handling."""

import asyncio
import signal
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock

from processcube_robot_agent.shutdown import (
    GracefulShutdownManager,
    ConnectionTracker,
    get_shutdown_manager,
    setup_signal_handlers,
    shutdown_handler,
)


class TestGracefulShutdownManager:
    """Test GracefulShutdownManager class."""

    def test_initialization(self):
        """Test manager initialization."""
        manager = GracefulShutdownManager(timeout_seconds=45)
        assert manager.timeout_seconds == 45
        assert manager.is_shutting_down is False
        assert manager.active_connections == 0
        assert len(manager.cleanup_tasks) == 0

    def test_register_cleanup_task(self):
        """Test registering cleanup tasks."""
        manager = GracefulShutdownManager()
        task1 = Mock()
        task2 = Mock()

        manager.register_cleanup_task(task1)
        manager.register_cleanup_task(task2)

        assert task1 in manager.cleanup_tasks
        assert task2 in manager.cleanup_tasks
        assert len(manager.cleanup_tasks) == 2

    def test_unregister_cleanup_task(self):
        """Test unregistering cleanup tasks."""
        manager = GracefulShutdownManager()
        task = Mock()

        manager.register_cleanup_task(task)
        assert task in manager.cleanup_tasks

        manager.unregister_cleanup_task(task)
        assert task not in manager.cleanup_tasks

    def test_increment_active_connections(self):
        """Test incrementing connection counter."""
        manager = GracefulShutdownManager()
        assert manager.active_connections == 0

        manager.increment_active_connections()
        assert manager.active_connections == 1

        manager.increment_active_connections()
        assert manager.active_connections == 2

    def test_decrement_active_connections(self):
        """Test decrementing connection counter."""
        manager = GracefulShutdownManager()
        manager.active_connections = 3

        manager.decrement_active_connections()
        assert manager.active_connections == 2

        manager.decrement_active_connections()
        manager.decrement_active_connections()
        assert manager.active_connections == 0

    def test_decrement_active_connections_below_zero(self):
        """Test that connections don't go below zero."""
        manager = GracefulShutdownManager()
        manager.active_connections = 0

        manager.decrement_active_connections()
        assert manager.active_connections == 0

    @pytest.mark.asyncio
    async def test_shutdown_sets_flag(self):
        """Test that shutdown sets the shutting_down flag."""
        manager = GracefulShutdownManager()
        assert manager.is_shutting_down is False

        await manager.shutdown(signal.SIGTERM)
        assert manager.is_shutting_down is True

    @pytest.mark.asyncio
    async def test_shutdown_already_in_progress(self):
        """Test that duplicate shutdown is ignored."""
        manager = GracefulShutdownManager()
        manager.is_shutting_down = True

        # Should return immediately without processing
        await manager.shutdown(signal.SIGTERM)
        assert manager.is_shutting_down is True

    @pytest.mark.asyncio
    async def test_shutdown_sets_shutdown_complete(self):
        """Test that shutdown_complete event is set."""
        manager = GracefulShutdownManager()

        # Shutdown should complete
        await manager.shutdown(signal.SIGTERM)
        assert manager.shutdown_complete.is_set()

    @pytest.mark.asyncio
    async def test_shutdown_with_cleanup_tasks(self):
        """Test shutdown executes cleanup tasks."""
        manager = GracefulShutdownManager()
        task1 = AsyncMock()
        task2 = AsyncMock()

        manager.register_cleanup_task(task1)
        manager.register_cleanup_task(task2)

        await manager.shutdown(signal.SIGTERM)

        task1.assert_called_once()
        task2.assert_called_once()

    @pytest.mark.asyncio
    async def test_shutdown_with_sync_cleanup_task(self):
        """Test shutdown handles sync cleanup tasks."""
        manager = GracefulShutdownManager()
        task = Mock()

        manager.register_cleanup_task(task)

        await manager.shutdown(signal.SIGTERM)

        task.assert_called_once()

    @pytest.mark.asyncio
    async def test_shutdown_with_cleanup_task_error(self):
        """Test shutdown continues if cleanup task fails."""
        manager = GracefulShutdownManager()
        task1 = AsyncMock(side_effect=Exception("Task failed"))
        task2 = AsyncMock()

        manager.register_cleanup_task(task1)
        manager.register_cleanup_task(task2)

        await manager.shutdown(signal.SIGTERM)

        task1.assert_called_once()
        task2.assert_called_once()

    @pytest.mark.asyncio
    async def test_wait_for_shutdown(self):
        """Test waiting for shutdown completion."""
        manager = GracefulShutdownManager()

        # Start shutdown in a task
        asyncio.create_task(manager.shutdown(signal.SIGTERM))

        # Wait for it to complete
        await asyncio.wait_for(manager.wait_for_shutdown(), timeout=5)

        assert manager.shutdown_complete.is_set()

    @pytest.mark.asyncio
    async def test_wait_for_connections_no_active(self):
        """Test waiting for connections when none are active."""
        manager = GracefulShutdownManager()
        manager.active_connections = 0

        # Should complete immediately
        await manager._wait_for_connections()

    @pytest.mark.asyncio
    async def test_wait_for_connections_with_timeout(self):
        """Test waiting for connections timeout."""
        manager = GracefulShutdownManager(timeout_seconds=0.1)
        manager.active_connections = 5

        # Should timeout and log warning
        await manager._wait_for_connections()

        # Connections should still be there (not modified)
        assert manager.active_connections == 5

    @pytest.mark.asyncio
    async def test_execute_cleanup_tasks_empty(self):
        """Test cleanup with no tasks."""
        manager = GracefulShutdownManager()

        # Should return immediately
        await manager._execute_cleanup_tasks()


class TestConnectionTracker:
    """Test ConnectionTracker context manager."""

    def test_sync_context_manager(self):
        """Test synchronous context manager."""
        manager = GracefulShutdownManager()
        assert manager.active_connections == 0

        with ConnectionTracker(manager):
            assert manager.active_connections == 1

        assert manager.active_connections == 0

    def test_sync_context_manager_nested(self):
        """Test nested context managers."""
        manager = GracefulShutdownManager()

        with ConnectionTracker(manager):
            assert manager.active_connections == 1
            with ConnectionTracker(manager):
                assert manager.active_connections == 2
            assert manager.active_connections == 1

    def test_sync_context_manager_exception(self):
        """Test context manager decrements even on exception."""
        manager = GracefulShutdownManager()

        try:
            with ConnectionTracker(manager):
                assert manager.active_connections == 1
                raise ValueError("Test error")
        except ValueError:
            pass

        assert manager.active_connections == 0

    def test_connection_tracker_default_manager(self):
        """Test ConnectionTracker uses default manager if none provided."""
        # Get initial state
        initial_manager = get_shutdown_manager()
        initial_connections = initial_manager.active_connections

        tracker = ConnectionTracker()
        assert tracker.manager is initial_manager

        with tracker:
            assert initial_manager.active_connections == initial_connections + 1

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test asynchronous context manager."""
        manager = GracefulShutdownManager()
        assert manager.active_connections == 0

        async with ConnectionTracker(manager):
            assert manager.active_connections == 1

        assert manager.active_connections == 0

    @pytest.mark.asyncio
    async def test_async_context_manager_exception(self):
        """Test async context manager decrements even on exception."""
        manager = GracefulShutdownManager()

        try:
            async with ConnectionTracker(manager):
                assert manager.active_connections == 1
                raise ValueError("Test error")
        except ValueError:
            pass

        assert manager.active_connections == 0


class TestGetShutdownManager:
    """Test get_shutdown_manager function."""

    def test_returns_same_instance(self):
        """Test that get_shutdown_manager returns the same instance."""
        manager1 = get_shutdown_manager()
        manager2 = get_shutdown_manager()

        assert manager1 is manager2

    @pytest.fixture(autouse=True)
    def reset_manager(self):
        """Reset the global manager for each test."""
        import processcube_robot_agent.shutdown as shutdown_module
        shutdown_module._shutdown_manager = None
        yield
        shutdown_module._shutdown_manager = None


class TestSetupSignalHandlers:
    """Test signal handler setup."""

    @pytest.fixture(autouse=True)
    def reset_manager_and_handlers(self):
        """Reset manager and clear signal handlers."""
        import processcube_robot_agent.shutdown as shutdown_module
        shutdown_module._shutdown_manager = None
        yield
        shutdown_module._shutdown_manager = None

    def test_setup_registers_handlers(self):
        """Test that signal handlers are registered."""
        # We can't easily test actual signal handling without forking,
        # but we can verify that setup_signal_handlers doesn't raise
        setup_signal_handlers()

        # Verify manager was created
        manager = get_shutdown_manager()
        assert manager is not None

    @patch("signal.signal")
    def test_setup_registers_sigterm(self, mock_signal):
        """Test that SIGTERM handler is registered."""
        setup_signal_handlers()

        # Check that signal.signal was called with SIGTERM
        calls = mock_signal.call_args_list
        assert any(call[0][0] == signal.SIGTERM for call in calls)

    @patch("signal.signal")
    def test_setup_registers_sigint(self, mock_signal):
        """Test that SIGINT handler is registered."""
        setup_signal_handlers()

        # Check that signal.signal was called with SIGINT
        calls = mock_signal.call_args_list
        assert any(call[0][0] == signal.SIGINT for call in calls)


class TestShutdownHandler:
    """Test shutdown_handler context manager."""

    @pytest.fixture(autouse=True)
    def reset_manager(self):
        """Reset the global manager for each test."""
        import processcube_robot_agent.shutdown as shutdown_module
        shutdown_module._shutdown_manager = None
        yield
        shutdown_module._shutdown_manager = None

    def test_shutdown_handler_is_context_manager(self):
        """Test that shutdown_handler is an async context manager."""
        # Verify it's callable and returns a context manager
        result = shutdown_handler()
        assert hasattr(result, '__aenter__')
        assert hasattr(result, '__aexit__')
