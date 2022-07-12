
from processcube_sdk.external_tasks import BaseHandler
from processcube_sdk.configuration import Config

from ..robot_agent import InprocRobotAgent

class RobotTaskHandler(BaseHandler):

    def __init__(self, topic: str, filename: str, config: Config):
        # TODO: Topic per robot-File
        super(RobotTaskHandler, self).__init__(topic)
        self._filename = filename
        self._config = config
        self._agent = InprocRobotAgent(self._filename, self._config)
    
    def __call__(self, payload, task):

        result = self._agent.execute(payload, task)

        return result
