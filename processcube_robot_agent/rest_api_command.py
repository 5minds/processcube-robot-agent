from typing import Any, Dict

from fastapi import FastAPI

from processcube_sdk.configuration.config_accessor import ConfigAccessor
from processcube_sdk.configuration import Config

from .watch_robots_command import start_watch_robots

from .rest_api import robots


description = """
The ProcessCube Robot Agent is a REST API that allows to rest the installed robots.
"""

webapp = FastAPI(
    title="API for ProcessCube Robot Agent",
    description=description,
    version="0.0.1",
    terms_of_service="https://www.5minds.de/impressum/",
    contact={
        "name": "5Minds IT-Solutions GmbH & Co. KG",
        "url": "https://www.5minds.de/kontakt/",
        "email": "solutions@5minds.de",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

webapp.include_router(robots.router)


def start_rest_api() -> None:
    """Start the REST API server.

    Initializes configuration from environment and starts
    the FastAPI server with uvicorn.
    """
    import uvicorn

    ConfigAccessor.ensure_from_env()
    config: Config = ConfigAccessor.current()

    port: int = config.get('rest_api', 'port', default=8000)
    host: str = config.get('rest_api', 'host', default='127.0.0.1')

    # Note: loop parameter was deprecated in uvicorn 0.24.0
    # uvicorn now automatically uses asyncio for async apps
    uvicorn.run("processcube_robot_agent.rest_api_command:webapp", host=host, port=port, log_level="info", reload=False)
