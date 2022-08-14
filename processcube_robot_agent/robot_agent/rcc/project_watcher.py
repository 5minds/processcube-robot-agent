import logging
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .project_packer import ProjectPacker

logger = logging.getLogger('processcube_robot_agent.robot_agent.project_watcher')

class RobotsFileSystemEventHandler(FileSystemEventHandler):
    def __init__(self, config, project_dir):
        super(RobotsFileSystemEventHandler, self).__init__()
        self._config = config
        self._project_dir = project_dir
        self._project_packer: ProjectPacker = ProjectPacker(config)

    def on_any_event(self, event):

        def find_robot_yaml(path: Path):
            logger.info(f"find_robot_yaml {path}")
            if path.absolute() == self._project_dir:
                return None
            elif path.is_dir():
                if path.joinpath('robot.yaml').exists():
                    return path.joinpath('robot.yaml')
                else:
                    return find_robot_yaml(path.parent)

        logger.info(event)
        changed_path = Path(event.src_path)

        robot_yaml = find_robot_yaml(changed_path)
        if robot_yaml is not None:
            self._project_packer.pack_folder(robot_yaml)
        else:
            logger.warn(f"Cannot find any robot.yaml in path {changed_path}")

class ProjectWatcher:

    def __init__(self, config):
        self._config = config
        self._project_dir = Path(self._config.get('rcc', 'project_dir')).absolute()
        self._wrap_dir = Path(self._config.get('rcc', 'wrap_dir')).absolute()

    def watch(self):
        event_handler = RobotsFileSystemEventHandler(self._config, self._project_dir)

        observer = Observer()
        observer.schedule(event_handler, self._project_dir, recursive=True)
        
        observer.start()
        try:
            while True:
                pass
        except KeyboardInterrupt:
            observer.stop()
            observer.join()