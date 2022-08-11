
from cgitb import handler
import logging
import sys

from processcube_sdk.configuration import ConfigAccessor

from .rcc import RobotTaskHandlerFactoryCreator as RobotTaskHandlerFactoryCreator

logger = logging.getLogger("processcube_robot_agent")

def build():
    ConfigAccessor.ensure_from_env()
    config = ConfigAccessor.current()

    handler_factory = RobotTaskHandlerFactoryCreator(config)

    return handler_factory
   