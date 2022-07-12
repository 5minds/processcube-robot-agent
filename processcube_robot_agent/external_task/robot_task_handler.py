import json
import os
from pathlib import Path
import robot
import tempfile


from processcube_sdk.external_tasks import BaseHandler
from processcube_sdk.configuration import Config

class RobotTaskHandler(BaseHandler):

    def __init__(self, config: Config):
        super(RobotTaskHandler, self).__init__('robot_task')
        self._root_dir = config.get('robot_agent', 'robots_root_dir')
        
    def create_input_data(self, temp_dirname:str, payload, task):
            input_file = Path(temp_dirname).joinpath(f"{task['id']}.json").absolute()
            output_file = Path(temp_dirname).joinpath(f"{task['id']}.output.json").absolute()

            os.environ['RPA_WORKITEMS_ADAPTER'] = 'RPA.Robocorp.WorkItems.FileAdapter'
            os.environ['RPA_INPUT_WORKITEM_PATH'] = str(input_file)
            os.environ['RPA_OUTPUT_WORKITEM_PATH'] = str(output_file)

            list_payload = [{'payload': payload}]

            with open(input_file, encoding='utf-8', mode='w') as fd:
                fd.write(json.dumps(list_payload, indent=4))

    def read_output_data(self, temp_dirname:str, task):
        output_file = Path(temp_dirname).joinpath(f"{task['id']}.output.json").absolute()
        if output_file.exists():
            with open(output_file, encoding='utf-8', mode='r') as fd:
                json_result = json.load(fd)

                if len(json_result) > 0:
                    return json_result[0].get('payload', {})
        return {}
    
    def __call__(self, payload, task):
        with tempfile.TemporaryDirectory() as tmpdirname:

            self.create_input_data(tmpdirname, payload, task)

            robot_fileame = Path().cwd().joinpath(self._root_dir).joinpath('test.robot').absolute()

            robot.run(robot_fileame)

            result = self.read_output_data(tmpdirname, task)
            
        return result


def create_external_task(config: Config) -> BaseHandler:

    handler = RobotTaskHandler(config)
    
    return handler
