"""Robot Framework Runner - Standalone entry point for executing Robot Framework files.

This module provides a simple command-line interface for executing Robot Framework
files without needing a separate main.py wrapper. It can be used as a [project.scripts]
entry point in pyproject.toml.

Usage:
    # Define in pyproject.toml:
    [project.scripts]
    robot_runner = "processcube_robot_agent.tools.robot_runner:main"

    # Then execute:
    python -m processcube_robot_agent.tools.robot_runner my_robot.robot
    # Or via entry point:
    robot_runner my_robot.robot
    # Or with variables:
    robot_runner my_robot.robot --variable USER=admin --variable PASSWORD=secret
    # Or with tags:
    robot_runner my_robot.robot --tag smoke --tag critical

    # Read robot_file from pyproject.toml [tool.processcube] section:
    robot_runner  # Uses robot_file from config

Example pyproject.toml:
    [project]
    name = "my-robot"
    version = "0.1.0"
    requires-python = ">=3.11"
    dependencies = ["robocorp-workitems>=1.0.0"]

    [project.scripts]
    robot_runner = "processcube_robot_agent.tools.robot_runner:main"

    [tool.processcube]
    robot_file = "my_robot.robot"  # Default if not specified on CLI
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional

from .robot_executor import RobotFrameworkExecutor
from .work_items import process_work_items
from .error_handlers import raise_robot_test_failed, raise_robot_execution_error

logger = logging.getLogger(__name__)


def load_config_robot_file() -> Optional[str]:
    """Load robot_file from pyproject.toml [tool.processcube] section.

    Returns:
        Robot file path if configured, None otherwise
    """
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib  # type: ignore
        except ImportError:
            logger.debug("Could not load tomllib/tomli - skipping config file parsing")
            return None

    pyproject_path = Path.cwd() / "pyproject.toml"
    if not pyproject_path.exists():
        return None

    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
            return data.get("tool", {}).get("processcube", {}).get("robot_file")
    except Exception as e:
        logger.debug(f"Failed to load config from pyproject.toml: {e}")
        return None


def parse_arguments(args: Optional[List[str]] = None) -> tuple:
    """Parse command-line arguments for robot_runner.

    Args:
        args: Command-line arguments (sys.argv[1:] if None)

    Returns:
        Tuple of (robot_file, variables_dict, tags_list)
    """
    if args is None:
        args = sys.argv[1:]

    robot_file = None
    variables = {}
    tags = []
    i = 0

    # First positional argument is robot_file
    while i < len(args):
        if args[i].startswith("-"):
            break
        robot_file = args[i]
        i += 1

    # Parse options
    while i < len(args):
        if args[i] == "--variable" and i + 1 < len(args):
            # Parse --variable KEY=VALUE
            key_value = args[i + 1]
            if "=" in key_value:
                key, value = key_value.split("=", 1)
                variables[key] = value
            i += 2
        elif args[i] == "--tag" and i + 1 < len(args):
            # Parse --tag TAG
            tags.append(args[i + 1])
            i += 2
        elif args[i] == "--help" or args[i] == "-h":
            print_help()
            sys.exit(0)
        else:
            logger.warning(f"Unknown argument: {args[i]}")
            i += 1

    return robot_file, variables, tags


def print_help() -> None:
    """Print help message."""
    help_text = """
Robot Framework Runner - Execute Robot Framework files with ProcessCube integration.

Usage:
    robot_runner [ROBOT_FILE] [OPTIONS]

Arguments:
    ROBOT_FILE                  Path to .robot file to execute
                                If not provided, reads from pyproject.toml [tool.processcube] robot_file

Options:
    --variable KEY=VALUE        Pass variable to Robot Framework (can be repeated)
    --tag TAG                   Include tag in execution (can be repeated)
    --help, -h                  Show this help message

Examples:
    # Execute robot file
    robot_runner my_robot.robot

    # With variables
    robot_runner my_robot.robot --variable USER=admin --variable PASSWORD=secret

    # With tags
    robot_runner my_robot.robot --tag smoke --tag critical

    # From config (reads from pyproject.toml)
    robot_runner

Configuration:
    Add to pyproject.toml to set default robot file:

    [tool.processcube]
    robot_file = "my_robot.robot"

ProcessCube Integration:
    This tool integrates with ProcessCube via work items:
    - Reads input work items from RPA_WORKITEMS_PATH
    - Writes output work items to RPA_OUTPUT_WORKITEM_PATH
    - Raises FunctionalError on test failures for proper error handling

Requires:
    - robocorp-workitems >= 1.0.0
    - Robot Framework installed
"""
    print(help_text)


def main(args: Optional[List[str]] = None) -> None:
    """Main entry point for robot_runner.

    Args:
        args: Command-line arguments (sys.argv[1:] if None)
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger.info("Starting Robot Framework Runner")

    # Parse arguments
    robot_file, variables, tags = parse_arguments(args)

    # If no robot file from CLI, try config
    if not robot_file:
        robot_file = load_config_robot_file()

    # If still no robot file, error
    if not robot_file:
        logger.error("No robot file specified. Use: robot_runner <robot_file> or set robot_file in pyproject.toml")
        print_help()
        sys.exit(1)

    logger.info(f"Robot file: {robot_file}")
    if variables:
        logger.info(f"Variables: {variables}")
    if tags:
        logger.info(f"Tags: {tags}")

    # Initialize executor
    executor = RobotFrameworkExecutor()

    # Define processor that executes the robot file
    def process_robot_task(payload: Dict) -> Dict:
        """Execute the configured robot file.

        Args:
            payload: Input work item payload (may contain overrides)

        Returns:
            Execution results dictionary
        """
        # Allow payload to override robot_file
        file_to_execute = payload.get("robot_file", robot_file)
        payload_vars = payload.get("variables", {})
        payload_tags = payload.get("tags", tags)

        # Merge variables (payload overrides CLI)
        merged_vars = {**variables, **payload_vars}

        logger.info(f"Executing: {file_to_execute}")

        # Execute robot file
        result = executor.execute(
            robot_file=file_to_execute,
            variables=merged_vars,
            tags=payload_tags if payload_tags else None
        )

        logger.info(f"Execution status: {result['status']}")

        # Signal failures to ProcessCube
        if result["status"] == "fail":
            raise_robot_test_failed(file_to_execute, result["return_code"])
        elif result["status"] == "error":
            raise_robot_execution_error(result.get("error", "Unknown error"), file_to_execute)

        return result

    # Process work items
    process_work_items(process_robot_task)
    logger.info("Robot Framework Runner completed successfully")


if __name__ == "__main__":
    main()
