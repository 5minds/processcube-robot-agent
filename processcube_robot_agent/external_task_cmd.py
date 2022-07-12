
import logging

from processcube_sdk.configuration import ConfigAccessor
from atlas_engine_client.external_task import ExternalTaskClient

from .external_task import robot_task_handler

logger = logging.getLogger("processcube-robot-agent")

def start_external_task(loop=None):
    ConfigAccessor.ensure_from_env()
    config = ConfigAccessor.current()

    engine_url = config.get('engine', 'url')

    client = ExternalTaskClient(engine_url, loop=loop)

    handler_factories = [
        robot_task_handler,
    ]

    for factory in handler_factories:
        handler = factory.create_external_task(config)
        
        logger.info(f"Starting external task worker for topic '{handler.get_topic()}'")

        if loop is None:
            client.subscribe_to_external_task_for_topic(handler.get_topic(), handler)
        else:
            client.subscribe_to_external_task_for_topic(handler.get_topic(), handler, loop=loop)

    if loop is None:
        client.start()
    else:
        client.start(run_forever=False)
