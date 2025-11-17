"""Integration tests for external task handling.

Tests the integration between the robot agent and ProcessCube engine,
including external task subscription and execution.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Any, Dict

from tests.integration.mock_engine import MockProcessCubeEngine, MockExternalTaskClient


class TestExternalTaskSubscription:
    """Test external task subscription flow."""
    
    @pytest.mark.asyncio
    async def test_agent_can_subscribe_to_topics(self):
        """Test that agent can subscribe to external tasks."""
        mock_engine = MockProcessCubeEngine()
        await mock_engine.start()
        await mock_engine.connect_agent("http://localhost:42042")
        
        # Subscribe to topics
        await mock_engine.client.subscribe_to_external_task("test.webui")
        await mock_engine.client.subscribe_to_external_task("test.windows.ui")
        
        topics = mock_engine.get_subscribed_topics()
        assert "test.webui" in topics
        assert "test.windows.ui" in topics
        
        await mock_engine.stop()
    
    @pytest.mark.asyncio
    async def test_subscription_without_connection_fails(self):
        """Test that subscription fails without engine connection."""
        client = MockExternalTaskClient()
        
        with pytest.raises(RuntimeError, match="Not connected to engine"):
            await client.subscribe_to_external_task("test.topic")
    
    @pytest.mark.asyncio
    async def test_multiple_topic_subscriptions(self):
        """Test subscribing to multiple topics."""
        mock_engine = MockProcessCubeEngine()
        await mock_engine.start()
        await mock_engine.connect_agent("http://localhost:42042")
        
        topics = ["test.webui", "test.windows.ui", "test.custom"]
        for topic in topics:
            await mock_engine.client.subscribe_to_external_task(topic)
        
        subscribed = mock_engine.get_subscribed_topics()
        assert len(subscribed) == 3
        assert all(t in subscribed for t in topics)
        
        await mock_engine.stop()
    
    @pytest.mark.asyncio
    async def test_subscription_count(self):
        """Test subscription counting."""
        mock_engine = MockProcessCubeEngine()
        await mock_engine.start()
        await mock_engine.connect_agent("http://localhost:42042")
        
        assert mock_engine.subscription_count() == 0
        
        await mock_engine.client.subscribe_to_external_task("test.topic1")
        assert mock_engine.subscription_count() == 1
        
        await mock_engine.client.subscribe_to_external_task("test.topic2")
        assert mock_engine.subscription_count() == 2
        
        await mock_engine.stop()


class TestExternalTaskExecution:
    """Test external task execution."""
    
    @pytest.mark.asyncio
    async def test_execute_task_on_subscribed_topic(self):
        """Test executing task on subscribed topic."""
        mock_engine = MockProcessCubeEngine()
        await mock_engine.start()
        await mock_engine.connect_agent("http://localhost:42042")
        
        await mock_engine.client.subscribe_to_external_task("test.webui")
        
        payload = {"order_id": "TEST-001", "customer": "Acme Corp"}
        result = await mock_engine.execute_external_task("test.webui", payload)
        
        assert result is not None
        assert "success" in result or "result" in result
        
        await mock_engine.stop()
    
    @pytest.mark.asyncio
    async def test_execute_task_on_unsubscribed_topic_fails(self):
        """Test that executing task on unsubscribed topic fails."""
        mock_engine = MockProcessCubeEngine()
        await mock_engine.start()
        await mock_engine.connect_agent("http://localhost:42042")
        
        payload = {"order_id": "TEST-001"}
        
        with pytest.raises(ValueError, match="Not subscribed to topic"):
            await mock_engine.execute_external_task("test.unsubscribed", payload)
        
        await mock_engine.stop()
    
    @pytest.mark.asyncio
    async def test_task_payload_passed_correctly(self):
        """Test that payload is passed to task execution."""
        mock_engine = MockProcessCubeEngine()
        await mock_engine.start()
        await mock_engine.connect_agent("http://localhost:42042")
        
        # Setup handler that captures payload
        captured_payload = {}
        
        def capture_handler(payload):
            captured_payload.update(payload)
            return {"success": True}
        
        await mock_engine.client.subscribe_to_external_task(
            "test.topic",
            handler=capture_handler
        )
        
        test_payload = {
            "order_id": "TEST-123",
            "customer": "Test Customer",
            "items": [{"sku": "ITEM-001", "qty": 5}]
        }
        
        await mock_engine.execute_external_task("test.topic", test_payload)
        
        assert captured_payload == test_payload
        
        await mock_engine.stop()


class TestEngineConnectionManagement:
    """Test engine connection lifecycle."""
    
    @pytest.mark.asyncio
    async def test_agent_connects_to_engine(self):
        """Test that agent connects to engine."""
        mock_engine = MockProcessCubeEngine()
        await mock_engine.start()
        
        assert not mock_engine.is_agent_connected()
        
        await mock_engine.connect_agent("http://localhost:42042")
        
        assert mock_engine.is_agent_connected()
        
        await mock_engine.stop()
    
    @pytest.mark.asyncio
    async def test_agent_disconnects_from_engine(self):
        """Test that agent properly disconnects."""
        mock_engine = MockProcessCubeEngine()
        await mock_engine.start()
        await mock_engine.connect_agent("http://localhost:42042")
        
        assert mock_engine.is_agent_connected()
        
        await mock_engine.stop()
        
        assert not mock_engine.is_agent_connected()
    
    @pytest.mark.asyncio
    async def test_connection_error_handling(self):
        """Test handling of connection errors."""
        client = MockExternalTaskClient()
        
        # Simulate connection error
        error = Exception("Connection refused")
        client.error_on_connect = error
        
        with pytest.raises(Exception, match="Connection refused"):
            await client.connect("http://invalid:99999")
    
    @pytest.mark.asyncio
    async def test_reconnection_scenario(self):
        """Test reconnection after disconnect."""
        mock_engine = MockProcessCubeEngine()
        await mock_engine.start()
        
        # Initial connection
        await mock_engine.connect_agent("http://localhost:42042")
        assert mock_engine.is_agent_connected()
        
        # Disconnect
        await mock_engine.stop()
        assert not mock_engine.is_agent_connected()
        
        # Reconnect
        mock_engine2 = MockProcessCubeEngine()
        await mock_engine2.start()
        await mock_engine2.connect_agent("http://localhost:42042")
        assert mock_engine2.is_agent_connected()
        
        await mock_engine2.stop()


class TestTopicRegistration:
    """Test topic registration and management."""
    
    @pytest.mark.asyncio
    async def test_topics_with_prefix(self):
        """Test topic prefix handling."""
        mock_engine = MockProcessCubeEngine()
        await mock_engine.start()
        await mock_engine.connect_agent("http://localhost:42042")
        
        # Subscribe to topics with different prefixes
        await mock_engine.client.subscribe_to_external_task("rcc.webui")
        await mock_engine.client.subscribe_to_external_task("robot.windows.ui")
        
        topics = mock_engine.get_subscribed_topics()
        assert "rcc.webui" in topics
        assert "robot.windows.ui" in topics
        
        await mock_engine.stop()
    
    @pytest.mark.asyncio
    async def test_topics_with_nested_paths(self):
        """Test topics with nested directory paths."""
        mock_engine = MockProcessCubeEngine()
        await mock_engine.start()
        await mock_engine.connect_agent("http://localhost:42042")
        
        nested_topics = [
            "rcc.windows.ui",
            "rcc.some_dir.another",
            "rcc.deep.nested.path.topic"
        ]
        
        for topic in nested_topics:
            await mock_engine.client.subscribe_to_external_task(topic)
        
        subscribed = mock_engine.get_subscribed_topics()
        assert all(t in subscribed for t in nested_topics)
        
        await mock_engine.stop()
    
    @pytest.mark.asyncio
    async def test_duplicate_subscription_handling(self):
        """Test handling of duplicate topic subscriptions."""
        mock_engine = MockProcessCubeEngine()
        await mock_engine.start()
        await mock_engine.connect_agent("http://localhost:42042")
        
        # Subscribe to same topic twice
        await mock_engine.client.subscribe_to_external_task("test.topic")
        await mock_engine.client.subscribe_to_external_task("test.topic")
        
        # Should still have only one subscription
        topics = mock_engine.get_subscribed_topics()
        assert len(topics) == 1
        assert "test.topic" in topics
        
        await mock_engine.stop()


class TestExternalTaskErrorScenarios:
    """Test error scenarios in external task handling."""
    
    @pytest.mark.asyncio
    async def test_handler_error_handling(self):
        """Test that handler errors are handled."""
        mock_engine = MockProcessCubeEngine()
        await mock_engine.start()
        await mock_engine.connect_agent("http://localhost:42042")
        
        def error_handler(payload):
            raise ValueError("Handler error")
        
        await mock_engine.client.subscribe_to_external_task(
            "test.error",
            handler=error_handler
        )
        
        payload = {"data": "test"}
        
        with pytest.raises(ValueError):
            await mock_engine.execute_external_task("test.error", payload)
        
        await mock_engine.stop()
    
    @pytest.mark.asyncio
    async def test_engine_shutdown_handling(self):
        """Test handling of engine shutdown."""
        mock_engine = MockProcessCubeEngine()
        await mock_engine.start()
        await mock_engine.connect_agent("http://localhost:42042")
        await mock_engine.client.subscribe_to_external_task("test.topic")
        
        await mock_engine.stop()
        
        # After shutdown, connection should be lost
        assert not mock_engine.is_agent_connected()
        assert mock_engine.subscription_count() == 0
    
    @pytest.mark.asyncio
    async def test_invalid_payload_handling(self):
        """Test handling of invalid payloads."""
        mock_engine = MockProcessCubeEngine()
        await mock_engine.start()
        await mock_engine.connect_agent("http://localhost:42042")
        await mock_engine.client.subscribe_to_external_task("test.topic")
        
        # Execute with various payload types
        payloads = [
            {},
            {"key": "value"},
            {"nested": {"data": "value"}},
            {"array": [1, 2, 3]}
        ]
        
        for payload in payloads:
            result = await mock_engine.execute_external_task("test.topic", payload)
            assert result is not None
        
        await mock_engine.stop()
