import logging

from processcube_sdk.configuration.config_accessor import ConfigAccessor

from .robot_agent.rcc import ProjectPacker
from .robot_agent.rcc import ProjectWatcher

logger = logging.getLogger("processcube_robot_agent")

def start_watch_robots():

    ConfigAccessor.ensure_from_env()
    config = ConfigAccessor.current()

    logger.info(f"start watch robots new or changed robots (and pack @ first all available robots).")
    project_packer = ProjectPacker(config)
    project_packer.start()

    project_watcher = ProjectWatcher(config)
    project_watcher.watch()