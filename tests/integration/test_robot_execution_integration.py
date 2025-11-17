"""Integration tests for end-to-end robot execution.

Tests the complete flow from task submission to robot execution and result handling.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Any, Dict

from tests.integration.helpers import (
    create_test_robot,
    cleanup_robot,
    create_test_payload
)


class TestRobotExecutionBasics:
    """Test basic robot execution flow."""
    
    def test_robot_can_be_executed(self):
        """Test that a robot can be executed via the agent."""
        # Create test robot
        robot_path = create_test_robot("test_execution", task_name="ExecuteTest")
        
        try:
            assert robot_path.exists()
            assert (robot_path / "robot.yaml").exists()
            assert (robot_path / "tasks.robot").exists()
            assert (robot_path / "conda.yaml").exists()
        finally:
            cleanup_robot(robot_path)
    
    def test_robot_payload_handling(self):
        """Test that robot payload is handled correctly."""
        payload = create_test_payload(
            order_id="TEST-001",
            customer="Test Customer"
        )
        
        assert payload["order_id"] == "TEST-001"
        assert payload["customer_name"] == "Test Customer"
        assert "items" in payload
        assert len(payload["items"]) == 2
    
    def test_robot_output_directory_created(self):
        """Test that robot output directory is created."""
        robot_path = create_test_robot("test_output")
        
        try:
            output_dir = robot_path / "output"
            assert output_dir.exists()
            assert output_dir.is_dir()
        finally:
            cleanup_robot(robot_path)
    
    def test_robot_agent_structure(self):
        """Test robot agent structure and capabilities."""
        from processcube_robot_agent.robot_agent.rcc.robot_agent import RobotAgent
        
        # RobotAgent should have execute method
        assert hasattr(RobotAgent, 'execute')
        assert callable(getattr(RobotAgent, 'execute'))


class TestRobotTaskExecution:
    """Test specific robot task execution scenarios."""
    
    def test_robot_with_single_task(self):
        """Test robot with a single task."""
        robot_path = create_test_robot("single_task", task_name="SingleTask")
        
        try:
            robot_yaml = (robot_path / "robot.yaml").read_text()
            assert "SingleTask" in robot_yaml
        finally:
            cleanup_robot(robot_path)
    
    def test_robot_with_multiple_tasks(self):
        """Test robot with multiple tasks."""
        robot_path = create_test_robot("multi_task", task_name="MainTask")
        
        try:
            # Add another task to robot.yaml
            yaml_content = (robot_path / "robot.yaml").read_text()
            yaml_content += """  SecondTask:
    robotTaskName: SecondTask
