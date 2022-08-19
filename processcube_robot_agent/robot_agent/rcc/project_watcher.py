import logging
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .project_packer import ProjectPacker
from .robot_task_handler_factory import FactoryBuilder

logger = logging.getLogger('processcube_robot_agent.robot_agent.project_watcher')

class RobotsFileSystemEventHandler(FileSystemEventHandler):
    def __init__(self, config, project_dir, external_task_client):
        super(RobotsFileSystemEventHandler, self).__init__()
        self._config = config
        self._project_dir = project_dir
        self._project_packer: ProjectPacker = ProjectPacker(config)
        self._external_task_client = external_task_client
        
        wrap_dir = Path(self._config.get('rcc', 'wrap_dir')).absolute()
        topic_prefix = self._config.get('rcc', 'topic_prefix', default='robot_task')

        self._factory_builder = FactoryBuilder(wrap_dir, topic_prefix)

    def install_robot(self, packed_robot_path: str):
        factory = self._factory_builder.build(packed_robot_path)
        handler = factory.create_external_task(self._config)
        self._external_task_client.subscribe_to_external_task_for_topic(handler.get_topic(), handler)

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
            elif path.is_file():
                return find_robot_yaml(path.parent)
            else:
                return None

        logger.info(event)
        changed_path = Path(event.src_path)

        robot_yaml = find_robot_yaml(changed_path)
        if robot_yaml is not None:
            packed_robot_path = self._project_packer.pack_folder(robot_yaml)
            self.install_robot(packed_robot_path)
        else:
            logger.warn(f"Cannot find any robot.yaml in path {changed_path}")

class ProjectWatcher:

    def __init__(self, config, external_task_client):
        self._config = config
        self._project_dir = Path(self._config.get('rcc', 'project_dir')).absolute()
        self._wrap_dir = Path(self._config.get('rcc', 'wrap_dir')).absolute()
        self._external_task_client = external_task_client

    def watch(self):
        event_handler = RobotsFileSystemEventHandler(self._config, self._project_dir, self._external_task_client)

        observer = Observer()
        observer.schedule(event_handler, self._project_dir, recursive=True)
        
        observer.start()
