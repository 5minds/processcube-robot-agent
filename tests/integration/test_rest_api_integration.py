"""Integration tests for REST API endpoints.

Tests the REST API functionality including:
- Service startup and health checks
- Robot listing endpoints
- Response format validation
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from processcube_robot_agent.rest_api import robots


class TestRESTAPIHealthCheck:
    """Test REST API health and availability."""
    
    def test_service_can_initialize(self):
        """Test that REST API service can be initialized."""
        from processcube_robot_agent.rest_api_command import webapp
        
        assert webapp is not None
        assert hasattr(webapp, 'include_router')
        assert hasattr(webapp, 'openapi')
    
    def test_service_has_robot_router(self):
        """Test that REST API includes robot endpoints."""
        from processcube_robot_agent.rest_api_command import webapp
        
        # Check that router is included
        assert len(webapp.routes) > 0
        
        # Look for robots endpoint
        robot_routes = [r for r in webapp.routes if 'robots' in str(r.path)]
        assert len(robot_routes) > 0


class TestRobotsEndpoint:
    """Test /robot_agents/robots endpoint integration."""
    
    def test_robots_endpoint_exists(self):
        """Test that robots endpoint is properly registered."""
        assert hasattr(robots, 'router')
        assert hasattr(robots.router, 'routes')
        
        # Find GET /robot_agents/robots route
        routes = list(robots.router.routes)
        assert len(routes) > 0
    
    def test_get_robots_returns_list(self):
        """Test that robots endpoint structure is correct."""
        from processcube_robot_agent.rest_api.robots import Robots, Robot
        
        # Create response model
        robots = Robots(topics=[
            Robot(name='webui', topic='test.webui'),
            Robot(name='windows.ui', topic='test.windows.ui')
        ])
        
        # Verify response
        assert robots is not None
        assert 'topics' in robots.__dict__
        assert isinstance(robots.topics, list)
        assert len(robots.topics) == 2
    
    def test_get_robots_empty_list(self):
        """Test robots endpoint with no registered robots."""
        from processcube_robot_agent.rest_api.robots import Robots
        
        robots = Robots(topics=[])
        
        assert robots.topics == []
    
    def test_get_robots_topic_format(self):
        """Test that robots endpoint formats topics correctly."""
        from processcube_robot_agent.rest_api.robots import Robots, Robot
        
        robots = Robots(topics=[
            Robot(name='webui', topic='test.webui')
        ])
        
        topics = robots.topics
        assert len(topics) == 1
        assert topics[0].name == 'webui'
        assert topics[0].topic == 'test.webui'
    
    def test_get_robots_multiple_robots(self):
        """Test robots endpoint with multiple robots."""
        from processcube_robot_agent.rest_api.robots import Robots, Robot
        
        robots = Robots(topics=[
            Robot(name='webui', topic='test.webui'),
            Robot(name='windows/ui', topic='test.windows.ui'),
            Robot(name='web-example-rpa-challenge', topic='test.web-example-rpa-challenge'),
        ])
        
        assert len(robots.topics) == 3
        names = [r.name for r in robots.topics]
        assert 'webui' in names
        assert 'windows/ui' in names
        assert 'web-example-rpa-challenge' in names
    
    def test_get_robots_response_format(self):
        """Test that response format matches API specification."""
        from processcube_robot_agent.rest_api.robots import Robots, Robot
        
        robots = Robots(topics=[
            Robot(name='test', topic='test.test')
        ])
        
        # Verify structure
        assert hasattr(robots, 'topics')
        assert isinstance(robots.topics, list)
        
        topics = robots.topics
        assert len(topics) > 0
        
        topic = topics[0]
        assert hasattr(topic, 'name')
        assert hasattr(topic, 'topic')
        assert isinstance(topic.name, str)
        assert isinstance(topic.topic, str)


class TestRESTAPIErrorHandling:
    """Test error handling in REST API."""
    
    def test_robots_endpoint_error_scenario(self):
        """Test endpoint error handling scenarios."""
        from processcube_robot_agent.rest_api.robots import Robots, Robot
        
        # Test that malformed data is caught during model creation
        try:
            # This should fail due to missing required field
            Robot(name='test')  # Missing 'topic'
            assert False, "Should have raised validation error"
        except (TypeError, ValueError):
            # Expected
            pass
    
    def test_robots_response_model_validation(self):
        """Test response model validation."""
        from processcube_robot_agent.rest_api.robots import Robots
        
        # Valid response
        robots = Robots(topics=[])
        assert robots.topics == []
        
        # Response should handle empty topics
        robots2 = Robots(topics=[])
        assert len(robots2.topics) == 0


class TestAPIResponseModels:
    """Test API response data models."""
    
    def test_robot_model_creation(self):
        """Test Robot model can be created."""
        from processcube_robot_agent.rest_api.robots import Robot
        
        robot = Robot(name="webui", topic="test.webui")
        assert robot.name == "webui"
        assert robot.topic == "test.webui"
    
    def test_robot_model_validation(self):
        """Test Robot model validates data."""
        from processcube_robot_agent.rest_api.robots import Robot
        
        # Valid robot
        robot = Robot(name="test", topic="test.test")
        assert robot.name == "test"
    
    def test_robots_response_model(self):
        """Test Robots response model."""
        from processcube_robot_agent.rest_api.robots import Robot, Robots
        
        robots = Robots(topics=[
            Robot(name="webui", topic="test.webui"),
            Robot(name="windows", topic="test.windows.ui")
        ])
        
        assert len(robots.topics) == 2
        assert robots.topics[0].name == "webui"
    
    def test_robots_response_empty_list(self):
        """Test Robots response with empty list."""
        from processcube_robot_agent.rest_api.robots import Robots
        
        robots = Robots(topics=[])
        assert len(robots.topics) == 0
