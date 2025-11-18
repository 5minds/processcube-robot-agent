# ProcessCube Robot Agent Tools Library Guide

The `processcube_robot_agent.tools` package provides reusable, well-tested utilities for building ProcessCube robots. This guide shows how to use them to dramatically simplify robot development.

## Overview

The tools library consists of four main components:

1. **RobotFrameworkExecutor** - Execute *.robot files from Python
2. **process_work_items()** - Standard work item processing framework
3. **Error handlers** - FunctionalError utilities for proper error signaling
4. **Built-in tests** - Comprehensive test suite for all tools

## Installation

The tools are part of `processcube_robot_agent` and are automatically available:

```python
from processcube_robot_agent.tools import (
    RobotFrameworkExecutor,
    process_work_items,
    raise_robot_test_failed,
    raise_robot_execution_error,
    raise_functional_error,
)
```

## Quick Start: Basic Robot Template

Here's the minimal setup for a UV-based robot:

```python
"""My Simple Robot"""
import logging
from processcube_robot_agent.tools import process_work_items

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_task(payload):
    """Process a work item."""
    logger.info(f"Processing: {payload}")
    
    # Your business logic here
    result = {"status": "success", "processed": payload}
    
    return result


if __name__ == "__main__":
    process_work_items(process_task)
```

That's it! No need for:
- Manually handling `inputs` and `outputs`
- Try/except blocks for work item iteration
- Error output creation
- FunctionalError integration

## Using RobotFrameworkExecutor

Execute *.robot files from within your Python robot:

```python
"""Robot that executes Robot Framework tests"""
import logging
from processcube_robot_agent.tools import (
    RobotFrameworkExecutor,
    process_work_items,
    raise_robot_test_failed,
    raise_robot_execution_error,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

executor = RobotFrameworkExecutor()


def process_robot_task(payload):
    """Execute a robot file with variables and tags."""
    robot_file = payload.get("robot_file", "tests/example.robot")
    variables = payload.get("variables", {})
    tags = payload.get("tags")
    
    logger.info(f"Executing: {robot_file}")
    
    # Execute the robot file
    result = executor.execute(
        robot_file=robot_file,
        variables=variables,
        tags=tags
    )
    
    # Signal failures to ProcessCube
    if result["status"] == "fail":
        raise_robot_test_failed(robot_file, result["return_code"])
    elif result["status"] == "error":
        raise_robot_execution_error(result.get("error"), robot_file)
    
    return result


if __name__ == "__main__":
    process_work_items(process_robot_task)
```

### RobotFrameworkExecutor API

```python
executor = RobotFrameworkExecutor()

result = executor.execute(
    robot_file="tests/example.robot",           # Required
    variables={"user": "admin"},                # Optional
    tags=["smoke", "critical"],                 # Optional
    suite_name="My Test Suite"                  # Optional
)

# Result structure:
# {
#     "status": "pass|fail|error",
#     "return_code": <int>,
#     "output_xml": <xml_string>,              # If available
#     "log_html_path": <path>,                 # If available
#     "report_html_path": <path>,              # If available
#     "statistics": {"total": "1", "passed": "1", "failed": "0"},
#     "stdout": <output>,
#     "stderr": <errors>
# }
```

## Error Handling

### Automatic Work Item Processing

The `process_work_items()` function handles all error scenarios:

```python
from processcube_robot_agent.tools import process_work_items
from processcube_sdk.external_tasks import FunctionalError


def processor(payload):
    if not payload.get("required_field"):
        # Raise FunctionalError for business logic failures
        raise FunctionalError("MISSING_FIELD", "required_field is required")
    
    # Regular exceptions are logged and skipped
    result = process_data(payload)
    
    return result


if __name__ == "__main__":
    # FunctionalError is re-raised to signal ProcessCube
    # Regular exceptions are logged, error output is created, processing continues
    process_work_items(processor)
```

### Custom Error Functions

```python
from processcube_robot_agent.tools import (
    raise_robot_test_failed,      # For test failures
    raise_robot_execution_error,  # For execution errors
    raise_functional_error,       # For custom errors
)

# Example: Test failure
result = executor.execute("tests/validation.robot")
if result["status"] == "fail":
    raise_robot_test_failed("tests/validation.robot", result["return_code"])

# Example: Execution error
if result["status"] == "error":
    raise_robot_execution_error("Robot not found", "tests/validation.robot")

# Example: Custom domain error
if not api_available:
    raise_functional_error("API_UNAVAILABLE", "External API is not responding")
```

## Real-World Examples

### Example 1: Hybrid Robot (API + Tests)

```python
"""Robot that validates data via API then runs tests"""
import logging
from processcube_robot_agent.tools import (
    RobotFrameworkExecutor,
    process_work_items,
    raise_robot_test_failed,
    raise_functional_error,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

executor = RobotFrameworkExecutor()


def process_data_validation(payload):
    """Validate via API, then run Robot Framework tests."""
    user_id = payload.get("user_id")
    
    # Step 1: API validation
    logger.info(f"Validating user {user_id} via API...")
    user_data = call_api(f"/users/{user_id}")
    
    if not user_data:
        raise_functional_error("USER_NOT_FOUND", f"User {user_id} not found")
    
    # Step 2: Run Robot Framework tests with API data
    logger.info(f"Running validation tests for user {user_id}...")
    result = executor.execute(
        robot_file="tests/user_validation.robot",
        variables={
            "user_id": user_id,
            "api_response": user_data
        },
        tags=["validation"]
    )
    
    if result["status"] == "fail":
        raise_robot_test_failed(
            "tests/user_validation.robot",
            result["return_code"],
            f"User {user_id} failed validation"
        )
    
    return {
        "status": "success",
        "user_id": user_id,
        "test_results": result
    }


def call_api(endpoint):
    # Implementation here
    pass


if __name__ == "__main__":
    process_work_items(process_data_validation)
```

