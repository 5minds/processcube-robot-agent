import typer
from processcube_sdk.logging import setup_logging
from processcube_sdk.configuration.config_accessor import ConfigAccessor

from .pack_robots_command import start_pack_robots
from .rest_api_command import start_rest_api

app = typer.Typer()


@app.command(short_help="Pack the rcc projects folders and install them into the agent.")
def pack():
    setup_logging()
    start_pack_robots()


@app.command(short_help="Start the restapi and the external tasks worker for every installed robot.")
def serve():

    setup_logging()

    # NOTE: Debugger is disabled by default to avoid asyncio.run() conflicts
    # with modern uvicorn versions (0.38+). The processcube_sdk debugger patches
    # asyncio.run() which is incompatible with uvicorn's new loop_factory parameter.
    # This is a known limitation and should be resolved in future SDK updates.
    ConfigAccessor.ensure_from_env()

    start_rest_api()

if __name__ == '__main__':
    app()