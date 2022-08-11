from processcube_sdk.configuration.config_accessor import ConfigAccessor

from .robot_agent.rcc import ProjectPacker

def start_pack_robots():

    ConfigAccessor.ensure_from_env()
    config = ConfigAccessor.current()

    project_packer = ProjectPacker(config)
    project_packer.start()