"""Tests for UV robot agent execution."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

from processcube_robot_agent.robot_agent.uv.robot_agent import RobotAgent
from processcube_robot_agent.robot_agent.error import RobotError


class MockConfig:
    """Mock configuration object."""

    def __init__(self):
        self._config = {
            "uv": {
                "wrap_dir": "robots/installed/uv",
                "unwrap_dir": "temp/robots/uv/unwrapped",
            }
        }

    def get(self, section, key, default=None):
        """Get configuration value."""
        if section in self._config and key in self._config[section]:
            return self._config[section][key]
        return default


class TestRobotAgent:
    """Test RobotAgent class."""

    def test_initialization(self):
        """Test robot agent initialization."""
        config = MockConfig()
        agent = RobotAgent("test_robot.zip", config)

        assert agent._filename == "test_robot.zip"
        assert agent._config is config
        assert agent._wrap_dir == "robots/installed/uv"
        assert agent._unwrap_dir == "temp/robots/uv/unwrapped"

    def test_initialization_custom_dirs(self):
        """Test initialization with custom directories."""
        config = MockConfig()
        config._config["uv"]["wrap_dir"] = "custom/wrap"
        config._config["uv"]["unwrap_dir"] = "custom/unwrap"

        agent = RobotAgent("test.zip", config)

        assert agent._wrap_dir == "custom/wrap"
        assert agent._unwrap_dir == "custom/unwrap"

    def test_get_robot_filename(self):
        """Test getting robot filename path."""
        config = MockConfig()
        agent = RobotAgent("myrobot.zip", config)

        path = agent.get_robot_filename()

        assert path.name == "myrobot.zip"
        assert str(path).endswith("robots/installed/uv/myrobot.zip")

    def test_get_unwrapped_path(self):
        """Test getting unwrapped directory path."""
        config = MockConfig()
        agent = RobotAgent("myrobot.zip", config)

        path = agent.get_unwrapped_path()

        assert path.name == "myrobot"
        assert str(path).endswith("temp/robots/uv/unwrapped/myrobot")

    def test_get_unwrapped_path_removes_zip(self):
        """Test that .zip extension is removed."""
        config = MockConfig()
        agent = RobotAgent("test_robot.zip", config)

        path = agent.get_unwrapped_path()

        assert not str(path).endswith(".zip")
        assert str(path).endswith("test_robot")

    def test_create_input_data(self):
        """Test creating input work item data."""
        config = MockConfig()
        agent = RobotAgent("test.zip", config)

        with tempfile.TemporaryDirectory() as tmpdir:
            payload = {"username": "test_user", "password": "secret"}
            task = {"id": "task123"}

            agent.create_input_data(tmpdir, payload, task)

            input_file = Path(tmpdir) / "task123.json"
            assert input_file.exists()

            with open(input_file) as f:
                data = json.load(f)

            assert len(data) == 1
            assert data[0]["payload"] == payload

    def test_read_output_data_file_exists(self):
        """Test reading output data when file exists."""
        config = MockConfig()
        agent = RobotAgent("test.zip", config)

        with tempfile.TemporaryDirectory() as tmpdir:
            task = {"id": "task456"}
            output_file = Path(tmpdir) / "task456.output.json"

            output_data = {"result": "success", "status": "completed"}
            with open(output_file, "w") as f:
                json.dump([{"payload": output_data}], f)

            result = agent.read_output_data(tmpdir, task)

            assert result == output_data

    def test_read_output_data_file_not_exists(self):
        """Test reading output data when file doesn't exist."""
        config = MockConfig()
        agent = RobotAgent("test.zip", config)

        with tempfile.TemporaryDirectory() as tmpdir:
            task = {"id": "nonexistent"}

            result = agent.read_output_data(tmpdir, task)

            assert result == {}

    def test_read_output_data_empty_list(self):
        """Test reading output data with empty payload list."""
        config = MockConfig()
        agent = RobotAgent("test.zip", config)

        with tempfile.TemporaryDirectory() as tmpdir:
            task = {"id": "task789"}
            output_file = Path(tmpdir) / "task789.output.json"

            with open(output_file, "w") as f:
                json.dump([], f)

            result = agent.read_output_data(tmpdir, task)

            assert result == {}

    def test_get_data(self):
        """Test extracting data from payload."""
        config = MockConfig()
        agent = RobotAgent("test.zip", config)

        payload = {"key1": "value1", "key2": "value2"}
        task = {"id": "ignored"}

        result = agent.get_data(payload, task)

        assert result == payload

    def test_get_robot_filename_is_absolute(self):
        """Test that robot filename is absolute path."""
        config = MockConfig()
        agent = RobotAgent("robot.zip", config)

        path = agent.get_robot_filename()

        assert path.is_absolute()

    def test_get_unwrapped_path_is_absolute(self):
        """Test that unwrapped path is absolute."""
        config = MockConfig()
        agent = RobotAgent("robot.zip", config)

        path = agent.get_unwrapped_path()

        assert path.is_absolute()

    def test_extract_dependencies_no_file(self):
        """Test extracting dependencies when pyproject.toml doesn't exist."""
        config = MockConfig()
        agent = RobotAgent("test.zip", config)

        result = agent._extract_dependencies(Path("/nonexistent/pyproject.toml"))

        assert result == []

    def test_extract_dependencies_valid_file(self):
        """Test extracting dependencies from valid pyproject.toml."""
        config = MockConfig()
        agent = RobotAgent("test.zip", config)

        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_file = Path(tmpdir) / "pyproject.toml"
            
            # Create a minimal pyproject.toml
            pyproject_content = """
[project]
name = "test-robot"
dependencies = [
    "robotframework>=7.0",
    "rpaframework>=31.0",
    "requests>=2.28.0"
]
"""
            pyproject_file.write_text(pyproject_content)

            result = agent._extract_dependencies(pyproject_file)

            assert len(result) == 3
            assert "robotframework>=7.0" in result
            assert "rpaframework>=31.0" in result
            assert "requests>=2.28.0" in result

    def test_extract_dependencies_no_dependencies_section(self):
        """Test extracting when no dependencies are defined."""
        config = MockConfig()
        agent = RobotAgent("test.zip", config)

        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_file = Path(tmpdir) / "pyproject.toml"
            
            pyproject_content = """
[project]
name = "test-robot"
"""
            pyproject_file.write_text(pyproject_content)

            result = agent._extract_dependencies(pyproject_file)

            assert result == []

    def test_extract_dependencies_invalid_toml(self):
        """Test extracting from invalid TOML file."""
        config = MockConfig()
        agent = RobotAgent("test.zip", config)

        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_file = Path(tmpdir) / "pyproject.toml"
            pyproject_file.write_text("invalid toml syntax ][")

            result = agent._extract_dependencies(pyproject_file)

            assert result == []

    def test_get_entry_point_from_pyproject_exists(self):
        """Test extracting entry point when it exists."""
        config = MockConfig()
        agent = RobotAgent("test.zip", config)

        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_file = Path(tmpdir) / "pyproject.toml"
            
            pyproject_content = """
[project.scripts]
robot_runner = "my_module:main"
another_tool = "other_module:run"
"""
            pyproject_file.write_text(pyproject_content)

            result = agent._get_entry_point_from_pyproject(pyproject_file)

            assert result == "robot_runner"

    def test_get_entry_point_from_pyproject_not_exists(self):
        """Test extracting entry point when none exists."""
        config = MockConfig()
        agent = RobotAgent("test.zip", config)

        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_file = Path(tmpdir) / "pyproject.toml"
            
            pyproject_content = """
[project]
name = "test-robot"
"""
            pyproject_file.write_text(pyproject_content)

            result = agent._get_entry_point_from_pyproject(pyproject_file)

            assert result is None

    def test_get_entry_point_from_pyproject_invalid_file(self):
        """Test extracting entry point from invalid TOML."""
        config = MockConfig()
        agent = RobotAgent("test.zip", config)

        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_file = Path(tmpdir) / "pyproject.toml"
            pyproject_file.write_text("invalid toml ][")

            result = agent._get_entry_point_from_pyproject(pyproject_file)

            assert result is None

    def test_get_entry_point_file_not_found(self):
        """Test extracting entry point from non-existent file."""
        config = MockConfig()
        agent = RobotAgent("test.zip", config)

        result = agent._get_entry_point_from_pyproject(Path("/nonexistent/pyproject.toml"))

        assert result is None

    def test_create_input_data_sets_environment_variables(self):
        """Test that create_input_data sets RPA environment variables."""
        config = MockConfig()
        agent = RobotAgent("test.zip", config)

        with tempfile.TemporaryDirectory() as tmpdir:
            payload = {"test": "data"}
            task = {"id": "task999"}

            import os
            original_env = dict(os.environ)

            agent.create_input_data(tmpdir, payload, task)

            # Check environment variables are set
            assert "RPA_WORKITEMS_ADAPTER" in os.environ
            assert os.environ["RPA_WORKITEMS_ADAPTER"] == "RPA.Robocorp.WorkItems.FileAdapter"
            assert "RPA_WORKITEMS_PATH" in os.environ
            assert "RPA_INPUT_WORKITEM_PATH" in os.environ
            assert "RPA_OUTPUT_WORKITEM_PATH" in os.environ

            # Restore environment
            os.environ.clear()
            os.environ.update(original_env)

    @patch("processcube_robot_agent.robot_agent.uv.robot_agent.subprocess.run")
    def test_unwrap_extracts_zip(self, mock_run):
        """Test that unwrap extracts ZIP file."""
        config = MockConfig()
        agent = RobotAgent("test.zip", config)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a mock robot file
            robot_path = Path(tmpdir) / "robots" / "installed" / "uv" / "test.zip"
            robot_path.parent.mkdir(parents=True, exist_ok=True)

            # Create a simple ZIP with a pyproject.toml
            import zipfile
            with zipfile.ZipFile(robot_path, "w") as zf:
                zf.writestr("pyproject.toml", "[project]\nname = 'test'\ndependencies = []")

            # Mock the paths
            with patch.object(agent, "get_robot_filename", return_value=robot_path):
                with patch.object(agent, "get_unwrapped_path") as mock_unwrapped:
                    unwrap_path = Path(tmpdir) / "unwrapped"
                    mock_unwrapped.return_value = unwrap_path

                    # Mock subprocess to avoid actual venv creation
                    mock_run.return_value = MagicMock(returncode=0)

                    agent.unwrap()

                    # Verify unwrap directory was created
                    assert unwrap_path.exists()
                    assert (unwrap_path / "pyproject.toml").exists()

    @patch("processcube_robot_agent.robot_agent.uv.robot_agent.subprocess.run")
    def test_unwrap_raises_on_extract_failure(self, mock_run):
        """Test that unwrap raises error on extraction failure."""
        config = MockConfig()
        agent = RobotAgent("invalid.zip", config)

        with tempfile.TemporaryDirectory() as tmpdir:
            robot_path = Path(tmpdir) / "invalid.zip"
            robot_path.write_text("not a zip file")

            with patch.object(agent, "get_robot_filename", return_value=robot_path):
                with patch.object(agent, "get_unwrapped_path") as mock_unwrapped:
                    mock_unwrapped.return_value = Path(tmpdir) / "unwrapped"

                    with pytest.raises(RobotError) as exc_info:
                        agent.unwrap()

                    assert "unwrap" in str(exc_info.value)

    def test_read_output_data_with_multiple_items(self):
        """Test reading output when list has multiple items."""
        config = MockConfig()
        agent = RobotAgent("test.zip", config)

        with tempfile.TemporaryDirectory() as tmpdir:
            task = {"id": "task123"}
            output_file = Path(tmpdir) / "task123.output.json"

            # Create output with multiple items
            output_data = {"result": "success"}
            with open(output_file, "w") as f:
                json.dump(
                    [
                        {"payload": output_data},
                        {"payload": {"other": "data"}},
                    ],
                    f,
                )

            result = agent.read_output_data(tmpdir, task)

            # Should return first item's payload
            assert result == output_data

    def test_create_input_data_json_format(self):
        """Test that input data is properly formatted JSON."""
        config = MockConfig()
        agent = RobotAgent("test.zip", config)

        with tempfile.TemporaryDirectory() as tmpdir:
            payload = {"nested": {"key": "value"}, "list": [1, 2, 3]}
            task = {"id": "task_complex"}

            agent.create_input_data(tmpdir, payload, task)

            input_file = Path(tmpdir) / "task_complex.json"
            
            with open(input_file) as f:
                data = json.load(f)

            assert data[0]["payload"]["nested"]["key"] == "value"
            assert data[0]["payload"]["list"] == [1, 2, 3]
