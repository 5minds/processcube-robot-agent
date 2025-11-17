"""Helper utilities for integration testing."""

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional


def create_temp_config(
    engine_url: str = "http://localhost:56100",
    api_port: int = 42042,
    topic_prefix: str = "test"
) -> str:
    """Create a temporary configuration file for testing.
    
    Args:
        engine_url: ProcessCube engine URL
        api_port: REST API port
        topic_prefix: Topic prefix for robots
        
    Returns:
        Path to the created config file
    """
    config = {
        "debugging": {
            "enabled": False,
            "hostname": "localhost",
            "port": 5678,
            "wait_for_client": False
        },
        "engine": {
            "url": engine_url
        },
        "rcc": {
            "topic_prefix": topic_prefix,
            "wrap_dir": "robots/installed/rcc",
            "unwrap_dir": "temp/robots/rcc/unwrapped",
            "start_watch_project_dir": False,
            "project_dir": "robots/src/rcc"
        },
        "rest_api": {
            "port": api_port,
            "host": "0.0.0.0"
        }
    }
    
    # Create temp file
    fd, path = tempfile.mkstemp(suffix=".json", prefix="test_config_")
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(config, f, indent=2)
    except:
        os.close(fd)
        raise
    
    return path


def cleanup_config(config_path: str) -> None:
    """Clean up temporary configuration file.
    
    Args:
        config_path: Path to config file to delete
    """
    try:
        if os.path.exists(config_path):
            os.remove(config_path)
    except Exception as e:
        print(f"Failed to clean up config file: {e}")


def create_test_robot(
    name: str,
    project_dir: str = "robots/src/rcc",
    task_name: str = "TestTask"
) -> Path:
    """Create a minimal test robot.
    
    Args:
        name: Robot name/directory
        project_dir: Base directory for robots
        task_name: Task name
        
    Returns:
        Path to the created robot directory
    """
    robot_path = Path(project_dir) / name
    robot_path.mkdir(parents=True, exist_ok=True)
    
    # Create robot.yaml
    robot_yaml = f"""tasks:
  {task_name}:
    robotTaskName: {task_name}

condaConfigFile: conda.yaml
artifactsDir: output
PATH: [.]
PYTHONPATH: [.]
"""
    (robot_path / "robot.yaml").write_text(robot_yaml)
    
    # Create tasks.robot
    tasks_robot = f"""*** Settings ***
Library    Collections

*** Tasks ***
{task_name}
    Log    Test robot executed successfully
    [Return]    {{"status": "completed"}}
"""
    (robot_path / "tasks.robot").write_text(tasks_robot)
    
    # Create conda.yaml
    conda_yaml = """channels:
  - conda-forge

dependencies:
  - python=3.9
  - pip
  - pip:
    - rpaframework>=15.1.4
    - robotframework>=5.0.1
"""
    (robot_path / "conda.yaml").write_text(conda_yaml)
    
    # Create output directory
    (robot_path / "output").mkdir(exist_ok=True)
    
    return robot_path


def cleanup_robot(robot_path: Path) -> None:
    """Clean up test robot directory.
    
    Args:
        robot_path: Path to robot directory to delete
    """
    try:
        if robot_path.exists():
            shutil.rmtree(robot_path)
    except Exception as e:
        print(f"Failed to clean up robot: {e}")


def create_test_payload(
    order_id: str = "TEST-001",
    customer: str = "Test Customer"
) -> Dict[str, Any]:
    """Create a test work item payload.
    
    Args:
        order_id: Order ID
        customer: Customer name
        
    Returns:
        Test payload dictionary
    """
    return {
        "order_id": order_id,
        "customer_name": customer,
        "items": [
            {"sku": "ITEM-001", "qty": 5},
            {"sku": "ITEM-002", "qty": 3}
        ],
        "metadata": {
            "source": "integration_test",
            "timestamp": "2025-11-17T18:00:00Z"
        }
    }


def get_robot_list_from_output(response_text: str) -> list:
    """Parse robot list from API response.
    
    Args:
        response_text: JSON response text from /robot_agents/robots
        
    Returns:
        List of robot topics
    """
    data = json.loads(response_text)
    return [robot.get("topic") for robot in data.get("topics", [])]


class ServiceManager:
    """Helper for managing service lifecycle in integration tests."""
    
    def __init__(self, config_path: str):
        """Initialize service manager.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.process = None
        self.is_running = False
    
    async def start(self) -> None:
        """Start the robot agent service.
        
        Note: This would be implemented with actual process management
        in a full test suite. For now, it's a placeholder.
        """
        self.is_running = True
    
    async def stop(self) -> None:
        """Stop the robot agent service."""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except:
                self.process.kill()
        self.is_running = False
    
    def is_service_running(self) -> bool:
        """Check if service is running."""
        return self.is_running
