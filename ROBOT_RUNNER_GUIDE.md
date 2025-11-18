# Robot Runner Guide - Execute Robot Framework Files Without main.py

**robot_runner** is a standalone CLI tool that lets you execute Robot Framework files in ProcessCube without needing a `main.py` wrapper. Just define your `.robot` files and configure them in `pyproject.toml`.

## Quick Start

### 1. Create Your Robot Package

```bash
mkdir my-robot
cd my-robot
```

### 2. Create pyproject.toml

```toml
[project]
name = "my-robot"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "robotframework>=7.0",
    "rpaframework>=31.0",
    "robocorp-workitems>=1.0.0",
]

# Define the robot_runner entry point
[project.scripts]
robot_runner = "processcube_robot_agent.tools.robot_runner:main"

# Optional: Set default robot file
[tool.processcube]
robot_file = "test_automation.robot"
```

### 3. Create Your Robot File

```robot
# test_automation.robot
*** Test Cases ***
Example Test
    Log    Running test with ProcessCube
    Sleep    1s
    Log    Done!
```

### 4. Pack and Execute

```bash
# Pack the robot
zip -r my-robot.zip .

# ProcessCube will automatically detect the entry point and execute it!
```

That's it! No `main.py` needed.

---

## CLI Usage

### Basic Execution

```bash
# If you have [tool.processcube] robot_file configured:
robot_runner

# Or specify robot file explicitly:
robot_runner my_robot.robot
```

### With Variables

Pass variables to your Robot Framework tests:

```bash
robot_runner my_robot.robot \
    --variable USERNAME=admin \
    --variable PASSWORD=secret123
```

In your robot file:

```robot
*** Test Cases ***
Login Test
    Log    Username: ${USERNAME}
    Log    Password: ${PASSWORD}
```

### With Tags

Filter test execution by tags:

```bash
robot_runner my_robot.robot --tag smoke --tag critical
```

In your robot file:

```robot
*** Test Cases ***
Smoke Test
    [Tags]    smoke
    Log    This is a smoke test

Integration Test
    [Tags]    integration
    Log    This is an integration test

Critical Test
    [Tags]    critical
    Log    This is critical
```

Execute only smoke tests:

```bash
robot_runner my_robot.robot --tag smoke
```

### Help

```bash
robot_runner --help
```

---

## Comparison: Old vs New

### Old Way (Still Supported)

```python
# main.py - boilerplate required
from processcube_robot_agent.tools import (
    RobotFrameworkExecutor,
    process_work_items,
    raise_robot_test_failed,
)

executor = RobotFrameworkExecutor()

def process_robot_task(payload):
    robot_file = payload.get("robot_file", "example.robot")
    result = executor.execute(robot_file)
    
    if result["status"] == "fail":
        raise_robot_test_failed(robot_file, result["return_code"])
    
    return result

if __name__ == "__main__":
    process_work_items(process_robot_task)
```

### New Way (Recommended)

```toml
# pyproject.toml - that's all you need!
[project.scripts]
robot_runner = "processcube_robot_agent.tools.robot_runner:main"

[tool.processcube]
robot_file = "my_robot.robot"
```

---

## Advanced: Payload Overrides

Even with `robot_runner`, you can still pass data via ProcessCube work items. The payload can override configuration:

### Configuration

```toml
[tool.processcube]
robot_file = "default.robot"  # Default if not in payload
```

### Input Work Item

```json
{
    "robot_file": "custom.robot",
    "variables": {
        "USER": "john",
        "PASS": "secret"
    },
    "tags": ["smoke"]
}
```

### Robot File

```robot
*** Test Cases ***
Custom Test
    [Tags]    smoke
    Log    User: ${USER}
    Log    Pass: ${PASS}
```

The tool will use `custom.robot` instead of `default.robot` and apply the variables and tags from the payload.

---

## ProcessCube Integration

### Error Handling

When tests fail, the tool properly signals ProcessCube:

```robot
*** Test Cases ***
Test That Might Fail
    ${result}=    Run Keyword And Return Status    Should Be Equal    1    2
    Run Keyword If    not ${result}    Fail    Test failed as expected
```

If tests fail → `FunctionalError("ROBOT_TESTS_FAILED", ...)`  
If execution errors → `FunctionalError("ROBOT_EXECUTION_ERROR", ...)`

