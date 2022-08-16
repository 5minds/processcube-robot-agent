import asyncio
import logging

import typer

from processcube_sdk.debugging import start_debugging
from processcube_sdk.logging import setup_logging
from processcube_sdk.external_tasks import start_external_task

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

@app.command(short_help="Watch to pack new robots from project folder to wrap folder.")
def watch():
    setup_logging()
    start_watch_robots()

@app.command(short_help="Start the restapi and the external tasks worker for every installed robot.")
def serve():
    @webapp.on_event('startup')
    def event_start_external_task():
        loop = asyncio.get_running_loop()

        c = start_external_task(builder.build(), loop=loop)
        logger.info(f"Started external task {c}")
    
    setup_logging()
    start_debugging()
    start_rest_api()

#@app.callback(invoke_without_command=True)
#def default():
#    start_all()


if __name__ == '__main__':
    app()