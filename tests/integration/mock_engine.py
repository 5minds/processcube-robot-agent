"""Mock ProcessCube Engine for integration testing.

This module provides a mock implementation of the ProcessCube Engine
that simulates external task subscription and callback behavior.
"""

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ExternalTaskSubscription:
    """Represents an external task subscription."""
    topic: str
    timestamp: datetime = field(default_factory=datetime.now)
    callbacks: List[Callable] = field(default_factory=list)


@dataclass
class MockExternalTaskClient:
    """Mock implementation of ProcessCube external task client."""
    
    subscriptions: Dict[str, ExternalTaskSubscription] = field(default_factory=dict)
    connected: bool = False
    engine_url: str = ""
    error_on_connect: Optional[Exception] = None
    
    async def connect(self, engine_url: str) -> None:
        """Simulate connection to ProcessCube engine."""
        self.engine_url = engine_url
        
        if self.error_on_connect:
            raise self.error_on_connect
        
        self.connected = True
        logger.info(f"Mock engine connected to {engine_url}")
    
    async def subscribe_to_external_task(
        self, 
        topic: str, 
        handler: Optional[Callable] = None
    ) -> None:
        """Simulate external task subscription."""
        if not self.connected:
            raise RuntimeError("Not connected to engine")
        
        subscription = ExternalTaskSubscription(topic=topic)
        if handler:
            subscription.callbacks.append(handler)
        
        self.subscriptions[topic] = subscription
        logger.info(f"Subscribed to external task: {topic}")
    
    async def disconnect(self) -> None:
        """Simulate disconnection from engine."""
        self.connected = False
        self.subscriptions.clear()
        logger.info("Mock engine disconnected")
    
    def get_subscribed_topics(self) -> List[str]:
        """Get list of all subscribed topics."""
        return list(self.subscriptions.keys())
    
    async def simulate_task_execution(
        self, 
        topic: str, 
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simulate executing an external task."""
        if topic not in self.subscriptions:
            raise ValueError(f"Not subscribed to topic: {topic}")
        
        subscription = self.subscriptions[topic]
        
        # Call registered callbacks
        for callback in subscription.callbacks:
            result = callback(payload)
            if isinstance(result, dict):
                return result
        
        return {"success": True, "result": payload}


class MockProcessCubeEngine:
    """Mock ProcessCube Engine server for testing."""
    
    def __init__(self, host: str = "localhost", port: int = 56100):
        """Initialize mock engine.
        
        Args:
            host: Engine host
            port: Engine port
        """
        self.host = host
        self.port = port
        self.url = f"http://{host}:{port}"
        self.client = MockExternalTaskClient()
        self.is_running = False
    
    async def start(self) -> None:
        """Start the mock engine."""
        self.is_running = True
        logger.info(f"Mock ProcessCube Engine started on {self.url}")
    
    async def stop(self) -> None:
        """Stop the mock engine."""
        await self.client.disconnect()
        self.is_running = False
        logger.info("Mock ProcessCube Engine stopped")
    
    async def connect_agent(self, agent_url: str) -> None:
        """Simulate agent connecting to engine.
        
        Args:
            agent_url: URL of the robot agent
        """
        await self.client.connect(self.url)
        logger.info(f"Agent connected from {agent_url}")
    
    def get_subscribed_topics(self) -> List[str]:
        """Get topics subscribed by the agent."""
        return self.client.get_subscribed_topics()
    
    async def execute_external_task(
        self, 
        topic: str, 
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute an external task.
        
        Args:
            topic: Task topic
            payload: Task payload
            
        Returns:
            Task execution result
        """
        return await self.client.simulate_task_execution(topic, payload)
    
    def is_agent_connected(self) -> bool:
        """Check if agent is connected."""
        return self.client.connected
    
    def subscription_count(self) -> int:
        """Get number of subscribed topics."""
        return len(self.client.subscriptions)
