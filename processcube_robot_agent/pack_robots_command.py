import logging

from processcube_sdk.configuration.config_accessor import ConfigAccessor

from .robot_agent.rcc import ProjectPacker as RccProjectPacker
from .robot_agent.uv import ProjectPacker as UvProjectPacker

logger = logging.getLogger("processcube_robot_agent")


def start_pack_robots():
    """Pack all robots from both RCC and UV sources.

    Discovers and packages robots from configured project directories
    for both RCC and UV runners.
    """
    ConfigAccessor.ensure_from_env()
    config = ConfigAccessor.current()

    logger.info("Starting to pack robots from all sources...")

    # Pack RCC robots
    try:
        logger.info("Packing RCC robots...")
        rcc_packer = RccProjectPacker(config)
        rcc_packer.start()
        logger.info("RCC robots packed successfully")
    except Exception as e:
        logger.warning(f"Failed to pack RCC robots: {e}")

    # Pack UV robots
    try:
        logger.info("Packing UV robots...")
        uv_packer = UvProjectPacker(config)
        uv_packer.start()
        logger.info("UV robots packed successfully")
    except Exception as e:
        logger.warning(f"Failed to pack UV robots: {e}")

    logger.info("Robot packing completed")