
from processcube_sdk.external_tasks import BaseHandler

from ..robot_agent import BaseAgent

class RobotTaskHandler(BaseHandler):

    def __init__(self, topic: str, agent: BaseAgent):
        super(RobotTaskHandler, self).__init__(topic)
        self._agent = agent
    
    def __call__(self, payload, task):

        result = self._agent.execute(payload, task)

        return result