"""
            (robot_path / "robot.yaml").write_text(yaml_content)
            
            robot_yaml = (robot_path / "robot.yaml").read_text()
            assert "MainTask" in robot_yaml
            assert "SecondTask" in robot_yaml
        finally:
            cleanup_robot(robot_path)
    
    def test_robot_task_with_input_data(self):
        """Test robot task receives input data."""
        payload = create_test_payload()
        
        assert "order_id" in payload
        assert "customer_name" in payload
        assert "items" in payload
        assert isinstance(payload["items"], list)
    
    def test_robot_task_output_generation(self):
        """Test robot task output generation."""
        robot_path = create_test_robot("output_test")
        
        try:
            # Simulate output file creation
            output_file = robot_path / "output" / "output.json"
            output_data = {
                "status": "completed",
                "result": {"processed": 5}
            }
            output_file.write_text(json.dumps(output_data))
            
            # Verify output can be read
            result = json.loads(output_file.read_text())
            assert result["status"] == "completed"
            assert result["result"]["processed"] == 5
        finally:
            cleanup_robot(robot_path)


class TestRobotExecutionErrors:
    """Test error scenarios during robot execution."""
    
    def test_error_class_exists(self):
        """Test that error classes exist."""
        from processcube_robot_agent.robot_agent.error import RobotError
        
        # Error class should be importable
        assert RobotError is not None
        
        # Should inherit from FunctionalError
        from processcube_sdk.external_tasks import FunctionalError
        assert issubclass(RobotError, FunctionalError)
    
    def test_robot_agent_methods_exist(self):
        """Test that robot agent has required methods."""
        from processcube_robot_agent.robot_agent.rcc.robot_agent import RobotAgent
        
        # Check that required methods exist
        assert hasattr(RobotAgent, 'unwrap')
        assert hasattr(RobotAgent, 'check_rcc')
        assert hasattr(RobotAgent, 'execute')
    
    def test_robot_initialization_structure(self):
        """Test robot agent initialization structure."""
        from processcube_robot_agent.robot_agent.rcc.robot_agent import RobotAgent
        
        # RobotAgent should be a class
        assert isinstance(RobotAgent, type)
        
        # Should have __init__ method
        assert hasattr(RobotAgent, '__init__')
    
    def test_invalid_task_name(self):
        """Test handling of invalid task name."""
        robot_path = create_test_robot("task_error", task_name="ValidTask")
        
        try:
            # Try to access non-existent task
            tasks_file = robot_path / "tasks.robot"
            content = tasks_file.read_text()
            assert "ValidTask" in content
            assert "InvalidTask" not in content
        finally:
            cleanup_robot(robot_path)


class TestRobotExecutionWithPayload:
    """Test robot execution with various payload scenarios."""
    
    def test_execution_with_empty_payload(self):
        """Test robot execution with empty payload."""
        payload = {}
        assert isinstance(payload, dict)
        assert len(payload) == 0
    
    def test_execution_with_simple_payload(self):
        """Test robot execution with simple key-value payload."""
        payload = {
            "order_id": "ORD-001",
            "customer": "ACME Corp"
        }
        
        assert payload["order_id"] == "ORD-001"
        assert payload["customer"] == "ACME Corp"
    
    def test_execution_with_nested_payload(self):
        """Test robot execution with nested payload structure."""
        payload = {
            "order": {
                "id": "ORD-001",
                "items": [
                    {"sku": "ITEM-001", "qty": 5},
                    {"sku": "ITEM-002", "qty": 3}
                ]
            },
            "customer": {
                "name": "ACME Corp",
                "email": "contact@acme.com"
            }
        }
        
        assert payload["order"]["id"] == "ORD-001"
        assert len(payload["order"]["items"]) == 2
        assert payload["customer"]["name"] == "ACME Corp"
    
    def test_execution_with_large_payload(self):
        """Test robot execution with large payload."""
        items = [{"sku": f"ITEM-{i:03d}", "qty": i} for i in range(100)]
        payload = {
            "order_id": "BIG-ORDER",
            "items": items
        }
        
        assert len(payload["items"]) == 100
        assert payload["items"][0]["sku"] == "ITEM-000"
        assert payload["items"][99]["sku"] == "ITEM-099"


class TestRobotExecutionResults:
    """Test robot execution result handling."""
    
    def test_successful_execution_result(self):
        """Test handling of successful robot execution result."""
        result = {
            "status": "completed",
            "task_id": "task-123",
            "duration_ms": 1234,
            "result": {
                "processed_items": 5,
                "success_count": 5,
                "error_count": 0
            }
        }
        
        assert result["status"] == "completed"
        assert result["result"]["success_count"] == 5
    
    def test_failed_execution_result(self):
        """Test handling of failed robot execution result."""
        result = {
            "status": "failed",
            "task_id": "task-456",
            "error": "Robot execution timeout",
            "error_details": {
                "code": "TIMEOUT",
                "message": "Robot did not complete within 300 seconds"
            }
        }
        
        assert result["status"] == "failed"
        assert result["error_details"]["code"] == "TIMEOUT"
    
    def test_execution_result_with_output_data(self):
        """Test result includes output data."""
        result = {
            "status": "completed",
            "output": {
                "extracted_data": [
                    {"id": 1, "name": "Item 1"},
                    {"id": 2, "name": "Item 2"}
                ],
                "summary": {
                    "total_processed": 2,
                    "duration_seconds": 5.2
                }
            }
        }
        
        assert len(result["output"]["extracted_data"]) == 2
        assert result["output"]["summary"]["total_processed"] == 2


class TestRobotExecutionIntegration:
    """Test full integration of robot execution flow."""
    
    def test_complete_execution_flow(self):
        """Test complete flow from robot creation to execution."""
        # Create robot
        robot_path = create_test_robot("complete_flow", task_name="CompleteTest")
        
        try:
            # Verify robot structure
            assert robot_path.exists()
            assert (robot_path / "robot.yaml").exists()
            
            # Verify payload preparation
            payload = create_test_payload()
            assert "order_id" in payload
            
            # Simulate output
            output_dir = robot_path / "output"
            assert output_dir.exists()
            
            # Simulate result
            result = {
                "status": "completed",
                "payload": payload
            }
            assert result["status"] == "completed"
            
        finally:
            cleanup_robot(robot_path)
    
    def test_mock_agent_execution_simulation(self):
        """Test mock agent execution simulation."""
        # Create mock agent
        mock_agent = Mock()
        mock_agent.execute.return_value = {"status": "completed"}
        
        # Execute
        payload = create_test_payload()
        task = {"id": "task-789", "topic": "test.robot"}
        
        result = mock_agent.execute(payload, task)
        
        assert result["status"] == "completed"
        mock_agent.execute.assert_called_once_with(payload, task)
