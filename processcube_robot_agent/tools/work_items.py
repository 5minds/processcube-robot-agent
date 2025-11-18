"""Work Items processing framework for ProcessCube robots.

Provides a standardized way to handle input/output work items with proper
error handling, logging, and FunctionalError integration.

Usage:
    from processcube_robot_agent.tools import process_work_items
    from processcube_sdk.external_tasks import FunctionalError
    
    def process_robot_task(payload):
        # Your business logic here
        result = do_something(payload)
        return result
    
    if __name__ == "__main__":
        process_work_items(process_robot_task)
"""

import logging
from typing import Any, Callable, Dict

try:
    from robocorp.workitems import inputs, outputs
except ImportError:
    # robocorp.workitems is only available in UV robot environment
    inputs = None
    outputs = None

from processcube_sdk.external_tasks import FunctionalError

logger = logging.getLogger(__name__)


def process_work_items(processor: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
    """Process all input work items with standardized error handling.
    
    This is the main entry point for robots. It handles:
    - Reading input work items
    - Processing each item with the provided processor function
    - Writing output work items
    - Proper error handling and FunctionalError propagation
    - Detailed logging throughout the process
    
    Args:
        processor: Callable that takes payload dict and returns result dict.
                   Should raise FunctionalError for business logic failures.
    
    Example:
        def my_processor(payload):
            data = payload.get("data")
            if not data:
                raise FunctionalError("MISSING_DATA", "Data field is required")
            
            result = process_data(data)
            return {"status": "success", "result": result}
        
        if __name__ == "__main__":
            process_work_items(my_processor)
    """
    logger.info("Starting work item processor")
    
    try:
        logger.info("Reading input work items...")
        item_count = 0
        
        # Process all input work items
        for input_item in inputs:
            item_count += 1
            payload = input_item.payload
            logger.info(f"Processing work item {item_count}: {payload}")
            
            try:
                # Call the processor function
                logger.debug(f"Calling processor for item {item_count}...")
                result = processor(payload)
                
                # Create and save output work item
                logger.info("Creating output work item...")
                output_item = outputs.create(result)
                output_item.save()
                logger.info(f"Output saved for work item {item_count}")
                
            except FunctionalError:
                # FunctionalError should be re-raised to signal to ProcessCube
                logger.error(f"FunctionalError processing work item {item_count}", exc_info=True)
                # Save error output before re-raising
                error_output = {
                    "status": "error",
                    "error": str(FunctionalError),
                }
                try:
                    output_item = outputs.create(error_output)
                    output_item.save()
                except Exception as output_error:
                    logger.error(f"Failed to write error output: {output_error}", exc_info=True)
                # Re-raise to signal to ProcessCube
                raise
                
            except Exception as e:
                logger.error(f"Error processing work item {item_count}: {e}", exc_info=True)
                error_output = {
                    "status": "error",
                    "error": str(e),
                }
                try:
                    output_item = outputs.create(error_output)
                    output_item.save()
                except Exception as output_error:
                    logger.error(f"Failed to write error output: {output_error}", exc_info=True)
                # Continue processing other items on non-FunctionalError exceptions
                continue
        
        if item_count == 0:
            logger.warning("No input work items found")
        else:
            logger.info(f"Work item processor completed successfully ({item_count} items)")
        
    except FunctionalError:
        # Re-raise FunctionalError to signal to ProcessCube
        logger.error("Fatal FunctionalError in work item processor", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Fatal error in work item processor: {e}", exc_info=True)
        raise
