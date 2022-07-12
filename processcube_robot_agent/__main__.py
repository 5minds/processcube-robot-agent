
import typer

from .external_task_cmd import start_external_task
from .infrastructure.debugging import start_debugging
from .infrastructure.logging import setup_logging

app = typer.Typer()

@app.callback(invoke_without_command=True)
def default():
    setup_logging()
    start_debugging()
    start_external_task()


if __name__ == '__main__':
    app()