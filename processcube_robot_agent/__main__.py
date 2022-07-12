
import typer

from processcube_sdk.configuration import ConfigAccessor
from processcube_sdk.debugging import start_debugging
from processcube_sdk.logging import setup_logging
from processcube_sdk.external_tasks import start_external_task

from .robot_agent.inproc import RobotTaskHandlerFactoryCreator


app = typer.Typer()

@app.callback(invoke_without_command=True)
def default():
    ConfigAccessor.ensure_from_env()
    config = ConfigAccessor.current()

    setup_logging()
    start_debugging()

    handler_factory= RobotTaskHandlerFactoryCreator(config)

    start_external_task(handler_factory)


if __name__ == '__main__':
    app()