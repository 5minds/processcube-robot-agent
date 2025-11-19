"""Tests for RobotFrameworkExecutor tool."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from processcube_robot_agent.tools import RobotFrameworkExecutor


@pytest.fixture
def executor():
    """Create a RobotFrameworkExecutor instance."""
    return RobotFrameworkExecutor()


class TestRobotExecutor:
    """Tests for RobotFrameworkExecutor class."""
    
    def test_executor_initialization(self, executor):
        """Test that executor initializes properly."""
        assert executor is not None
    
    @patch('processcube_robot_agent.tools.robot_executor.subprocess.run')
    def test_execute_success(self, mock_run, executor):
        """Test successful robot execution with minimal Option A format."""
        # Mock successful robot execution
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Robot execution output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a dummy robot file
            robot_file = Path(tmpdir) / "test.robot"
            robot_file.write_text("*** Test Cases ***\nTest\n    Log    Hello")

            # Create output.xml for the test
            output_dir = Path(tmpdir) / "output"
            output_dir.mkdir()
            output_xml = output_dir / "output.xml"
            output_xml.write_text(
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<robot><statistics><total><stat total="1" passed="1" failed="0"/></total></statistics></robot>'
            )

            # Patch the output directory creation
            with patch('processcube_robot_agent.tools.robot_executor.tempfile.TemporaryDirectory') as mock_tmpdir:
                mock_context = MagicMock()
                mock_context.__enter__.return_value = tmpdir
                mock_context.__exit__.return_value = None
                mock_tmpdir.return_value = mock_context

                result = executor.execute(str(robot_file))

                # Verify Option A minimal format
                assert result["status"] == "pass"
                assert result["return_code"] == 0
                assert "duration" in result
                assert isinstance(result["duration"], float)
                assert "tests_passed" in result
                assert result["tests_passed"] == 1
                assert "log_html" in result

                # Verify verbose fields are NOT included
                assert "stdout" not in result
                assert "stderr" not in result
                assert "output_xml" not in result
    
    def test_execute_robot_file_not_found(self, executor):
        """Test execution with non-existent robot file."""
        result = executor.execute("/nonexistent/path/test.robot")
        
        assert result["status"] == "error"
        assert "Robot file not found" in result["error"]
        assert result["return_code"] == -1
    
    @patch('processcube_robot_agent.tools.robot_executor.subprocess.run')
    def test_execute_with_variables(self, mock_run, executor):
        """Test execution with variables."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        with tempfile.TemporaryDirectory() as tmpdir:
            robot_file = Path(tmpdir) / "test.robot"
            robot_file.write_text("*** Test Cases ***\nTest\n    Log    ${VAR}")
            
            # Create output dir
            output_dir = Path(tmpdir) / "output"
            output_dir.mkdir()
            
            with patch('processcube_robot_agent.tools.robot_executor.tempfile.TemporaryDirectory') as mock_tmpdir:
                mock_context = MagicMock()
                mock_context.__enter__.return_value = tmpdir
                mock_context.__exit__.return_value = None
                mock_tmpdir.return_value = mock_context
                
                result = executor.execute(
                    str(robot_file),
                    variables={"VAR": "test_value"}
                )
                
                # Verify subprocess was called with variablefile parameter
                call_args = mock_run.call_args[0][0]
                assert "--variablefile" in call_args
    
    @patch('processcube_robot_agent.tools.robot_executor.subprocess.run')
    def test_execute_with_tags(self, mock_run, executor):
        """Test execution with tags."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        with tempfile.TemporaryDirectory() as tmpdir:
            robot_file = Path(tmpdir) / "test.robot"
            robot_file.write_text("*** Test Cases ***\nTest\n    Log    Hello")
            
            output_dir = Path(tmpdir) / "output"
            output_dir.mkdir()
            
            with patch('processcube_robot_agent.tools.robot_executor.tempfile.TemporaryDirectory') as mock_tmpdir:
                mock_context = MagicMock()
                mock_context.__enter__.return_value = tmpdir
                mock_context.__exit__.return_value = None
                mock_tmpdir.return_value = mock_context
                
                result = executor.execute(
                    str(robot_file),
                    tags=["smoke", "critical"]
                )
                
                # Verify subprocess was called with include tags
                call_args = mock_run.call_args[0][0]
                assert "--include" in call_args
    
    @patch('processcube_robot_agent.tools.robot_executor.subprocess.run')
    def test_execute_with_suite_name(self, mock_run, executor):
        """Test execution with custom suite name."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        with tempfile.TemporaryDirectory() as tmpdir:
            robot_file = Path(tmpdir) / "test.robot"
            robot_file.write_text("*** Test Cases ***\nTest\n    Log    Hello")
            
            output_dir = Path(tmpdir) / "output"
            output_dir.mkdir()
            
            with patch('processcube_robot_agent.tools.robot_executor.tempfile.TemporaryDirectory') as mock_tmpdir:
                mock_context = MagicMock()
                mock_context.__enter__.return_value = tmpdir
                mock_context.__exit__.return_value = None
                mock_tmpdir.return_value = mock_context
                
                result = executor.execute(
                    str(robot_file),
                    suite_name="My Test Suite"
                )
                
                # Verify subprocess was called with suite name
                call_args = mock_run.call_args[0][0]
                assert "--name" in call_args
                assert "My Test Suite" in call_args
    
    @patch('processcube_robot_agent.tools.robot_executor.subprocess.run')
    def test_execute_timeout(self, mock_run, executor):
        """Test execution timeout handling."""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("robot", 3600)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            robot_file = Path(tmpdir) / "test.robot"
            robot_file.write_text("*** Test Cases ***\nTest\n    Log    Hello")
            
            result = executor.execute(str(robot_file))
            
            assert result["status"] == "error"
            assert "timed out" in result["error"].lower()
            assert result["return_code"] == -1
    
    @patch('processcube_robot_agent.tools.robot_executor.subprocess.run')
    def test_execute_subprocess_error(self, mock_run, executor):
        """Test execution with subprocess error."""
        mock_run.side_effect = Exception("Command not found")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            robot_file = Path(tmpdir) / "test.robot"
            robot_file.write_text("*** Test Cases ***\nTest\n    Log    Hello")
            
            result = executor.execute(str(robot_file))
            
            assert result["status"] == "error"
            assert "Command not found" in result["error"]
            assert result["return_code"] == -1
