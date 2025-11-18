import logging
from typing import List

from processcube_sdk.configuration import ConfigAccessor

from .rcc import RobotTaskHandlerFactoryCreator as RccRobotTaskHandlerFactoryCreator
from .uv import RobotTaskHandlerFactoryCreator as UvRobotTaskHandlerFactoryCreator

logger = logging.getLogger("processcube_robot_agent")


class MultiRunnerFactoryCreator:
    """Combines RCC and UV robot factories for multi-runner support."""

    def __init__(self, config):
        """Initialize with both RCC and UV factories.

        Args:
            config: ProcessCube configuration object.
        """
        self._config = config
        self._factories = []

        # Initialize RCC factory if configured
        try:
            self._factories.append(RccRobotTaskHandlerFactoryCreator(config))
            logger.info("RCC robot factory initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize RCC factory: {e}")

        # Initialize UV factory if configured
        try:
            self._factories.append(UvRobotTaskHandlerFactoryCreator(config))
            logger.info("UV robot factory initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize UV factory: {e}")

    def __iter__(self):
        """Iterate through all robot factories."""
        for factory in self._factories:
            for item in factory:
                yield item


def build() -> MultiRunnerFactoryCreator:
    """Build and return the multi-runner robot task handler factory.

    Loads configuration from environment and creates factories
    for managing both RCC and UV robot task handlers.

    Returns:
        MultiRunnerFactoryCreator: Factory combining RCC and UV runners.
    """
    ConfigAccessor.ensure_from_env()
    config = ConfigAccessor.current()

    handler_factory = MultiRunnerFactoryCreator(config)

    return handler_factory