### Example 2: Batch Processing Robot

```python
"""Robot that processes items with error recovery"""
import logging
from processcube_robot_agent.tools import (
    process_work_items,
    raise_functional_error,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_batch_items(payload):
    """Process multiple items with error recovery."""
    items = payload.get("items", [])
    
    if not items:
        raise_functional_error("EMPTY_BATCH", "No items to process")
    
    results = []
    for item in items:
        try:
            logger.info(f"Processing item: {item}")
            result = process_single_item(item)
            results.append({"item": item, "status": "success", "result": result})
        except Exception as e:
            # Log but continue processing other items
            logger.error(f"Failed to process {item}: {e}")
            results.append({"item": item, "status": "error", "error": str(e)})
    
    return {
        "total": len(items),
        "results": results
    }


def process_single_item(item):
    # Implementation here
    pass


if __name__ == "__main__":
    process_work_items(process_batch_items)
```

## Testing Your Robot

The tools library comes with comprehensive tests. Use them as a reference:

```bash
# Run all tools tests
pytest tests/test_tools_*.py -v

# Run specific test
pytest tests/test_tools_robot_executor.py -v
```

Example test structure for your robot:

```python
"""Tests for my robot"""
from unittest.mock import patch, MagicMock
import pytest
from processcube_sdk.external_tasks import FunctionalError
from myrobot import process_data_validation


@patch('myrobot.call_api')
def test_successful_validation(mock_api):
    """Test successful validation flow."""
    mock_api.return_value = {"id": 1, "name": "Test User"}
    
    result = process_data_validation({"user_id": 1})
    
    assert result["status"] == "success"
    assert result["user_id"] == 1


@patch('myrobot.call_api')
def test_missing_user(mock_api):
    """Test handling of missing user."""
    mock_api.return_value = None
    
    with pytest.raises(FunctionalError) as exc_info:
        process_data_validation({"user_id": 999})
    
    assert exc_info.value.get_code() == "USER_NOT_FOUND"
```

## Best Practices

### 1. Always Use process_work_items()

Instead of manually handling work items:

```python
# ❌ Don't do this
from robocorp.workitems import inputs, outputs

for input_item in inputs:
    try:
        # ... complex try/except logic
    except Exception as e:
        # ... error handling
```

Use the framework:

```python
# ✅ Do this
from processcube_robot_agent.tools import process_work_items

def processor(payload):
    return {"result": "success"}

if __name__ == "__main__":
    process_work_items(processor)
```

### 2. Raise FunctionalError for Business Logic Failures

```python
# ❌ Don't return error status
def processor(payload):
    if validation_fails:
        return {"status": "error", "message": "Validation failed"}

# ✅ Do raise FunctionalError
def processor(payload):
    if validation_fails:
        raise FunctionalError("VALIDATION_FAILED", "Validation failed")
```

### 3. Use Specific Error Codes

```python
# ✅ Use semantic error codes
raise_functional_error("API_TIMEOUT", "API request timed out")
raise_functional_error("INVALID_INPUT", "Missing required field: user_id")
raise_functional_error("DATABASE_ERROR", "Failed to connect to database")
```

### 4. Reuse Executors

```python
# ✅ Create executor once, reuse multiple times
executor = RobotFrameworkExecutor()

def processor(payload):
    result1 = executor.execute("tests/setup.robot")
    result2 = executor.execute("tests/main.robot")
    result3 = executor.execute("tests/cleanup.robot")
    return {"results": [result1, result2, result3]}
```

## Troubleshooting

### FunctionalError Not Being Caught

Make sure you're importing from the tools:

```python
# ✅ Correct
from processcube_robot_agent.tools import raise_robot_test_failed

# ❌ Wrong
from processcube_sdk.external_tasks import raise_robot_test_failed  # Doesn't exist
```

### Work Items Not Processing

Ensure `process_work_items()` is called in the `main` block:

```python
if __name__ == "__main__":
    process_work_items(processor)
```

### Robot File Not Found

Always check file paths - they're relative to the robot's working directory:

```python
import logging
logger = logging.getLogger(__name__)

# Use absolute paths for clarity
from pathlib import Path

robot_dir = Path(__file__).parent
result = executor.execute(str(robot_dir / "tests" / "example.robot"))
```

## API Reference

### process_work_items(processor)

Process all input work items with the provided processor function.

**Parameters:**
- `processor`: Callable that takes payload dict and returns result dict

**Behavior:**
- Reads all input work items
- Calls processor for each item
- Creates output work item with result
- FunctionalError is re-raised to signal ProcessCube
- Other exceptions are logged, error output created, processing continues

### RobotFrameworkExecutor.execute(robot_file, variables, tags, suite_name)

Execute a Robot Framework file.

**Parameters:**
- `robot_file` (str): Path to *.robot file
- `variables` (dict, optional): Variables to pass to Robot Framework
- `tags` (list, optional): Tags to include (--include)
- `suite_name` (str, optional): Suite name (--name)

**Returns:** Dict with execution results and reports

**Raises:** No exceptions - errors are returned in the result dict

### Error Functions

- `raise_robot_test_failed(robot_file, return_code, details="")`
- `raise_robot_execution_error(error, robot_file="")`
- `raise_functional_error(code, message)`

All raise `FunctionalError` to signal ProcessCube.

## Contributing

Found a bug or have an idea? The tools library has comprehensive tests:

```bash
pytest tests/test_tools_*.py -v --cov=processcube_robot_agent.tools
```

---

**Last Updated:** November 2025
**Tools Library Version:** 1.0
