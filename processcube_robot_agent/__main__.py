
import logging

import typer

from processcube_sdk.debugging import start_debugging
from processcube_sdk.logging import setup_logging
from processcube_sdk.external_tasks import start_external_task

from .robot_agent import builder

app = typer.Typer()

logger = logging.getLogger("processcube_robot_agent")

@app.callback(invoke_without_command=True)
def default():
    setup_logging()
    start_debugging()

    start_external_task(builder.build())


if __name__ == '__main__':
    app()