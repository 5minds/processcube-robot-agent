"""Pytest configuration and shared fixtures."""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
from processcube_sdk.configuration import Config


@pytest.fixture
def mock_config() -> Mock:
    """Create a mock configuration object.

    Returns:
        Mock config with RCC and REST API settings.
    """
    config = MagicMock(spec=Config)
    config.get.side_effect = lambda section, key, default=None: {
        ('rcc', 'wrap_dir'): 'robots/installed/rcc',
        ('rcc', 'unwrap_dir'): 'temp/robots/rcc/unwrapped',
        ('rcc', 'topic_prefix'): 'robot_task',
        ('rcc', 'project_dir'): 'robots/src/rcc',
        ('rest_api', 'port'): 8000,
        ('rest_api', 'host'): '127.0.0.1',
    }.get((section, key), default)
    return config


@pytest.fixture
def temp_robot_dir(tmp_path) -> Path:
    """Create a temporary robot directory structure.

    Args:
        tmp_path: Pytest temporary directory.

    Returns:
        Path to temporary robot directory with robot.yaml.
    """
    robot_dir = tmp_path / "webui"
    robot_dir.mkdir()

    # Create robot.yaml
    robot_yaml = robot_dir / "robot.yaml"
    robot_yaml.write_text("""
tasks:
  TestTask:
    robotTaskName: Test Task
condaConfigFile: conda.yaml
artifactsDir: output
PATH: [.]
PYTHONPATH: [.]
""")

    # Create tasks.robot
    tasks_robot = robot_dir / "tasks.robot"
    tasks_robot.write_text("""
*** Tasks ***
TestTask
    Log    Test execution
""")

    return robot_dir


@pytest.fixture
def mock_external_task_client() -> Mock:
    """Create a mock external task client.

    Returns:
        Mock client for subscribing to external tasks.
    """
    client = MagicMock()
    client.subscribe_to_external_task_for_topic = MagicMock()
    return client