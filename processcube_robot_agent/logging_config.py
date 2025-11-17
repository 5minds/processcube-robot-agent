"""Structured logging configuration with JSON output.

Provides JSON formatted logging for production environments
and readable logging for development.
"""

import json
import logging
import sys
import os
from datetime import datetime
from typing import Any, Dict
from logging import LogRecord


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: LogRecord) -> str:
        """Format log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON formatted log line
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
        
        # Add extra fields if present
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        return json.dumps(log_data)


class DevFormatter(logging.Formatter):
    """Human-readable formatter for development."""
    
    def format(self, record: LogRecord) -> str:
        """Format log record for human readability.
        
        Args:
            record: Log record to format
            
        Returns:
            Formatted log line
        """
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        level = record.levelname.ljust(8)
        logger = record.name.ljust(30)
        message = record.getMessage()
        
        log_line = f"{timestamp} | {level} | {logger} | {message}"
        
        if record.exc_info:
            log_line += f"\n{self.formatException(record.exc_info)}"
        
        return log_line


def setup_logging(env: str = "dev") -> None:
    """Set up logging configuration.
    
    Args:
        env: Environment ("dev" or "prod")
    """
    # Get log level from environment
    log_level_str = os.environ.get("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    
    # Get format preference
    log_format = os.environ.get("LOG_FORMAT", "dev" if env == "dev" else "json").lower()
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Set formatter based on format preference
    if log_format == "json":
        formatter = JSONFormatter()
    else:
        formatter = DevFormatter()
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if log directory exists)
    log_dir = "/var/log/processcube-robot-agent"
    if os.path.isdir(log_dir):
        try:
            file_handler = logging.FileHandler(
                f"{log_dir}/agent.log",
                encoding="utf-8"
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except (IOError, OSError):
            # If we can't write to log file, just use console
            pass
    
    # Set specific loggers to avoid spam
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("asyncio").setLevel(logging.INFO)


class CorrelationIdFilter(logging.Filter):
    """Add correlation ID to log records for request tracing."""
    
    def __init__(self):
        super().__init__()
        self.correlation_id = None
    
    def filter(self, record: LogRecord) -> bool:
        """Add correlation ID to log record.
        
        Args:
            record: Log record
            
        Returns:
            True to allow the record to be logged
        """
        if not hasattr(record, "extra"):
            record.extra = {}
        
        if self.correlation_id:
            record.extra["correlation_id"] = self.correlation_id
        
        return True
    
    def set_correlation_id(self, correlation_id: str) -> None:
        """Set correlation ID for subsequent logs.
        
        Args:
            correlation_id: Unique request ID
        """
        self.correlation_id = correlation_id


# Global correlation ID filter
_correlation_id_filter = CorrelationIdFilter()


def get_correlation_id_filter() -> CorrelationIdFilter:
    """Get the global correlation ID filter."""
    return _correlation_id_filter
