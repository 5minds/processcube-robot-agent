"""Tests for robot_runner CLI tool."""

from unittest.mock import patch, MagicMock
import pytest

from processcube_robot_agent.tools.robot_runner import (
    parse_arguments,
    load_config_robot_file,
    main,
)


class TestParseArguments:
    """Tests for argument parsing."""

    def test_parse_single_robot_file(self):
        """Test parsing single robot file argument."""
        robot_file, variables, tags = parse_arguments(["my_robot.robot"])
        
        assert robot_file == "my_robot.robot"
        assert variables == {}
        assert tags == []

    def test_parse_with_variables(self):
        """Test parsing with --variable arguments."""
        robot_file, variables, tags = parse_arguments([
            "my_robot.robot",
            "--variable", "USER=admin",
            "--variable", "PASSWORD=secret"
        ])
        
        assert robot_file == "my_robot.robot"
        assert variables == {"USER": "admin", "PASSWORD": "secret"}
        assert tags == []

    def test_parse_with_tags(self):
        """Test parsing with --tag arguments."""
        robot_file, variables, tags = parse_arguments([
            "my_robot.robot",
            "--tag", "smoke",
            "--tag", "critical"
        ])
        
        assert robot_file == "my_robot.robot"
        assert variables == {}
        assert tags == ["smoke", "critical"]

    def test_parse_with_variables_and_tags(self):
        """Test parsing with both variables and tags."""
        robot_file, variables, tags = parse_arguments([
            "my_robot.robot",
            "--variable", "USER=admin",
            "--tag", "smoke",
            "--variable", "PASS=secret",
            "--tag", "critical"
        ])
        
        assert robot_file == "my_robot.robot"
        assert variables == {"USER": "admin", "PASS": "secret"}
        assert tags == ["smoke", "critical"]

    def test_parse_no_robot_file(self):
        """Test parsing with no robot file specified."""
        robot_file, variables, tags = parse_arguments([
            "--variable", "USER=admin"
        ])
        
        assert robot_file is None
        assert variables == {"USER": "admin"}
        assert tags == []

    def test_parse_empty_args(self):
        """Test parsing with no arguments."""
        robot_file, variables, tags = parse_arguments([])
        
        assert robot_file is None
        assert variables == {}
        assert tags == []

    def test_parse_help_flag(self):
        """Test that --help is handled."""
        with pytest.raises(SystemExit) as exc_info:
            parse_arguments(["--help"])
        assert exc_info.value.code == 0

    def test_parse_help_flag_short(self):
        """Test that -h is handled."""
        with pytest.raises(SystemExit) as exc_info:
            parse_arguments(["-h"])
        assert exc_info.value.code == 0


class TestLoadConfigRobotFile:
    """Tests for loading robot file from config."""

    @patch('processcube_robot_agent.tools.robot_runner.Path')
    def test_load_config_file_exists(self, mock_path):
        """Test loading robot file from existing pyproject.toml."""
        import tempfile
        from pathlib import Path as RealPath
        
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_path = RealPath(tmpdir) / "pyproject.toml"
            pyproject_path.write_text("""
[tool.processcube]
robot_file = "my_robot.robot"
""")
            
            # Mock Path.cwd() to return our temp dir
            with patch('processcube_robot_agent.tools.robot_runner.Path.cwd', return_value=RealPath(tmpdir)):
                result = load_config_robot_file()
                assert result == "my_robot.robot"

    @patch('processcube_robot_agent.tools.robot_runner.Path')
    def test_load_config_no_file(self, mock_path):
        """Test loading when pyproject.toml doesn't exist."""
        from pathlib import Path as RealPath
        
        mock_path.cwd.return_value.joinpath.return_value.exists.return_value = False
        
        result = load_config_robot_file()
        assert result is None

    @patch('processcube_robot_agent.tools.robot_runner.Path')
    def test_load_config_no_setting(self, mock_path):
        """Test loading when robot_file not in config."""
        import tempfile
        from pathlib import Path as RealPath
        
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_path = RealPath(tmpdir) / "pyproject.toml"
            pyproject_path.write_text("[tool.other]\nkey = \"value\"")
            
            with patch('processcube_robot_agent.tools.robot_runner.Path.cwd', return_value=RealPath(tmpdir)):
                result = load_config_robot_file()
                assert result is None


