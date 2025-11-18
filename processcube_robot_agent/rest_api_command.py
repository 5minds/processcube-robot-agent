import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from typing import Any, Dict

# Allow nested event loops for ProcessCube SDK compatibility
import nest_asyncio
nest_asyncio.apply()

from processcube_sdk.configuration.config_accessor import ConfigAccessor
from processcube_sdk.configuration import Config
from processcube_sdk.external_tasks import start_external_task

from .robot_agent import builder
from .watch_robots_command import start_watch_robots
from .rest_api import robots, health, metrics

logger = logging.getLogger("processcube_robot_agent")

@asynccontextmanager
async def event_start_external_task(app: FastAPI) -> Any:
    """Initialize external task client and optionally start robot watchers.

    Sets up the multi-runner factory and starts watching for robot changes
    if configured in RCC or UV settings.
    """
    ConfigAccessor.ensure_from_env()
    config = ConfigAccessor.current()

    loop = asyncio.get_running_loop()

    external_task_client = start_external_task(builder.build(), loop=loop, run_forever=False)
    logger.info(f"Started external task {external_task_client}")

    # Check if watchers should start (either RCC or UV or both)
    rcc_watch = config.get('rcc', 'start_watch_project_dir', default=False)
    uv_watch = config.get('uv', 'start_watch_project_dir', default=False)
    start_watch_project_dir = rcc_watch or uv_watch

    if start_watch_project_dir:
        logger.info("Starting robot project watchers (RCC and/or UV)...")
        _ = loop.run_in_executor(None, start_watch_robots, external_task_client)
    else:
        logger.info("Robot project watchers disabled in configuration")

    yield

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
    lifespan=event_start_external_task,
)

webapp.include_router(robots.router)
webapp.include_router(health.router)
webapp.include_router(metrics.router)


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
