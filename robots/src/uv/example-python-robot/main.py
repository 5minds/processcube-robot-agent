"""Example Python Robot using UV and RPA Framework Work Items.

This robot demonstrates:
- Reading input work items
- Processing data
- Writing output work items
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict

from robocorp.workitems import inputs, outputs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def process_robot_task(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process the input data and return output.

    Args:
        input_data: Input payload from work items

    Returns:
        Dictionary with processing result
    """
    logger.info(f"Processing input: {input_data}")

    # Example processing: add a processed flag and timestamp
    output = {
        "original_input": input_data,
        "processed": True,
        "message": f"Successfully processed robot task with input: {input_data}",
        "status": "completed"
    }

    logger.info(f"Output data: {output}")
    return output


def main():
    """Main entry point for the robot.

    Reads input work items, processes them, and writes output work items.
    """
    logger.info("Starting example Python robot")

    try:
        # Get input work items
        logger.info("Reading input work items...")

        # In robocorp.workitems >= 1.0, iterate through inputs
        for input_item in inputs:
            input_payload = input_item.payload
            logger.info(f"Received input payload: {input_payload}")

            # Process the input
            output_payload = process_robot_task(input_payload)

            # Send output work item
            logger.info("Writing output work items...")
            output_item = outputs.create(output_payload)
            output_item.save()

        logger.info("Robot execution completed successfully")

    except Exception as e:
        logger.error(f"Error during robot execution: {e}", exc_info=True)
        # Optionally create error output
        error_output = {
            "error": str(e),
            "status": "failed"
        }
        try:
            output_item = outputs.create(error_output)
            output_item.save()
        except Exception as output_error:
            logger.error(f"Failed to write error output: {output_error}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
