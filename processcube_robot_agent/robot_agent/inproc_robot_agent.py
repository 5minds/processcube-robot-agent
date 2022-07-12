import json
import os
from pathlib import Path
import tempfile

import robot

from processcube_sdk.configuration import Config

from .error import RobotError

class InprocRobotAgent:

    def __init__(self, filename: str, config: Config):
        self._filename = filename
        self._config = config

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

    def get_execution_error(self, run_code:int, msg: str):

        new_msg = f"Robot: {self._filename} failed: {msg}"

        return RobotError(run_code, new_msg)

    def execute(self, payload, task):
        self._root_dir = self._config.get('robot_agent', 'robots_root_dir')

        robot_filename = self.get_robot_filename()

        with tempfile.TemporaryDirectory() as tmpdirname:

            self.create_input_data(tmpdirname, payload, task)

            run_code = robot.run(robot_filename)

            if run_code == 0:
                result = self.read_output_data(tmpdirname, task)
            elif run_code >= 0 or run_code <= 249:
                raise self.get_execution_error(run_code, f"Executing {run_code} tasks failed.")
            elif run_code == 251:
                msg = "Help or version information printed."
                raise self.get_execution_error(run_code, msg)
            elif run_code == 252:
                msg = "Invalid test data or command line options."
                raise self.get_execution_error(run_code, msg)
            elif run_code == 253:
                msg = "Test execution stopped by user."
                raise self.get_execution_error(run_code, msg)
            elif run_code == 255:
                msg = "Unexpected internal error."
                raise self.get_execution_error(run_code, msg)
            else:
                raise self.get_execution_error(run_code, f"Robot failed with {run_code} tasks failed to execute")

        return result
