from typing import Any, Dict


class BaseAgent:
    """Abstract base class for robot agents."""

    def execute(self, payload: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a robot task with the given payload.

        Args:
            payload: Input data for the robot.
            task: Task metadata.

        Returns:
            Result dictionary from robot execution.

        Raises:
            NotImplementedError: This is an abstract method.
        """
        raise NotImplementedError("Subclasses must implement the execute method")