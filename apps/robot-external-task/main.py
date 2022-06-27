from lib2to3.pgen2.token import INDENT
import logging
from tarfile import ENCODING
import robot
import os


import tempfile
import json


from pathlib import Path
from atlas_engine_client.external_task import ExternalTaskClient
from RPA.Robocorp.WorkItems import WorkItems

logger = logging.getLogger(__name__)

def _handler(payload, task):
    with tempfile.TemporaryDirectory() as tmpdirname:
        input_file = Path(tmpdirname).joinpath(f"{task['id']}.json").absolute()
        output_file = Path(tmpdirname).joinpath(f"{task['id']}.output.json").absolute()
        os.environ['RPA_WORKITEMS_ADAPTER'] = 'RPA.Robocorp.WorkItems.FileAdapter'
        os.environ['RPA_INPUT_WORKITEM_PATH'] = str(input_file)
        os.environ['RPA_OUTPUT_WORKITEM_PATH'] = str(output_file)

        list_payload = [{'payload': payload}]


        with open(input_file, encoding='utf-8', mode='w') as fd:
            fd.write(json.dumps(list_payload, indent=4))

        robot.run('apps/robot-external-task/test.robot')

        result = {}
        if output_file.exists():
            with open(output_file, encoding='utf-8', mode='r') as fd:
                json_result = json.load(fd)

                if len(json_result) > 0:
                    result = json_result[0].get('payload', {})
                    
    return result

def main(engine_url):
    client = ExternalTaskClient(engine_url)

    client.subscribe_to_external_task_for_topic("RobotTask", _handler, max_tasks=5)

    client.start()

if __name__ == '__main__':
    engine_url = 'http://localhost:56000'

    format_template = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    level = logging.INFO #logging.DEBUG
    logging.basicConfig(level=level, format=format_template)

    main(engine_url)