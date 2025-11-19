"""Robot Framework Executor - Reusable tool for executing *.robot files.

This module provides a clean API for executing Robot Framework files from Python,
with support for variables, tags, and comprehensive result extraction.

Usage:
    from processcube_robot_agent.tools import RobotFrameworkExecutor
    
    executor = RobotFrameworkExecutor()
    result = executor.execute(
        robot_file="tests/example.robot",
        variables={"username": "test", "password": "secret"},
        tags=["smoke"],
        suite_name="My Test Suite"
    )
    
    if result["status"] == "pass":
        print("All tests passed!")
    else:
        print(f"Tests failed: {result['error']}")
"""

import json
import logging
import subprocess
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def write_variables_file(variables: Dict[str, Any], tmpdir: str) -> str:
    """Write variables as Python file for Robot Framework.
    
    Robot Framework can read variables from Python files using --variablefile.
    This creates a valid Python file with variable definitions.
    
    Args:
        variables: Dictionary of variables to pass to Robot Framework
        tmpdir: Temporary directory to write the file to
        
    Returns:
        Path to the generated variables file
    """
    var_file = Path(tmpdir) / "variables.py"
    
    # Convert Python dict to Robot Framework variable definitions
    var_content = []
    for key, value in variables.items():
        # Ensure valid Python variable names
        if not key.isidentifier():
            logger.warning(f"Variable name '{key}' is not a valid identifier, skipping")
            continue
        
        # Handle different value types
        if isinstance(value, str):
            # Escape quotes in strings
            escaped_value = value.replace("'", "\\'")
            var_content.append(f"{key} = '{escaped_value}'")
        elif isinstance(value, bool):
            var_content.append(f"{key} = {str(value)}")
        elif isinstance(value, (int, float)):
            var_content.append(f"{key} = {value}")
        elif isinstance(value, (list, dict)):
            # For complex types, use JSON representation
            json_value = json.dumps(value)
            var_content.append(f"{key} = {json_value}")
        else:
            var_content.append(f"{key} = '{str(value)}'")
    
    var_file.write_text("\n".join(var_content))
    logger.debug(f"Created variables file at {var_file}")
    return str(var_file)


def extract_reports(output_dir: Path, result: subprocess.CompletedProcess, duration: float) -> Dict[str, Any]:
    """Extract Robot Framework reports from output directory (minimal format).

    Returns a compressed result dictionary to minimize logging output:
    - Excludes verbose stdout/stderr (stored in DEBUG logs instead)
    - Excludes full XML content (path to log.html provided for details)
    - Includes only: status, return_code, duration, tests_passed, log_html

    Robot Framework generates:
    - output.xml: Machine-readable test results (parsed for statistics only)
    - log.html: Detailed test execution logs (path provided for access)
    - report.html: High-level test report

    Args:
        output_dir: Directory where Robot Framework wrote its output
        result: CompletedProcess from robot execution
        duration: Execution duration in seconds

    Returns:
        Minimal result dictionary for ProcessCube integration:
        {
            'status': 'pass|fail',
            'return_code': <int>,
            'duration': <float>,
            'tests_passed': <int>,
            'log_html': <path>
        }
    """
    # Initialize minimal result (Option A format)
    reports = {
        "status": "pass" if result.returncode == 0 else "fail",
        "return_code": result.returncode,
        "duration": duration,
        "tests_passed": 0,
        "log_html": None,
    }

    # Log stdout/stderr at DEBUG level instead of including in result
    if result.stdout:
        logger.debug(f"Robot Framework STDOUT:\n{result.stdout}")
    if result.stderr:
        logger.debug(f"Robot Framework STDERR:\n{result.stderr}")

    # Extract output.xml (machine-readable test results)
    output_xml_path = output_dir / "output.xml"
    if output_xml_path.exists():
        try:
            # Try to parse for test statistics
            tree = ET.parse(output_xml_path)
            root = tree.getroot()

            # Extract test statistics if available
            stats = root.find(".//stat")
            if stats is not None:
                passed = stats.get("passed")
                if passed:
                    reports["tests_passed"] = int(passed)
                logger.debug(f"Robot test statistics - total: {stats.get('total')}, "
                           f"passed: {stats.get('passed')}, failed: {stats.get('failed')}")
        except Exception as e:
            logger.error(f"Failed to parse output.xml: {e}")
    else:
        logger.warning("No output.xml found in Robot Framework output")

    # Include log.html path for detailed logs
    log_html_path = output_dir / "log.html"
    if log_html_path.exists():
        reports["log_html"] = str(log_html_path)

    return reports


