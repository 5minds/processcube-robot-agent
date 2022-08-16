import asyncio
import logging

import typer

from processcube_sdk.debugging import start_debugging
from processcube_sdk.logging import setup_logging
from processcube_sdk.external_tasks import start_external_task
from processcube_sdk.configuration.config_accessor import ConfigAccessor

from .robot_agent import builder
from .pack_robots_command import start_pack_robots
from .watch_robots_command import start_watch_robots
from .rest_api_command import start_rest_api, webapp

app = typer.Typer()

logger = logging.getLogger("processcube_robot_agent")

@app.command(short_help="Pack the rcc projects folders and install them into the agent.")
def pack():
    setup_logging()
    start_pack_robots()

@app.command(short_help="Start the restapi and the external tasks worker for every installed robot.")
def serve():
    @webapp.on_event('startup')
    def event_start_external_task():
        loop = asyncio.get_running_loop()

        external_task_client = start_external_task(builder.build(), loop=loop)
        logger.info(f"Started external task {external_task_client}")

        ConfigAccessor.ensure_from_env()
        config = ConfigAccessor.current()

        start_watch_project_dir = config.get('rcc', 'start_watch_project_dir', default=False)

        if start_watch_project_dir:
            _ = loop.run_in_executor(None, start_watch_robots, external_task_client) # TODO: cancel the task if the service will stopped

    @webapp.on_event("shutdown")
    def event_stop_external_task():
        logger.info("Stopping external task")


    setup_logging()
    start_debugging()
    start_rest_api()

if __name__ == '__main__':
    app()