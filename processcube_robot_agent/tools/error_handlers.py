"""Error handling utilities for ProcessCube robots.

Provides standard FunctionalError raising functions to signal different
types of failures to ProcessCube, enabling proper error routing and workflow
continuation logic.

Usage:
    from processcube_robot_agent.tools import raise_robot_test_failed
    
    result = executor.execute("tests/example.robot")
    if result["status"] == "fail":
        raise_robot_test_failed("example.robot", result["return_code"])
"""

import logging
from processcube_sdk.external_tasks import FunctionalError

logger = logging.getLogger(__name__)


def raise_robot_test_failed(robot_file: str, return_code: int, details: str = "") -> None:
    """Raise FunctionalError when Robot Framework tests fail.
    
    This signals to ProcessCube that the failure is a business logic failure
    (tests didn't pass) rather than a technical failure (wrapper crashed).
    
    Args:
        robot_file: Path to the robot file that had failing tests
        return_code: Return code from Robot Framework execution
        details: Optional additional details about the failure
        
    Raises:
        FunctionalError: Always raises with code "ROBOT_TESTS_FAILED"
    """
    error_msg = (
        f"Robot Framework tests failed (return code: {return_code})\n"
        f"Failed tests detected in: {robot_file}"
    )
    if details:
        error_msg += f"\n{details}"
    
    logger.error(error_msg)
    raise FunctionalError("ROBOT_TESTS_FAILED", error_msg)


def raise_robot_execution_error(error: str, robot_file: str = "") -> None:
    """Raise FunctionalError when Robot Framework execution encounters errors.
    
    This signals to ProcessCube that the failure is a technical error
    (wrapper or execution problem) that should be handled as a functional error
    to enable proper error handling workflows.
    
    Args:
        error: Error message/details
        robot_file: Optional path to the robot file being executed
        
    Raises:
        FunctionalError: Always raises with code "ROBOT_EXECUTION_ERROR"
    """
    error_msg = f"Robot Framework execution error: {error}"
    if robot_file:
        error_msg = f"Robot Framework execution error in {robot_file}: {error}"
    
    logger.error(error_msg)
    raise FunctionalError("ROBOT_EXECUTION_ERROR", error_msg)


def raise_functional_error(code: str, message: str) -> None:
    """Raise a generic FunctionalError with custom code and message.
    
    Allows robots to raise custom FunctionalErrors for domain-specific errors.
    
    Args:
        code: Error code (e.g., "INVALID_INPUT", "API_FAILED")
        message: Error message
        
    Raises:
        FunctionalError: Always raises with provided code and message
    """
    logger.error(f"[{code}] {message}")
    raise FunctionalError(code, message)
