"""Prometheus metrics exporter for monitoring.

Exposes metrics in Prometheus format at /metrics endpoint.
"""

import logging
from datetime import datetime
from typing import Dict, Any
from enum import Enum

from fastapi import APIRouter

logger = logging.getLogger("processcube_robot_agent")

router = APIRouter(prefix="/metrics", tags=["metrics"])


class MetricType(str, Enum):
    """Prometheus metric types."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class Metric:
    """Base metric class."""
    
    def __init__(self, name: str, help_text: str, metric_type: MetricType):
        self.name = name
        self.help_text = help_text
        self.metric_type = metric_type
        self.labels: Dict[str, Any] = {}
    
    def to_prometheus_line(self) -> str:
        """Convert to Prometheus format line."""
        raise NotImplementedError


class Counter(Metric):
    """Counter metric (monotonically increasing)."""
    
    def __init__(self, name: str, help_text: str):
        super().__init__(name, help_text, MetricType.COUNTER)
        self.value = 0
    
    def increment(self, amount: float = 1) -> None:
        """Increment the counter."""
        self.value += amount
    
    def to_prometheus_line(self) -> str:
        """Convert to Prometheus format."""
        labels_str = ",".join(f'{k}="{v}"' for k, v in self.labels.items())
        if labels_str:
            return f'{self.name}{{{labels_str}}} {self.value}'
        return f'{self.name} {self.value}'


class Gauge(Metric):
    """Gauge metric (can increase or decrease)."""
    
    def __init__(self, name: str, help_text: str):
        super().__init__(name, help_text, MetricType.GAUGE)
        self.value = 0
    
    def set(self, value: float) -> None:
        """Set the gauge value."""
        self.value = value
    
    def increment(self, amount: float = 1) -> None:
        """Increment the gauge."""
        self.value += amount
    
    def decrement(self, amount: float = 1) -> None:
        """Decrement the gauge."""
        self.value -= amount
    
    def to_prometheus_line(self) -> str:
        """Convert to Prometheus format."""
        labels_str = ",".join(f'{k}="{v}"' for k, v in self.labels.items())
        if labels_str:
            return f'{self.name}{{{labels_str}}} {self.value}'
        return f'{self.name} {self.value}'


class MetricsCollector:
    """Collects and exposes metrics."""
    
    def __init__(self):
        """Initialize metrics collector."""
        # Request metrics
        self.requests_total = Counter(
            "processcube_robot_agent_requests_total",
            "Total HTTP requests"
        )
        self.request_duration_seconds = Gauge(
            "processcube_robot_agent_request_duration_seconds",
            "HTTP request duration in seconds"
        )
        
        # Robot execution metrics
        self.robot_executions_total = Counter(
            "processcube_robot_agent_robot_executions_total",
            "Total robot executions"
        )
        self.robot_execution_duration_seconds = Gauge(
            "processcube_robot_agent_robot_execution_duration_seconds",
            "Robot execution duration in seconds"
        )
        self.robot_execution_errors_total = Counter(
            "processcube_robot_agent_robot_execution_errors_total",
            "Total robot execution errors"
        )
        
        # External task metrics
        self.external_tasks_total = Counter(
            "processcube_robot_agent_external_tasks_total",
            "Total external tasks received"
        )
        self.external_tasks_completed = Counter(
            "processcube_robot_agent_external_tasks_completed",
            "Total external tasks completed"
        )
        self.external_tasks_failed = Counter(
            "processcube_robot_agent_external_tasks_failed",
            "Total external tasks failed"
        )
        
        # Engine connection metrics
        self.engine_connection_status = Gauge(
            "processcube_robot_agent_engine_connection_status",
            "Engine connection status (1=connected, 0=disconnected)"
        )
        self.engine_reconnection_attempts_total = Counter(
            "processcube_robot_agent_engine_reconnection_attempts_total",
            "Total engine reconnection attempts"
        )
        
        # Registered robots
        self.robots_registered = Gauge(
            "processcube_robot_agent_robots_registered",
            "Number of registered robots"
        )
        
        # Uptime
        self.uptime_seconds = Gauge(
            "processcube_robot_agent_uptime_seconds",
            "Service uptime in seconds"
        )
        
        self.startup_time = datetime.now()
    
    def update_uptime(self) -> None:
        """Update uptime metric."""
        uptime = (datetime.now() - self.startup_time).total_seconds()
        self.uptime_seconds.set(uptime)
    
    def to_prometheus_format(self) -> str:
        """Generate Prometheus format output.
        
        Returns:
            Metrics in Prometheus exposition format
        """
        self.update_uptime()
        
        lines = [
            "# HELP processcube_robot_agent_requests_total Total HTTP requests",
            "# TYPE processcube_robot_agent_requests_total counter",
            f"processcube_robot_agent_requests_total {self.requests_total.value}",
            "",
            "# HELP processcube_robot_agent_robot_executions_total Total robot executions",
            "# TYPE processcube_robot_agent_robot_executions_total counter",
            f"processcube_robot_agent_robot_executions_total {self.robot_executions_total.value}",
            "",
            "# HELP processcube_robot_agent_robot_execution_errors_total Total robot execution errors",
            "# TYPE processcube_robot_agent_robot_execution_errors_total counter",
            f"processcube_robot_agent_robot_execution_errors_total {self.robot_execution_errors_total.value}",
            "",
            "# HELP processcube_robot_agent_external_tasks_total Total external tasks received",
            "# TYPE processcube_robot_agent_external_tasks_total counter",
            f"processcube_robot_agent_external_tasks_total {self.external_tasks_total.value}",
            "",
            "# HELP processcube_robot_agent_external_tasks_completed Total external tasks completed",
            "# TYPE processcube_robot_agent_external_tasks_completed counter",
            f"processcube_robot_agent_external_tasks_completed {self.external_tasks_completed.value}",
            "",
            "# HELP processcube_robot_agent_external_tasks_failed Total external tasks failed",
            "# TYPE processcube_robot_agent_external_tasks_failed counter",
            f"processcube_robot_agent_external_tasks_failed {self.external_tasks_failed.value}",
            "",
            "# HELP processcube_robot_agent_engine_connection_status Engine connection status",
            "# TYPE processcube_robot_agent_engine_connection_status gauge",
            f"processcube_robot_agent_engine_connection_status {self.engine_connection_status.value}",
            "",
            "# HELP processcube_robot_agent_robots_registered Number of registered robots",
            "# TYPE processcube_robot_agent_robots_registered gauge",
            f"processcube_robot_agent_robots_registered {self.robots_registered.value}",
            "",
            "# HELP processcube_robot_agent_uptime_seconds Service uptime in seconds",
            "# TYPE processcube_robot_agent_uptime_seconds gauge",
            f"processcube_robot_agent_uptime_seconds {self.uptime_seconds.value}",
        ]
        
        return "\n".join(lines)


# Global metrics instance
_metrics = MetricsCollector()


def get_metrics() -> MetricsCollector:
    """Get the global metrics collector."""
    return _metrics


@router.get("")
async def metrics() -> str:
    """Export metrics in Prometheus format.
    
    Returns:
        Metrics in Prometheus exposition format
    """
    return get_metrics().to_prometheus_format()


@router.get("/summary")
async def metrics_summary() -> Dict[str, Any]:
    """Get a summary of key metrics.
    
    Returns:
        Dictionary with key metrics
    """
    metrics = get_metrics()
    
    return {
        "requests_total": metrics.requests_total.value,
        "robot_executions_total": metrics.robot_executions_total.value,
        "robot_execution_errors_total": metrics.robot_execution_errors_total.value,
        "external_tasks_total": metrics.external_tasks_total.value,
        "external_tasks_completed": metrics.external_tasks_completed.value,
        "external_tasks_failed": metrics.external_tasks_failed.value,
        "engine_connected": bool(metrics.engine_connection_status.value),
        "robots_registered": metrics.robots_registered.value,
        "uptime_seconds": metrics.uptime_seconds.value,
    }
