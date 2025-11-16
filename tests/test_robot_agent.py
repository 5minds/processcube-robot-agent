"""Unit tests for RobotAgent class."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from processcube_robot_agent.robot_agent.rcc.robot_agent import RobotAgent
from processcube_robot_agent.robot_agent.error import RobotError


class TestRobotAgentInit:
    """Tests for RobotAgent initialization."""

    def test_init_sets_attributes(self, mock_config):
        """Test that __init__ sets all required attributes."""
        agent = RobotAgent("test_robot.zip", mock_config)

        assert agent._filename == "test_robot.zip"
        assert agent._config == mock_config
        assert agent._wrap_dir == "robots/installed/rcc"
        assert agent._unwrap_dir == "temp/robots/rcc/unwrapped"

    def test_init_with_custom_config(self, tmp_path):
        """Test initialization with custom configuration."""
        config = MagicMock()
        config.get.side_effect = lambda section, key, default=None: {
            ('rcc', 'wrap_dir'): str(tmp_path / 'wrap'),
            ('rcc', 'unwrap_dir'): str(tmp_path / 'unwrap'),
        }.get((section, key), default)

        agent = RobotAgent("custom.zip", config)

        assert agent._filename == "custom.zip"
        assert agent._wrap_dir == str(tmp_path / 'wrap')


class TestRobotAgentGetData:
    """Tests for get_data method."""

    def test_get_data_returns_payload(self, mock_config):
        """Test that get_data returns the payload unchanged."""
        agent = RobotAgent("test.zip", mock_config)
        payload = {"key1": "value1", "key2": "value2"}

        result = agent.get_data(payload, {})

        assert result == payload
        assert result is payload

    def test_get_data_with_empty_payload(self, mock_config):
        """Test get_data with empty payload."""
        agent = RobotAgent("test.zip", mock_config)

        result = agent.get_data({}, {})

        assert result == {}

    def test_get_data_with_complex_payload(self, mock_config):
        """Test get_data with nested structures."""
        agent = RobotAgent("test.zip", mock_config)
        payload = {
            "user": {"name": "John", "id": 123},
            "items": [1, 2, 3],
            "active": True
        }

        result = agent.get_data(payload, {})

        assert result == payload
        assert result["user"]["name"] == "John"


class TestRobotAgentPaths:
    """Tests for path-related methods."""

    @patch('os.getcwd')
    def test_get_robot_filename(self, mock_cwd, mock_config):
        """Test get_robot_filename returns correct path."""
        mock_cwd.return_value = "/project"
        agent = RobotAgent("webui.zip", mock_config)

        result = agent.get_robot_filename()

        assert str(result).endswith("webui.zip")

    @patch('os.getcwd')
    def test_get_unwrapped_path(self, mock_cwd, mock_config):
        """Test get_unwrapped_path removes .zip suffix."""
        mock_cwd.return_value = "/project"
        agent = RobotAgent("webui.zip", mock_config)

        result = agent.get_unwrapped_path()

        assert str(result).endswith("webui")
        assert not str(result).endswith(".zip")

    @patch('os.getcwd')
    def test_get_unwrapped_path_without_zip(self, mock_cwd, mock_config):
        """Test get_unwrapped_path with non-.zip filename."""
        mock_cwd.return_value = "/project"
        agent = RobotAgent("webui", mock_config)

        result = agent.get_unwrapped_path()

        assert str(result).endswith("webui")


class TestRobotAgentCreateInputData:
    """Tests for create_input_data method."""

    @patch.dict('os.environ', {}, clear=True)
    def test_create_input_data_sets_environment(self, tmp_path, mock_config):
        """Test that create_input_data sets RPA environment variables."""
        agent = RobotAgent("test.zip", mock_config)
        temp_dir = str(tmp_path)
        payload = {"order_id": "123"}
        task = {"id": "task_001"}

        agent.create_input_data(temp_dir, payload, task)

        # Check environment variables are set
        assert "RPA_WORKITEMS_ADAPTER" in __import__('os').environ
        assert "RPA_WORKITEMS_PATH" in __import__('os').environ
        assert "RPA_INPUT_WORKITEM_PATH" in __import__('os').environ
        assert "RPA_OUTPUT_WORKITEM_PATH" in __import__('os').environ

    @patch.dict('os.environ', {}, clear=True)
    def test_create_input_data_creates_file(self, tmp_path, mock_config):
        """Test that create_input_data creates input JSON file."""
        agent = RobotAgent("test.zip", mock_config)
        temp_dir = str(tmp_path)
        payload = {"data": "test"}
        task = {"id": "task_001"}

        agent.create_input_data(temp_dir, payload, task)

        # Check file was created
        input_file = Path(temp_dir) / "task_001.json"
        assert input_file.exists()

    @patch.dict('os.environ', {}, clear=True)
    def test_create_input_data_json_format(self, tmp_path, mock_config):
        """Test that input data is in correct JSON format."""
        import json
        agent = RobotAgent("test.zip", mock_config)
        temp_dir = str(tmp_path)
        payload = {"key": "value"}
        task = {"id": "task_002"}

        agent.create_input_data(temp_dir, payload, task)

        # Check JSON format
        input_file = Path(temp_dir) / "task_002.json"
        data = json.loads(input_file.read_text())

        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["payload"] == payload


class TestRobotAgentReadOutputData:
    """Tests for read_output_data method."""

    def test_read_output_data_missing_file(self, tmp_path, mock_config):
        """Test read_output_data with missing output file."""
        agent = RobotAgent("test.zip", mock_config)
        temp_dir = str(tmp_path)
        task = {"id": "task_001"}

        result = agent.read_output_data(temp_dir, task)

        assert result == {}

    def test_read_output_data_valid_file(self, tmp_path, mock_config):
        """Test read_output_data with valid output file."""
        import json
        agent = RobotAgent("test.zip", mock_config)
        temp_dir = str(tmp_path)
        task = {"id": "task_001"}

        # Create output file
        output_file = Path(temp_dir) / "task_001.output.json"
        output_data = [{"payload": {"status": "success", "result": "data"}}]
        output_file.write_text(json.dumps(output_data))

        result = agent.read_output_data(temp_dir, task)

        assert result == {"status": "success", "result": "data"}

    def test_read_output_data_empty_list(self, tmp_path, mock_config):
        """Test read_output_data with empty output list."""
        import json
        agent = RobotAgent("test.zip", mock_config)
        temp_dir = str(tmp_path)
        task = {"id": "task_001"}

        # Create output file with empty list
        output_file = Path(temp_dir) / "task_001.output.json"
        output_file.write_text(json.dumps([]))

        result = agent.read_output_data(temp_dir, task)

        assert result == {}


class TestRobotAgentCheckRcc:
    """Tests for check_rcc method (inherited from RccRunner)."""

    @patch('subprocess.run')
    def test_check_rcc_success(self, mock_run, mock_config):
        """Test check_rcc when RCC is available."""
        mock_run.return_value = MagicMock(returncode=0)
        agent = RobotAgent("test.zip", mock_config)

        result = agent.check_rcc()

        assert result.returncode == 0
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_check_rcc_failure(self, mock_run, mock_config):
        """Test check_rcc when RCC is not available."""
        mock_run.return_value = MagicMock(returncode=1, stderr="not found")
        agent = RobotAgent("test.zip", mock_config)

        with pytest.raises(RobotError):
            agent.check_rcc()


class TestRobotAgentUnwrap:
    """Tests for unwrap method."""

    @patch('subprocess.run')
    @patch('pathlib.Path.mkdir')
    def test_unwrap_success(self, mock_mkdir, mock_run, mock_config):
        """Test successful robot unwrapping."""
        mock_run.return_value = MagicMock(returncode=0)
        agent = RobotAgent("test.zip", mock_config)

        result = agent.unwrap()

        assert result.returncode == 0
        mock_mkdir.assert_called()
        mock_run.assert_called_once()

    @patch('subprocess.run')
    @patch('pathlib.Path.mkdir')
    def test_unwrap_failure(self, mock_mkdir, mock_run, mock_config):
        """Test unwrap failure raises RobotError."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stderr="Unable to unwrap"
        )
        agent = RobotAgent("test.zip", mock_config)

        with pytest.raises(RobotError) as exc_info:
            agent.unwrap()

        assert "unwrap" in str(exc_info.value)

    @patch('subprocess.run')
    @patch('pathlib.Path.mkdir')
    def test_unwrap_uses_argument_list(self, mock_mkdir, mock_run, mock_config):
        """Test that unwrap uses argument list (not shell=True)."""
        mock_run.return_value = MagicMock(returncode=0)
        agent = RobotAgent("test.zip", mock_config)

        agent.unwrap()

        # Check that subprocess.run was called with list arguments
        call_args = mock_run.call_args
        assert isinstance(call_args[0][0], list)
        assert call_args[0][0][0] == "rcc"
        assert "shell" not in call_args[1] or call_args[1].get("shell") is False


