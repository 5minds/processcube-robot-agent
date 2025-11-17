"""Health check endpoints for monitoring and kubernetes probes.

Provides health status information for:
- Liveness probe (is the service running?)
- Readiness probe (is the service ready to receive traffic?)
- Detailed health endpoint with component status
"""

import logging
from datetime import datetime
from typing import Dict, Any
from enum import Enum

from fastapi import APIRouter, HTTPException

logger = logging.getLogger("processcube_robot_agent")

router = APIRouter(prefix="/health", tags=["health"])


class HealthStatus(str, Enum):
    """Health status values."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ComponentHealth:
    """Tracks health of individual components."""
    
    def __init__(self, name: str):
        self.name = name
        self.is_healthy = True
        self.last_error: str | None = None
        self.check_count = 0
        self.error_count = 0
    
    def mark_healthy(self) -> None:
        """Mark component as healthy."""
        self.is_healthy = True
        self.last_error = None
        self.check_count += 1
    
    def mark_unhealthy(self, error: str) -> None:
        """Mark component as unhealthy."""
        self.is_healthy = False
        self.last_error = error
        self.check_count += 1
        self.error_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "status": "healthy" if self.is_healthy else "unhealthy",
            "last_error": self.last_error,
            "check_count": self.check_count,
            "error_count": self.error_count
        }


class HealthChecker:
    """Central health checker for all components."""
    
    def __init__(self):
        self.components: Dict[str, ComponentHealth] = {
            "api": ComponentHealth("api"),
            "engine_connection": ComponentHealth("engine_connection"),
            "robot_registry": ComponentHealth("robot_registry"),
        }
        self.startup_time = datetime.now()
    
    def get_component(self, name: str) -> ComponentHealth:
        """Get or create component health tracker."""
        if name not in self.components:
            self.components[name] = ComponentHealth(name)
        return self.components[name]
    
    def is_healthy(self) -> bool:
        """Check if all components are healthy."""
        return all(c.is_healthy for c in self.components.values())
    
    def is_ready(self) -> bool:
        """Check if service is ready to receive traffic."""
        # API must be healthy
        # Engine connection should be healthy (but service can start without it)
        api_healthy = self.components["api"].is_healthy
        engine_healthy = self.components["engine_connection"].is_healthy
        
        return api_healthy and engine_healthy
    
    def get_status(self) -> Dict[str, Any]:
        """Get overall health status."""
        uptime_seconds = (datetime.now() - self.startup_time).total_seconds()
        
        return {
            "status": self._determine_status(),
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": uptime_seconds,
            "components": {
                name: component.to_dict()
                for name, component in self.components.items()
            }
        }
    
    def _determine_status(self) -> str:
        """Determine overall status from components."""
        if self.is_healthy():
            return HealthStatus.HEALTHY
        
        # If most components are healthy, it's degraded
        healthy_count = sum(1 for c in self.components.values() if c.is_healthy)
        if healthy_count > len(self.components) / 2:
            return HealthStatus.DEGRADED
        
        return HealthStatus.UNHEALTHY


# Global health checker instance
_health_checker = HealthChecker()


def get_health_checker() -> HealthChecker:
    """Get the global health checker instance."""
    return _health_checker


@router.get("")
async def health_check() -> Dict[str, Any]:
    """General health check endpoint.
    
    Returns:
        - status: Overall health status
        - timestamp: Current timestamp
        - uptime_seconds: Service uptime in seconds
        - components: Status of individual components
    
    Returns 200 if healthy, 503 if unhealthy.
    """
    checker = get_health_checker()
    status = checker.get_status()
    
    if status["status"] == HealthStatus.UNHEALTHY:
        raise HTTPException(
            status_code=503,
            detail="Service unhealthy"
        )
    
    return status


@router.get("/live")
async def liveness_probe() -> Dict[str, str]:
    """Liveness probe for Kubernetes.
    
    Indicates whether the container should be restarted.
    Returns 200 if the service is running.
    
    Returns:
        - status: "alive" if service is running
    """
    checker = get_health_checker()
    
    # Simple check: API component is initialized
    if not checker.components["api"].is_healthy:
        raise HTTPException(
            status_code=503,
            detail="Service not running"
        )
    
    return {"status": "alive"}


@router.get("/ready")
async def readiness_probe() -> Dict[str, str]:
    """Readiness probe for Kubernetes.
    
    Indicates whether the service is ready to receive traffic.
    Returns 200 if the service is ready.
    
    Returns:
        - status: "ready" if service is ready
    """
    checker = get_health_checker()
    
    if not checker.is_ready():
        raise HTTPException(
            status_code=503,
            detail="Service not ready"
        )
    
    return {"status": "ready"}


@router.get("/startup")
async def startup_check() -> Dict[str, Any]:
    """Startup probe for Kubernetes.
    
    Indicates whether the application has started.
    Returns 200 once the service is initialized.
    
    Returns:
        - status: "started" if initialization complete
        - startup_time: When the service started
        - duration_seconds: How long initialization took
    """
    checker = get_health_checker()
    
    if not checker.components["api"].is_healthy:
        raise HTTPException(
            status_code=503,
            detail="Still starting up"
        )
    
    duration = (datetime.now() - checker.startup_time).total_seconds()
    
    return {
        "status": "started",
        "startup_time": checker.startup_time.isoformat(),
        "duration_seconds": duration
    }
