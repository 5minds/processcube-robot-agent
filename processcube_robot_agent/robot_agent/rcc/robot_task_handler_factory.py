import glob
from pathlib import Path

from processcube_sdk.configuration import Config
from processcube_sdk.external_tasks import BaseHandler

from ...external_task.robot_task_handler import RobotTaskHandler

from .robot_agent import RobotAgent

class Factory:

    def __init__(self, filename, topic: str):

        self._filename = filename
        self._topic = topic

    def get_topic(self) -> str:

        return self._topic

    def create_external_task(self, config: Config) -> BaseHandler:

        inproc_agent = RobotAgent(self._filename, config)

        handler = RobotTaskHandler(self._topic, inproc_agent)

        return handler

class RobotTaskHandlerFactoryCreator:

    def __init__(self, config: Config):
        self._config = config
        self._robots_root_dir = Path(self._config.get('rcc_robot_agent', 'robots_root_dir')).absolute()
        self._topic_prefix = self._config.get('robot_agent', 'topic_prefix', default='robot_task')

    def _build_topic(self, filename: str) -> str:

        topic = filename.replace('/', '.').removesuffix('.zip')

        return f"{self._topic_prefix}.{topic}"

    def _build_factory(self, filename: str) -> Factory:

        robot_path = str(Path(filename).relative_to(self._robots_root_dir))

        topic = self._build_topic(robot_path)

        return Factory(robot_path, topic)

    def __iter__(self) -> Factory:

        for path in self._robots_root_dir.rglob('*.zip'):

            factory = self._build_factory(path)

            yield factory
