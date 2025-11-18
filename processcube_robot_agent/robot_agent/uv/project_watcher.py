import logging
from pathlib import Path
from typing import Optional

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .project_packer import ProjectPacker
from .robot_task_handler_factory import FactoryBuilder

logger = logging.getLogger('processcube_robot_agent.robot_agent.project_watcher')


class RobotsFileSystemEventHandler(FileSystemEventHandler):
    """Handles file system events for robot project changes."""

    def __init__(self, config, project_dir, external_task_client) -> None:
        """Initialize file system event handler.

        Args:
            config: ProcessCube configuration object.
            project_dir: Root project directory to monitor.
            external_task_client: Client for registering external tasks.
        """
        super(RobotsFileSystemEventHandler, self).__init__()
        self._config = config
        self._project_dir = project_dir
        self._project_packer: ProjectPacker = ProjectPacker(config)
        self._external_task_client = external_task_client

        wrap_dir = Path(self._config.get('uv', 'wrap_dir')).absolute()
        topic_prefix = self._config.get('uv', 'topic_prefix', default='uv_robot_task')

        self._factory_builder = FactoryBuilder(wrap_dir, topic_prefix)

    def install_robot(self, packed_robot_path: str) -> None:
        """Register a packed robot with the external task client.

        Args:
            packed_robot_path: Path to the packed robot .zip file.

        Raises:
            Exception: If factory building or subscription fails.
        """
        # Ensure external_task_client is available
        if self._external_task_client is None:
            logger.warning(f"Cannot install robot {packed_robot_path}: external_task_client is not initialized yet")
            return

        factory = self._factory_builder.build(packed_robot_path)
        handler = factory.create_external_task(self._config)
        self._external_task_client.subscribe_to_external_task_for_topic(handler.get_topic(), handler)

    def on_any_event(self, event) -> None:
        """Handle file system events with error handling.

        Args:
            event: File system event from watchdog.

        Handles:
            - Finding pyproject.toml for changed files
            - Packing modified robots
            - Registering with external task client
            - Logging warnings for unrelated changes
        """

        def find_pyproject_toml(path: Path) -> Optional[Path]:
            """Recursively find parent pyproject.toml file.

            Args:
                path: File or directory path to start search.

            Returns:
                Path to pyproject.toml if found, None otherwise.
            """
            logger.debug(f"find_pyproject_toml {path}")
            if path.absolute() == self._project_dir:
                return None
            elif path.is_dir():
                if path.joinpath('pyproject.toml').exists():
                    return path.joinpath('pyproject.toml')
                else:
                    return find_pyproject_toml(path.parent)
            elif path.is_file():
                return find_pyproject_toml(path.parent)
            else:
                return None

        try:
            logger.debug(f"File system event: {event}")
            changed_path = Path(event.src_path)

            pyproject_toml = find_pyproject_toml(changed_path)
            if pyproject_toml is not None:
                try:
                    logger.info(f"Robot file changed: {changed_path}")
                    packed_robot_path = self._project_packer.pack_folder(pyproject_toml)
                    self.install_robot(packed_robot_path)
                    logger.info(f"Successfully packed and registered robot: {packed_robot_path}")
                except Exception as e:
                    logger.error(f"Failed to pack or install robot {pyproject_toml}: {e}", exc_info=True)
            else:
                logger.debug(f"No pyproject.toml found for changed path {changed_path}")
        except Exception as e:
            logger.error(f"Error processing file system event: {e}", exc_info=True)

class ProjectWatcher:
    """Watches robot project directory for changes and auto-registers robots."""

    def __init__(self, config, external_task_client) -> None:
        """Initialize project watcher.

        Args:
            config: ProcessCube configuration object.
            external_task_client: Client for registering external tasks.
        """
        self._config = config
        self._project_dir = Path(self._config.get('uv', 'project_dir')).absolute()
        self._wrap_dir = Path(self._config.get('uv', 'wrap_dir')).absolute()
        self._external_task_client = external_task_client

    def watch(self) -> None:
        """Start monitoring the robot project directory for changes.

        Continuously watches for file system changes and automatically
        packs and registers modified robots.
        """
        event_handler = RobotsFileSystemEventHandler(self._config, self._project_dir, self._external_task_client)

        observer = Observer()
        observer.schedule(event_handler, self._project_dir, recursive=True)

        observer.start()
