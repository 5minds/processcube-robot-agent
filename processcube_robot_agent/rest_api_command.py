from fastapi import FastAPI

from processcube_sdk.configuration.config_accessor import ConfigAccessor

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

def start_rest_api():
    import uvicorn

    ConfigAccessor.ensure_from_env()
    config = ConfigAccessor.current()

    port = config.get('rest_api', 'port', default=8000)
    host = config.get('rest_api', 'host', default='127.0.0.1')

    # loop='asyncio' is required cause we are using papermill that raise an exception while running with 'uvloop'
    # "Can't patch loop of type <class 'uvloop.Loop'>"
    uvicorn.run("processcube_robot_agent.rest_api_command:webapp", host=host, port=port, log_level="info", reload=False, loop='asyncio')
