
from cgitb import handler
import logging
import sys

from processcube_sdk.configuration import ConfigAccessor

from .inproc import RobotTaskHandlerFactoryCreator as inproc_RobotTaskHandlerFactoryCreator
from .rcc import RobotTaskHandlerFactoryCreator as rcc_RobotTaskHandlerFactoryCreator

logger = logging.getLogger("processcube_robot_agent")

creator_map = {
    "inproc": inproc_RobotTaskHandlerFactoryCreator,
    "rcc": rcc_RobotTaskHandlerFactoryCreator,
}

def build():
    ConfigAccessor.ensure_from_env()
    config = ConfigAccessor.current()

    creator_type = config.get('robot_agent', 'type', default='inproc')
    creator_class = creator_map.get(creator_type)

    if creator_class is None:
        logger.error("Unknown robot agent type: %s", creator_type)
        sys.exit(-1)

    logger.info("Starting robot agent type: %s", creator_type)
    handler_factory = creator_class(config)

    return handler_factory
   