from processcube_sdk.configuration.config_accessor import ConfigAccessor

from .robot_agent.rcc import ProjectWatcher

def start_watch_robots():

    ConfigAccessor.ensure_from_env()
    config = ConfigAccessor.current()

    project_watcher = ProjectWatcher(config)
    project_watcher.watch()