class TestRobotAgentExecute:
    """Tests for execute method."""

    @patch('tempfile.TemporaryDirectory')
    @patch.object(RobotAgent, 'check_rcc')
    @patch.object(RobotAgent, 'create_input_data')
    @patch.object(RobotAgent, 'unwrap')
    @patch.object(RobotAgent, 'run_robot')
    @patch.object(RobotAgent, 'read_output_data')
    def test_execute_calls_all_steps(
        self,
        mock_read_output,
        mock_run,
        mock_unwrap,
        mock_create_input,
        mock_check_rcc,
        mock_temp_dir,
        mock_config
    ):
        """Test execute calls all required steps in order."""
        mock_temp_dir.return_value.__enter__.return_value = "/tmp"
        mock_read_output.return_value = {"status": "success"}

        agent = RobotAgent("test.zip", mock_config)
        payload = {"key": "value"}
        task = {"id": "task_001"}

        result = agent.execute(payload, task)

        assert result == {"status": "success"}
        mock_check_rcc.assert_called_once()
        mock_create_input.assert_called_once()
        mock_unwrap.assert_called_once()
        mock_run.assert_called_once()
        mock_read_output.assert_called_once()

    @patch('tempfile.TemporaryDirectory')
    @patch.object(RobotAgent, 'check_rcc')
    def test_execute_propagates_check_rcc_error(self, mock_check_rcc, mock_temp_dir, mock_config):
        """Test execute propagates RCC check errors."""
        mock_check_rcc.side_effect = RobotError("rcc", "RCC not found")

        agent = RobotAgent("test.zip", mock_config)

        with pytest.raises(RobotError):
            agent.execute({}, {"id": "task_001"})


class TestRobotAgentReadOutputXml:
    """Tests for read_output_xml method."""

    def test_read_output_xml_missing(self, tmp_path, mock_config):
        """Test read_output_xml when file doesn't exist."""
        agent = RobotAgent("test.zip", mock_config)
        yaml_path = tmp_path / "robot.yaml"

        result = agent.read_output_xml(yaml_path)

        assert result == ""

    def test_read_output_xml_exists(self, tmp_path, mock_config):
        """Test read_output_xml when file exists."""
        agent = RobotAgent("test.zip", mock_config)

        # Create output directory and file
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        output_file = output_dir / "output.xml"
        output_file.write_text("<robot>Test</robot>")

        yaml_path = tmp_path / "robot.yaml"
        result = agent.read_output_xml(yaml_path)

        assert result == "<robot>Test</robot>"