ProcessCube can catch these and route to error handlers.

### Work Items

The tool uses ProcessCube's work items system:

- **Input**: Reads from `RPA_WORKITEMS_PATH` (ProcessCube sets this)
- **Output**: Writes results to `RPA_OUTPUT_WORKITEM_PATH`
- **Payload**: Each work item contains your data

Example output:

```json
{
    "status": "pass",
    "return_code": 0,
    "output_xml": "<?xml version='1.0'?>...",
    "statistics": {
        "total": "5",
        "passed": "5",
        "failed": "0"
    }
}
```

---

## Best Practices

### 1. Keep It Simple

Don't add unnecessary complexity. `robot_runner` is designed for straightforward test execution.

```toml
[project.scripts]
robot_runner = "processcube_robot_agent.tools.robot_runner:main"

[tool.processcube]
robot_file = "tests.robot"
```

### 2. Use Meaningful Robot Names

```bash
# Good
validation_tests.robot
smoke_tests.robot
integration_tests.robot

# Bad
test.robot
robot1.robot
```

### 3. Organization with Tags

Use tags instead of multiple robot files:

```robot
*** Test Cases ***
Create User
    [Tags]    smoke    user
    Log    Creating user

Delete User
    [Tags]    integration    user
    Log    Deleting user

API Test
    [Tags]    integration    api
    Log    Testing API
```

Then execute with:

```bash
robot_runner --tag smoke       # Only smoke tests
robot_runner --tag user        # Only user-related tests
robot_runner --tag integration # Only integration tests
```

### 4. Leverage RPA Framework

The wrapper includes RPA Framework for advanced automation:

```robot
*** Settings ***
Library    RPA.Browser.Selenium
Library    RPA.Database
Library    RPA.Robocorp.WorkItems

*** Test Cases ***
Web Test
    Open Available Browser    https://example.com
    Close Browser

Database Test
    Connect To Database    ${DB_HOST}    ${DB_USER}    ${DB_PASS}
    @{result}=    Query    SELECT * FROM users
    Log    Found ${result} users
    Disconnect From Database
```

### 5. Handle Failures Properly

```robot
*** Test Cases ***
Test With Error Handling
    TRY
        Should Be Equal    1    2
    EXCEPT
        Log    Test failed but continuing
        # Optional: continue or fail
    END
```

---

## Troubleshooting

### Error: "Neither entry point found ... nor main.py found"

**Cause**: No `[project.scripts]` in pyproject.toml and no `main.py` file exists.

**Solution**: Add entry point to pyproject.toml:

```toml
[project.scripts]
robot_runner = "processcube_robot_agent.tools.robot_runner:main"
```

### Error: "No robot file specified"

**Cause**: No robot file in CLI args and no config in `[tool.processcube]`.

**Solution**: Either pass robot file as argument or add to config:

```toml
[tool.processcube]
robot_file = "my_robot.robot"
```

### Tests Not Executing

**Cause**: Tag or variable name issues.

**Solution**: Check Robot Framework syntax:

```bash
# List available tests and tags
robot --dryrun my_robot.robot

# Run specific tag
robot_runner my_robot.robot --tag smoke
```

### Variables Not Passed

**Cause**: Variable format issue.

**Solution**: Use KEY=VALUE format:

```bash
# Correct
robot_runner my_robot.robot --variable USER=admin

# Wrong
robot_runner my_robot.robot --variable USER admin
```

---

## Migration from main.py

If you have existing robots with `main.py`:

1. **Keep main.py** - It still works! No changes needed.

2. **Optional: Migrate gradually**
   ```bash
   # Add entry point to pyproject.toml
   [project.scripts]
   robot_runner = "processcube_robot_agent.tools.robot_runner:main"
   ```
   ProcessCube will automatically use entry point if available.

3. **Optional: Remove main.py** once you're confident with entry point mode.

---

## See Also

- [Tools Library Guide](./TOOLS_LIBRARY_GUIDE.md) - RobotFrameworkExecutor and process_work_items
- [UV Robot Creation Guide](./UV_ROBOT_CREATION_GUIDE.md) - Full UV robot development
- [Quick Start](./QUICK_START.md) - General setup instructions

---

**Last Updated**: November 2025  
**Status**: Production Ready
