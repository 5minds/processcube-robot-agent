"""Graceful shutdown handler for clean service termination.

Handles SIGTERM/SIGINT signals and cleanly shuts down:
- Active connections
- In-flight tasks
- Resource cleanup
- Logging and metrics finalization
"""

import asyncio
import logging
import signal
import sys
from typing import Callable, Optional, Set
from contextlib import asynccontextmanager

logger = logging.getLogger("processcube_robot_agent")


class GracefulShutdownManager:
    """Manages graceful shutdown of the application."""
    
    def __init__(self, timeout_seconds: int = 30):
        """Initialize shutdown manager.
        
        Args:
            timeout_seconds: Maximum time to wait for graceful shutdown
        """
        self.timeout_seconds = timeout_seconds
        self.is_shutting_down = False
        self.shutdown_complete = asyncio.Event()
        self.cleanup_tasks: Set[Callable] = set()
        self.active_connections = 0
    
    def register_cleanup_task(self, task: Callable) -> None:
        """Register a cleanup task to be executed on shutdown.
        
        Args:
            task: Async callable to execute during shutdown
        """
        self.cleanup_tasks.add(task)
    
    def unregister_cleanup_task(self, task: Callable) -> None:
        """Unregister a cleanup task.
        
        Args:
            task: Async callable to unregister
        """
        self.cleanup_tasks.discard(task)
    
    def increment_active_connections(self) -> None:
        """Increment active connection counter."""
        self.active_connections += 1
    
    def decrement_active_connections(self) -> None:
        """Decrement active connection counter."""
        self.active_connections = max(0, self.active_connections - 1)
    
    async def shutdown(self, signum: Optional[int] = None) -> None:
        """Execute graceful shutdown sequence.
        
        Args:
            signum: Signal number (SIGTERM=15, SIGINT=2)
        """
        if self.is_shutting_down:
            logger.warning("Shutdown already in progress")
            return
        
        self.is_shutting_down = True
        signal_name = signal.Signals(signum).name if signum else "UNKNOWN"
        logger.info(f"Received signal {signal_name}, initiating graceful shutdown")
        
        try:
            # Wait for active connections to complete (with timeout)
            await self._wait_for_connections()
            
            # Execute cleanup tasks
            await self._execute_cleanup_tasks()
            
            # Final logging
            logger.info("Graceful shutdown completed successfully")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}", exc_info=True)
        finally:
            self.shutdown_complete.set()
    
    async def _wait_for_connections(self) -> None:
        """Wait for active connections to complete.
        
        Waits up to timeout_seconds for all active connections to finish.
        """
        start_time = asyncio.get_event_loop().time()
        check_interval = 0.5  # Check every 500ms
        
        while self.active_connections > 0:
            elapsed = asyncio.get_event_loop().time() - start_time
            
            if elapsed > self.timeout_seconds:
                logger.warning(
                    f"Shutdown timeout: {self.active_connections} connections "
                    f"still active after {self.timeout_seconds}s"
                )
                break
            
            remaining = self.timeout_seconds - elapsed
            logger.info(
                f"Waiting for {self.active_connections} active connections "
                f"({remaining:.1f}s remaining)"
            )
            
            await asyncio.sleep(check_interval)
    
    async def _execute_cleanup_tasks(self) -> None:
        """Execute all registered cleanup tasks."""
        if not self.cleanup_tasks:
            return
        
        logger.info(f"Executing {len(self.cleanup_tasks)} cleanup tasks")
        
        for task in self.cleanup_tasks:
            try:
                if asyncio.iscoroutinefunction(task):
                    await task()
                else:
                    task()
                logger.debug(f"Cleanup task {task.__name__} completed")
            except Exception as e:
                logger.error(
                    f"Error in cleanup task {task.__name__}: {e}",
                    exc_info=True
                )
    
    async def wait_for_shutdown(self) -> None:
        """Wait for shutdown to complete."""
        await self.shutdown_complete.wait()


# Global shutdown manager instance
_shutdown_manager: Optional[GracefulShutdownManager] = None


def get_shutdown_manager() -> GracefulShutdownManager:
    """Get or create the global shutdown manager."""
    global _shutdown_manager
    if _shutdown_manager is None:
        _shutdown_manager = GracefulShutdownManager()
    return _shutdown_manager


def setup_signal_handlers() -> None:
    """Set up signal handlers for graceful shutdown.
    
    Handles SIGTERM (15) and SIGINT (2) signals.
    """
    manager = get_shutdown_manager()
    
    def signal_handler(signum: int, frame) -> None:
        """Handle shutdown signal."""
        # Schedule shutdown in event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(manager.shutdown(signum))
        else:
            asyncio.run(manager.shutdown(signum))
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    logger.info("Signal handlers registered for graceful shutdown")


@asynccontextmanager
async def shutdown_handler():
    """Context manager for graceful shutdown handling.
    
    Usage:
        async with shutdown_handler():
            await app.run()
    """
    manager = get_shutdown_manager()
    setup_signal_handlers()
    
    try:
        yield
    finally:
        # Ensure shutdown completes
        try:
            await asyncio.wait_for(
                manager.wait_for_shutdown(),
                timeout=manager.timeout_seconds + 5
            )
        except asyncio.TimeoutError:
            logger.error("Shutdown timeout exceeded, forcing exit")
            sys.exit(1)


class ConnectionTracker:
    """Context manager for tracking active connections."""
    
    def __init__(self, manager: Optional[GracefulShutdownManager] = None):
        """Initialize connection tracker.
        
        Args:
            manager: GracefulShutdownManager instance
        """
        self.manager = manager or get_shutdown_manager()
    
    def __enter__(self):
        """Enter context - increment active connections."""
        self.manager.increment_active_connections()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context - decrement active connections."""
        self.manager.decrement_active_connections()
        return False
    
    async def __aenter__(self):
        """Async enter - increment active connections."""
        self.manager.increment_active_connections()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async exit - decrement active connections."""
        self.manager.decrement_active_connections()
        return False
