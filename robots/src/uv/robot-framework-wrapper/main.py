"""UV-based wrapper for executing Robot Framework files.

This wrapper allows *.robot files to be executed via UV with full ProcessCube
integration. It demonstrates how to use the RobotFrameworkExecutor tool.

Usage:
    Accepts input work items:
    {
        "robot_file": "path/to/file.robot",  # Path to *.robot file to execute
        "variables": {...},                   # Optional dict of variables
        "tags": [...],                        # Optional list of tags to include
        "suite_name": "..."                   # Optional test suite name
    }
    
    Without robot_file, uses example.robot for demonstration.
    
    Creates output work items with execution results:
    {
        "status": "pass|fail|error",
        "return_code": <int>,
        "output_xml": <xml_string>,          # If available
        "log_html_path": <path>,             # If available
        "report_html_path": <path>,          # If available
        "statistics": {...},                 # If parsed from output.xml
        "stdout": <output>,                  # Robot Framework console output
        "stderr": <errors>,                  # Any error messages
    }
"""

import logging

from processcube_robot_agent.tools import (
    RobotFrameworkExecutor,
    process_work_items,
    raise_robot_test_failed,
    raise_robot_execution_error,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize executor once
executor = RobotFrameworkExecutor()


def process_robot_task(payload):
    """Process a robot execution task.
    
    Extracts robot file path and execution parameters from the payload,
    executes the robot file, and raises FunctionalError if tests fail.
    
    Args:
        payload: Input work item payload
        
    Returns:
        Dictionary with execution results
        
    Raises:
        FunctionalError: When tests fail or execution encounters errors
    """
    # Extract robot file path (optional - defaults to example.robot)
    robot_file = payload.get("robot_file")
    
    # If no robot file specified, use example.robot for demonstration
    if not robot_file:
        logger.warning("No 'robot_file' specified in payload, using example.robot for demonstration")
        robot_file = "example.robot"
    
    # Extract optional parameters
    variables = payload.get("variables", {})
    tags = payload.get("tags")
    suite_name = payload.get("suite_name")
    
    # Log execution details
    logger.info(f"Executing robot file: {robot_file}")
    if variables:
        logger.info(f"With variables: {variables}")
    if tags:
        logger.info(f"With tags: {tags}")
    if suite_name:
        logger.info(f"With suite name: {suite_name}")
    
    # Execute robot file using the executor tool
    result = executor.execute(
        robot_file=robot_file,
        variables=variables,
        tags=tags,
        suite_name=suite_name,
    )
    
    logger.info(f"Robot execution completed with status: {result['status']}")
    
    # Signal failures to ProcessCube via FunctionalError
    if result["status"] == "fail":
        raise_robot_test_failed(robot_file, result["return_code"])
    elif result["status"] == "error":
        raise_robot_execution_error(result.get("error", "Unknown error"), robot_file)
    
    return result


if __name__ == "__main__":
    logger.info("Starting Robot Framework wrapper")
    process_work_items(process_robot_task)
    logger.info("Robot Framework wrapper completed successfully")
