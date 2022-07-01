import logging


from pathlib import Path
from atlas_engine_client.external_task import ExternalTaskClient

from .external_task_handler import ExternalTaskHandler

logger = logging.getLogger(__name__)

root_dir = Path(__file__).parent.absolute()

def main(engine_url):
    client = ExternalTaskClient(engine_url)

    client.subscribe_to_external_task_for_topic(
        "RobotTask", ExternalTaskHandler())

    client.start()


if __name__ == '__main__':
    engine_url = 'http://localhost:56000'

    format_template = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    level = logging.INFO  # logging.DEBUG
    logging.basicConfig(level=level, format=format_template)

    main(engine_url)
