import logging

from processcube_sdk.configuration import ConfigAccessor

from .rcc import RobotTaskHandlerFactoryCreator

logger = logging.getLogger("processcube_robot_agent")


def build() -> RobotTaskHandlerFactoryCreator:
    """Build and return the robot task handler factory.

    Loads configuration from environment and creates a factory
    for managing robot task handlers.

    Returns:
        RobotTaskHandlerFactoryCreator: Factory for creating robot handlers.
    """
    ConfigAccessor.ensure_from_env()
    config = ConfigAccessor.current()

    handler_factory = RobotTaskHandlerFactoryCreator(config)

    return handler_factory
   