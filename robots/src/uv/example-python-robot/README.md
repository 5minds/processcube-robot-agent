# Example Python Robot with UV

This is an example Python robot that demonstrates how to use UV for dependency management with the ProcessCube Robot Agent.

## Project Structure

```
example-python-robot/
├── pyproject.toml      # Project configuration and dependencies
├── main.py             # Robot entry point
└── README.md           # This file
```

## Setup for Development

### Prerequisites

- Python 3.11+
- UV (https://docs.astral.sh/uv/)

### Local Development

1. **Create a virtual environment:**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   uv pip install -r requirements.txt
   ```
   Or with pyproject.toml:
   ```bash
   uv pip install -e .
   ```

3. **Run the robot locally:**
   ```bash
   uv run python main.py
   ```

## How It Works

### Input

The robot expects input work items in the ProcessCube format (JSON files):

```json
[
  {
    "payload": {
      "example_key": "example_value"
    }
  }
]
```

### Processing

The `main.py` script:
1. Reads the input work item using `robocorp.workitems`
2. Processes the payload
3. Creates an output work item with the result

### Output

The robot writes output work items with the processing result:

```json
[
  {
    "payload": {
      "original_input": {...},
      "processed": true,
      "message": "...",
      "status": "completed"
    }
  }
]
```

## Dependencies

- **robocorp-workitems**: For handling ProcessCube work items

## Packaging with UV

When deployed via ProcessCube Robot Agent:

1. The robot is automatically found (via `pyproject.toml`)
2. Dependencies are installed using `uv pip install`
3. The robot runs with `uv run python main.py`
4. Work items are handled automatically via JSON files

## Integration with ProcessCube Robot Agent

The robot is automatically discovered and packaged when:
1. Files change in `robots/src/uv/` directory
2. ProjectWatcher detects the change
3. ProjectPacker creates a ZIP file with `uv.lock`
4. Robot is registered as an external task

## Troubleshooting

### UV not found
Ensure UV is installed and available in your PATH:
```bash
uv --version
```

### Dependencies not installing
Check that `pyproject.toml` has correct dependency syntax and `uv.lock` is created:
```bash
uv lock
```

### Work items not found
Ensure the robot is running in ProcessCube context with proper environment variables set:
- `RPA_WORKITEMS_ADAPTER`
- `RPA_INPUT_WORKITEM_PATH`
- `RPA_OUTPUT_WORKITEM_PATH`
