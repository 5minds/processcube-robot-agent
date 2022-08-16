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

class FactoryBuilder:
    
    def __init__(self, wrap_dir: str, topic_prefix: str):
        self._wrap_dir = wrap_dir
        self._topic_prefix = topic_prefix

    def _build_topic(self, filename: str) -> str:

        topic = filename.replace('/', '.').removesuffix('.zip')

        return f"{self._topic_prefix}.{topic}"

    def _build_robot_path(self, filename: str) -> str:

        robot_path = str(Path(filename).relative_to(self._wrap_dir))

        return robot_path

    def build(self, filename: str) -> Factory:

        robot_path = self._build_robot_path(filename)
        topic = self._build_topic(robot_path)

        return Factory(robot_path, topic)

class RobotTaskHandlerFactoryCreator:

    def __init__(self, config: Config):
        self._config = config
        self._wrap_dir = Path(self._config.get('rcc', 'wrap_dir')).absolute()
        self._topic_prefix = self._config.get('rcc', 'topic_prefix', default='robot_task')
        self._factory_builder = FactoryBuilder(self._wrap_dir, self._topic_prefix)

    def _build_topic(self, filename: str) -> str:

        topic = filename.replace('/', '.').removesuffix('.zip')

        return f"{self._topic_prefix}.{topic}"

    def _build_factory_new(self, filename: str) -> Factory:

        robot_path = str(Path(filename).relative_to(self._wrap_dir))

        topic = self._build_topic(robot_path)

        return Factory(robot_path, topic)

    def _build_factory(self, filename: str) -> Factory:

        return self._factory_builder.build(filename)

    def __iter__(self) -> Factory:

        for path in self._wrap_dir.rglob('*.zip'):

            factory = self._build_factory(str(path))

            yield factory
