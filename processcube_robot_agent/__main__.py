import asyncio
import logging

import typer

from processcube_sdk.debugging import start_debugging
from processcube_sdk.logging import setup_logging
from processcube_sdk.external_tasks import start_external_task

from .robot_agent import builder
from .rest_api_command import start_rest_api, webapp

app = typer.Typer()

logger = logging.getLogger("processcube_robot_agent")

@app.callback(invoke_without_command=True)
def default():
    @webapp.on_event('startup')
    def event_start_external_task():
        loop = asyncio.get_running_loop()

        start_external_task(builder.build(), loop=loop)
    
    setup_logging()
    start_debugging()
    start_rest_api()


if __name__ == '__main__':
    app()