class TestMainFunction:
    """Tests for main entry point."""

    @patch('processcube_robot_agent.tools.robot_runner.process_work_items')
    @patch('processcube_robot_agent.tools.robot_runner.RobotFrameworkExecutor')
    def test_main_with_robot_file(self, mock_executor_class, mock_process_work_items):
        """Test main with robot file argument."""
        mock_executor = MagicMock()
        mock_executor_class.return_value = mock_executor
        
        # Capture the processor function
        captured_processor = None
        def capture_processor(proc):
            nonlocal captured_processor
            captured_processor = proc
        
        mock_process_work_items.side_effect = capture_processor
        
        # Call main
        main(["my_robot.robot"])
        
        # Verify process_work_items was called
        mock_process_work_items.assert_called_once()
        assert captured_processor is not None

    @patch('processcube_robot_agent.tools.robot_runner.load_config_robot_file')
    def test_main_no_robot_file(self, mock_load_config):
        """Test main with no robot file specified."""
        mock_load_config.return_value = None
        
        with pytest.raises(SystemExit) as exc_info:
            main([])
        
        assert exc_info.value.code == 1

    @patch('processcube_robot_agent.tools.robot_runner.process_work_items')
    @patch('processcube_robot_agent.tools.robot_runner.RobotFrameworkExecutor')
    def test_main_processor_success(self, mock_executor_class, mock_process_work_items):
        """Test processor function with successful execution."""
        mock_executor = MagicMock()
        mock_executor.execute.return_value = {
            "status": "pass",
            "return_code": 0,
            "output_xml": "<xml/>"
        }
        mock_executor_class.return_value = mock_executor
        
        captured_processor = None
        def capture_processor(proc):
            nonlocal captured_processor
            captured_processor = proc
        
        mock_process_work_items.side_effect = capture_processor
        
        main(["my_robot.robot"])
        
        # Call processor with test payload
        result = captured_processor({"data": "test"})
        
        assert result["status"] == "pass"
        assert result["return_code"] == 0
        mock_executor.execute.assert_called_once_with(
            robot_file="my_robot.robot",
            variables={},
            tags=None
        )

    @patch('processcube_robot_agent.tools.robot_runner.process_work_items')
    @patch('processcube_robot_agent.tools.robot_runner.RobotFrameworkExecutor')
    @patch('processcube_robot_agent.tools.robot_runner.raise_robot_test_failed')
    def test_main_processor_test_failed(self, mock_raise_error, mock_executor_class, mock_process_work_items):
        """Test processor function when tests fail."""
        mock_executor = MagicMock()
        mock_executor.execute.return_value = {
            "status": "fail",
            "return_code": 1
        }
        mock_executor_class.return_value = mock_executor
        
        captured_processor = None
        def capture_processor(proc):
            nonlocal captured_processor
            captured_processor = proc
        
        mock_process_work_items.side_effect = capture_processor
        
        main(["my_robot.robot"])
        
        # Call processor - should raise
        with pytest.raises(Exception):  # FunctionalError
            captured_processor({"data": "test"})
        
        mock_raise_error.assert_called_once()

    @patch('processcube_robot_agent.tools.robot_runner.process_work_items')
    @patch('processcube_robot_agent.tools.robot_runner.RobotFrameworkExecutor')
    def test_main_with_variables(self, mock_executor_class, mock_process_work_items):
        """Test main with variables passed."""
        mock_executor = MagicMock()
        mock_executor.execute.return_value = {"status": "pass", "return_code": 0}
        mock_executor_class.return_value = mock_executor
        
        captured_processor = None
        def capture_processor(proc):
            nonlocal captured_processor
            captured_processor = proc
        
        mock_process_work_items.side_effect = capture_processor
        
        main([
            "my_robot.robot",
            "--variable", "USER=admin",
            "--variable", "PASSWORD=secret"
        ])
        
        # Call processor
        captured_processor({})
        
        # Verify variables were passed
        mock_executor.execute.assert_called_once()
        call_args = mock_executor.execute.call_args
        assert call_args[1]["variables"] == {"USER": "admin", "PASSWORD": "secret"}

    @patch('processcube_robot_agent.tools.robot_runner.process_work_items')
    @patch('processcube_robot_agent.tools.robot_runner.RobotFrameworkExecutor')
    def test_main_with_tags(self, mock_executor_class, mock_process_work_items):
        """Test main with tags passed."""
        mock_executor = MagicMock()
        mock_executor.execute.return_value = {"status": "pass", "return_code": 0}
        mock_executor_class.return_value = mock_executor
        
        captured_processor = None
        def capture_processor(proc):
            nonlocal captured_processor
            captured_processor = proc
        
        mock_process_work_items.side_effect = capture_processor
        
        main([
            "my_robot.robot",
            "--tag", "smoke",
            "--tag", "critical"
        ])
        
        # Call processor
        captured_processor({})
        
        # Verify tags were passed
        mock_executor.execute.assert_called_once()
        call_args = mock_executor.execute.call_args
        assert call_args[1]["tags"] == ["smoke", "critical"]
