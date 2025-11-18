import logging
from concurrent.futures import ThreadPoolExecutor

from processcube_sdk.configuration.config_accessor import ConfigAccessor

from .robot_agent.rcc import ProjectPacker as RccProjectPacker
from .robot_agent.rcc import ProjectWatcher as RccProjectWatcher
from .robot_agent.uv import ProjectPacker as UvProjectPacker
from .robot_agent.uv import ProjectWatcher as UvProjectWatcher

logger = logging.getLogger("processcube_robot_agent")


def start_watch_robots(external_task_client):
    """Watch and pack robots from both RCC and UV sources.

    Discovers all robots initially, then continuously monitors for changes
    in both RCC and UV project directories.

    Args:
        external_task_client: Client for registering external tasks.
    """
    ConfigAccessor.ensure_from_env()
    config = ConfigAccessor.current()

    logger.info("Starting to watch robots from all sources (and pack all available robots initially).")

    # Initial pack of all robots from both sources
    logger.info("Packing all robots initially...")
    try:
        rcc_packer = RccProjectPacker(config)
        rcc_packer.start()
        logger.info("RCC robots packed successfully")
    except Exception as e:
        logger.warning(f"Failed to pack RCC robots: {e}")

    try:
        uv_packer = UvProjectPacker(config)
        uv_packer.start()
        logger.info("UV robots packed successfully")
    except Exception as e:
        logger.warning(f"Failed to pack UV robots: {e}")

    # Start watchers for both RCC and UV in separate threads
    executor = ThreadPoolExecutor(max_workers=2)

    # Watch RCC robots
    try:
        logger.info("Starting RCC project watcher...")
        rcc_watcher = RccProjectWatcher(config, external_task_client)
        executor.submit(rcc_watcher.watch)
        logger.info("RCC project watcher started")
    except Exception as e:
        logger.warning(f"Failed to start RCC watcher: {e}")

    # Watch UV robots
    try:
        logger.info("Starting UV project watcher...")
        uv_watcher = UvProjectWatcher(config, external_task_client)
        executor.submit(uv_watcher.watch)
        logger.info("UV project watcher started")
    except Exception as e:
        logger.warning(f"Failed to start UV watcher: {e}")

    logger.info("Robot watchers initialized and running")