class RobotFrameworkExecutor:
    """Executes Robot Framework files and returns structured results.
    
    This class handles:
    - Variable passing to Robot Framework
    - Output directory management (temporary directories)
    - Report extraction
    - Error handling
    
    Example:
        executor = RobotFrameworkExecutor()
        result = executor.execute("tests/example.robot")
        
        if result["status"] == "pass":
            print("Success!")
        else:
            print(f"Failed: {result['error']}")
    """
    
    def execute(
        self,
        robot_file: str,
        variables: Optional[Dict[str, Any]] = None,
        tags: Optional[list] = None,
        suite_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute a Robot Framework file.
        
        This is the main method that runs Robot Framework with proper:
        - Variable passing (via --variablefile)
        - Output directory management (temporary directory)
        - Report extraction
        - Error handling
        
        Args:
            robot_file: Path to the *.robot file to execute
            variables: Dictionary of variables to pass to Robot Framework
            tags: List of tags to include in execution (--include)
            suite_name: Name for the test suite (--name)
            
        Returns:
            Dictionary with execution results and reports (minimal format):
                {
                    "status": "pass|fail|error",
                    "return_code": <int>,
                    "duration": <float>,             # Execution time in seconds
                    "tests_passed": <int>,           # Number of passing tests
                    "log_html": <path>,              # Path to detailed HTML logs
                }
        """
        if variables is None:
            variables = {}

        logger.info(f"Running Robot Framework file: {robot_file}")
        logger.info(f"Variables: {variables}")

        # Verify robot file exists
        robot_path = Path(robot_file)
        if not robot_path.exists():
            return {
                "status": "error",
                "error": f"Robot file not found: {robot_file}",
                "return_code": -1,
            }

        # Create temporary directory for output
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            output_dir.mkdir(parents=True, exist_ok=True)

            # Build robot command
            cmd = [
                "robot",
                "--outputdir", str(output_dir),
            ]

            # Add variables if provided
            if variables:
                var_file = write_variables_file(variables, tmpdir)
                cmd.extend(["--variablefile", var_file])

            # Add optional parameters
            if tags:
                for tag in tags:
                    cmd.extend(["--include", tag])

            if suite_name:
                cmd.extend(["--name", suite_name])

            # Add robot file as last argument
            cmd.append(str(robot_path))

            logger.info(f"Executing: {' '.join(cmd)}")

            # Execute robot framework
            try:
                # Track execution time
                start_time = time.time()
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=3600  # 1 hour timeout
                )
                duration = time.time() - start_time

                logger.info(f"Robot execution completed with return code: {result.returncode} (duration: {duration:.3f}s)")
                if result.stdout:
                    logger.debug(f"STDOUT:\n{result.stdout}")
                if result.stderr:
                    logger.debug(f"STDERR:\n{result.stderr}")

                # Extract and return reports with duration
                reports = extract_reports(output_dir, result, duration)
                return reports
                
            except subprocess.TimeoutExpired:
                return {
                    "status": "error",
                    "error": "Robot Framework execution timed out (1 hour limit)",
                    "return_code": -1,
                }
            except Exception as e:
                logger.error(f"Error executing Robot Framework: {e}", exc_info=True)
                return {
                    "status": "error",
                    "error": str(e),
                    "return_code": -1,
                }
