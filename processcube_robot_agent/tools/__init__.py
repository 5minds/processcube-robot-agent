"""ProcessCube Robot Agent Tools - Reusable utilities for building robots.

This package provides reusable tools for building ProcessCube robots:
- RobotFrameworkExecutor: Execute *.robot files from Python
- process_work_items: Standard work item processing framework
- Error handlers: FunctionalError utilities for proper error signaling

Example:
    from processcube_robot_agent.tools import (
        RobotFrameworkExecutor,
        process_work_items,
        raise_robot_test_failed,
        raise_robot_execution_error,
    )
    
    executor = RobotFrameworkExecutor()
    
    def process_task(payload):
        robot_file = payload.get("robot_file", "example.robot")
        result = executor.execute(robot_file)
        
        if result["status"] == "fail":
            raise_robot_test_failed(robot_file, result["return_code"])
        
        return result
    
    if __name__ == "__main__":
        process_work_items(process_task)
"""

from .robot_executor import RobotFrameworkExecutor
from .work_items import process_work_items
from .error_handlers import (
    raise_robot_test_failed,
    raise_robot_execution_error,
    raise_functional_error,
)

__all__ = [
    "RobotFrameworkExecutor",
    "process_work_items",
    "raise_robot_test_failed",
    "raise_robot_execution_error",
    "raise_functional_error",
]
