import json
import os
from pathlib import Path
import subprocess
import tempfile

from processcube_sdk.configuration import Config

from ..base_agent import BaseAgent
from ..error import RobotError

class RobotAgent(BaseAgent):

    def __init__(self, filename: str, config: Config):
        self._filename = filename
        self._config = config
        self._root_dir = self._config.get('rcc_robot_agent', 'robots_root_dir', default="robots")
        self._unwrap_dir = self._config.get('rcc_robot_agent', 'unwrap_root_dir', default="temp/unwrap")

    def create_input_data(self, temp_dirname:str, payload, task):
        input_file = Path(temp_dirname).joinpath(f"{task['id']}.json").absolute()
        output_file = Path(temp_dirname).joinpath(f"{task['id']}.output.json").absolute()

        os.environ['RPA_WORKITEMS_ADAPTER'] = 'RPA.Robocorp.WorkItems.FileAdapter'
        os.environ['RPA_INPUT_WORKITEM_PATH'] = str(input_file)
        os.environ['RPA_OUTPUT_WORKITEM_PATH'] = str(output_file)

        data_parameters = self.get_data(payload, task)

        list_payload = [{'payload': data_parameters}]

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

    def get_data(self, payload, _):
        data_parameters = payload

        return data_parameters

    def get_robot_filename(self):

        robot_filename = Path().cwd().joinpath(self._root_dir).joinpath(self._filename).absolute()

        return robot_filename

    def get_unwrapped_path(self):

        filename = self._filename.removesuffix('.zip')

        unwrapped_path = Path().cwd().joinpath(self._unwrap_dir).joinpath(filename).absolute()

        return unwrapped_path

    def unwrap(self):

        robot_path = self.get_robot_filename()
        unwrapped_path = self.get_unwrapped_path()

        Path(unwrapped_path).mkdir(parents=True, exist_ok=True)

        cmd = f"rcc robot unwrap -z {str(robot_path)} -d {str(unwrapped_path)} --force"

        return_code = subprocess.call(cmd, shell=True)

        return return_code

    def run_robot(self):

        unwrapped_path = self.get_unwrapped_path().joinpath('robot.yaml').absolute()

        cmd = f"rcc run -r {str(unwrapped_path)}"

        return_code = subprocess.call(cmd, shell=True)

        return return_code

    def execute(self, payload, task):

        result = {}

        with tempfile.TemporaryDirectory() as tmpdirname:

            self.create_input_data(tmpdirname, payload, task)
            
            self.unwrap()

            self.run_robot()

            result = self.read_output_data(tmpdirname, task)

        return result
