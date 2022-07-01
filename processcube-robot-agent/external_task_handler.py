import json
import os
from pathlib import Path
import robot
import tempfile


class ExternalTaskHandler:

    def __init__(self):
        self._root_dir = Path(__file__).parent.absolute()

    def __call__(self, payload, task):
        with tempfile.TemporaryDirectory() as tmpdirname:
            input_file = Path(tmpdirname).joinpath(f"{task['id']}.json").absolute()
            output_file = Path(tmpdirname).joinpath(
                f"{task['id']}.output.json").absolute()
            os.environ['RPA_WORKITEMS_ADAPTER'] = 'RPA.Robocorp.WorkItems.FileAdapter'
            os.environ['RPA_INPUT_WORKITEM_PATH'] = str(input_file)
            os.environ['RPA_OUTPUT_WORKITEM_PATH'] = str(output_file)

            list_payload = [{'payload': payload}]

            with open(input_file, encoding='utf-8', mode='w') as fd:
                fd.write(json.dumps(list_payload, indent=4))

            robot.run(self._root_dir.joinpath('test.robot'))

            result = {}
            
            if output_file.exists():
                with open(output_file, encoding='utf-8', mode='r') as fd:
                    json_result = json.load(fd)

                    if len(json_result) > 0:
                        result = json_result[0].get('payload', {})

        return result
