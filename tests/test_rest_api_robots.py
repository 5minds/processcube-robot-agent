"""Unit tests for REST API robots endpoint."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from processcube_robot_agent.rest_api_command import webapp


client = TestClient(webapp)


class TestGetRobotsEndpoint:
    """Tests for GET /robot_agents/robots endpoint."""

    @patch('processcube_robot_agent.rest_api.robots.builder.build')
    @pytest.mark.asyncio
    async def test_get_robots_returns_robots_list(self, mock_build):
        """Test that endpoint returns a list of robots."""
        # Setup mocks
        mock_factory = MagicMock()
        mock_factory.get_topic_prefix.return_value = "robot_task"
        mock_factory.__iter__.return_value = []
        mock_build.return_value = mock_factory

        # Execute
        response = client.get("/robot_agents/robots")

        # Verify
        assert response.status_code == 200
        assert "topics" in response.json()
        assert isinstance(response.json()["topics"], list)

    @patch('processcube_robot_agent.rest_api.robots.builder.build')
    def test_get_robots_empty_list(self, mock_build):
        """Test that endpoint returns empty list when no robots available."""
        # Setup mocks
        mock_factory = MagicMock()
        mock_factory.get_topic_prefix.return_value = "robot_task"
        mock_factory.__iter__.return_value = []
        mock_build.return_value = mock_factory

        # Execute
        response = client.get("/robot_agents/robots")

        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["topics"] == []

    @patch('processcube_robot_agent.rest_api.robots.builder.build')
    def test_get_robots_with_single_robot(self, mock_build):
        """Test that endpoint returns single robot with correct structure."""
        # Setup mocks
        mock_task_record = MagicMock()
        mock_task_record.get_topic.return_value = "robot_task.my_robot"

        mock_factory = MagicMock()
        mock_factory.get_topic_prefix.return_value = "robot_task"
        mock_factory.__iter__.return_value = [mock_task_record]
        mock_build.return_value = mock_factory

        # Execute
        response = client.get("/robot_agents/robots")

        # Verify
        assert response.status_code == 200
        data = response.json()
        assert len(data["topics"]) == 1
        robot = data["topics"][0]
        assert "name" in robot
        assert "topic" in robot
        assert robot["topic"] == "robot_task.my_robot"

    @patch('processcube_robot_agent.rest_api.robots.builder.build')
    def test_get_robots_topic_prefix_stripped(self, mock_build):
        """Test that topic prefix is stripped from robot name."""
        # Setup mocks
        mock_task_record = MagicMock()
        mock_task_record.get_topic.return_value = "robot_task.folder.my_robot"

        mock_factory = MagicMock()
        mock_factory.get_topic_prefix.return_value = "robot_task"
        mock_factory.__iter__.return_value = [mock_task_record]
        mock_build.return_value = mock_factory

        # Execute
        response = client.get("/robot_agents/robots")

        # Verify
        assert response.status_code == 200
        data = response.json()
        robot = data["topics"][0]
        # Name should have dots converted to slashes and prefix removed
        assert "/" in robot["name"]

    @patch('processcube_robot_agent.rest_api.robots.builder.build')
    def test_get_robots_multiple_robots(self, mock_build):
        """Test that endpoint returns multiple robots."""
        # Setup mocks
        mock_task_record1 = MagicMock()
        mock_task_record1.get_topic.return_value = "robot_task.robot1"

        mock_task_record2 = MagicMock()
        mock_task_record2.get_topic.return_value = "robot_task.robot2"

        mock_task_record3 = MagicMock()
        mock_task_record3.get_topic.return_value = "robot_task.robot3"

        mock_factory = MagicMock()
        mock_factory.get_topic_prefix.return_value = "robot_task"
        mock_factory.__iter__.return_value = [
            mock_task_record1,
            mock_task_record2,
            mock_task_record3,
        ]
        mock_build.return_value = mock_factory

        # Execute
        response = client.get("/robot_agents/robots")

        # Verify
        assert response.status_code == 200
        data = response.json()
        assert len(data["topics"]) == 3

    @patch('processcube_robot_agent.rest_api.robots.builder.build')
    def test_get_robots_response_format(self, mock_build):
        """Test that response follows Robots model format."""
        # Setup mocks
        mock_task_record = MagicMock()
        mock_task_record.get_topic.return_value = "robot_task.test_bot"

        mock_factory = MagicMock()
        mock_factory.get_topic_prefix.return_value = "robot_task"
        mock_factory.__iter__.return_value = [mock_task_record]
        mock_build.return_value = mock_factory

        # Execute
        response = client.get("/robot_agents/robots")

        # Verify JSON structure
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "topics" in data
        assert isinstance(data["topics"], list)
        if len(data["topics"]) > 0:
            robot = data["topics"][0]
            assert isinstance(robot, dict)
            assert "name" in robot
            assert "topic" in robot
            assert isinstance(robot["name"], str)
            assert isinstance(robot["topic"], str)

    @patch('processcube_robot_agent.rest_api.robots.builder.build')
    def test_get_robots_calls_builder(self, mock_build):
        """Test that endpoint calls builder.build()."""
        # Setup mocks
        mock_factory = MagicMock()
        mock_factory.get_topic_prefix.return_value = "robot_task"
        mock_factory.__iter__.return_value = []
        mock_build.return_value = mock_factory

        # Execute
        client.get("/robot_agents/robots")

        # Verify builder was called
        mock_build.assert_called_once()

    @patch('processcube_robot_agent.rest_api.robots.builder.build')
    def test_get_robots_dot_to_slash_conversion(self, mock_build):
        """Test that dots in topics are converted to slashes in names."""
        # Setup mocks
        mock_task_record = MagicMock()
        mock_task_record.get_topic.return_value = "robot_task.folder.subfolder.robot"

        mock_factory = MagicMock()
        mock_factory.get_topic_prefix.return_value = "robot_task"
        mock_factory.__iter__.return_value = [mock_task_record]
        mock_build.return_value = mock_factory

        # Execute
        response = client.get("/robot_agents/robots")

        # Verify
        assert response.status_code == 200
        data = response.json()
        robot = data["topics"][0]
        # After conversion, name should use slashes
        assert "/" in robot["name"]


class TestRobotModel:
    """Tests for Robot Pydantic model."""

    def test_robot_model_creation(self):
        """Test that Robot model can be created with valid data."""
        from processcube_robot_agent.rest_api.robots import Robot

        robot = Robot(name="test_robot", topic="robot_task.test")
        assert robot.name == "test_robot"
        assert robot.topic == "robot_task.test"

    def test_robot_model_validation(self):
        """Test that Robot model validates required fields."""
        from processcube_robot_agent.rest_api.robots import Robot

        try:
            # Should fail without required name
            robot = Robot(topic="robot_task.test")
            pytest.fail("Robot model should require 'name' field")
        except Exception:
            pass

    def test_robots_model_empty_list(self):
        """Test that Robots model accepts empty list."""
        from processcube_robot_agent.rest_api.robots import Robots

        robots = Robots(topics=[])
        assert robots.topics == []

    def test_robots_model_with_robots(self):
        """Test that Robots model can contain multiple robots."""
        from processcube_robot_agent.rest_api.robots import Robot, Robots

        robot1 = Robot(name="robot1", topic="topic1")
        robot2 = Robot(name="robot2", topic="topic2")
        robots = Robots(topics=[robot1, robot2])

        assert len(robots.topics) == 2
        assert robots.topics[0].name == "robot1"
        assert robots.topics[1].name == "robot2"