import json
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Any, Dict

from processcube_sdk.configuration import Config

from ..base_agent import BaseAgent
from ..error import RobotError

from .rcc_runner import RccRunner


class RobotAgent(BaseAgent, RccRunner):
    """Robot execution agent using RCC (Robot Code Compiler).

    Handles unpacking, executing, and managing robot tasks.
    """

    def __init__(self, filename: str, config: Config) -> None:
        """Initialize RobotAgent.

        Args:
            filename: Robot package filename (e.g., 'webui.zip').
            config: ProcessCube configuration object.
        """
        self._filename = filename
        self._config = config
        self._wrap_dir = self._config.get('rcc', 'wrap_dir', default="robots")
        self._unwrap_dir = self._config.get('rcc', 'unwrap_dir', default="temp/unwrap")

    def create_input_data(self, temp_dirname: str, payload: Dict[str, Any], task: Dict[str, Any]) -> None:
        """Create input work items for robot execution.

        Args:
            temp_dirname: Temporary directory for work items.
            payload: Input data for the robot.
            task: Task metadata.
        """
        input_file = Path(temp_dirname).joinpath(f"{task['id']}.json").absolute()
        output_file = Path(temp_dirname).joinpath(f"{task['id']}.output.json").absolute()

        # siehe https://robocorp.com/docs/development-guide/control-room/data-pipeline#developing-with-work-items-locally)
        os.environ['RPA_WORKITEMS_ADAPTER'] = 'RPA.Robocorp.WorkItems.FileAdapter'
        os.environ['RPA_WORKITEMS_PATH'] = str(input_file)
        os.environ['RPA_INPUT_WORKITEM_PATH'] = str(input_file)
        os.environ['RPA_OUTPUT_WORKITEM_PATH'] = str(output_file)

        data_parameters = self.get_data(payload, task)

        list_payload = [{'payload': data_parameters}]

        with open(input_file, encoding='utf-8', mode='w') as fd:
            fd.write(json.dumps(list_payload, indent=4))

    def read_output_data(self, temp_dirname: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Read output data from robot execution.

        Args:
            temp_dirname: Temporary directory containing output files.
            task: Task metadata with 'id' field.

        Returns:
            Dictionary with robot output data.
        """
        output_file = Path(temp_dirname).joinpath(f"{task['id']}.output.json").absolute()
        if output_file.exists():
            with open(output_file, encoding='utf-8', mode='r') as fd:
                json_result = json.load(fd)

                if len(json_result) > 0:
                    return json_result[0].get('payload', {})
        return {}

    def get_data(self, payload: Dict[str, Any], _: Dict[str, Any]) -> Dict[str, Any]:
        """Get data parameters from payload.

        Args:
            payload: Input payload.
            _: Ignored parameter (task).

        Returns:
            Data parameters dictionary.
        """
        data_parameters = payload
        return data_parameters

    def get_robot_filename(self) -> Path:
        """Get the absolute path to the robot package file.

        Returns:
            Absolute path to robot .zip file.
        """
        robot_filename = Path().cwd().joinpath(self._wrap_dir).joinpath(self._filename).absolute()
        return robot_filename

    def get_unwrapped_path(self) -> Path:
        """Get the path where robot will be unpacked.

        Returns:
            Absolute path to unpacking directory.
        """
        filename = self._filename.removesuffix('.zip')
        unwrapped_path = Path().cwd().joinpath(self._unwrap_dir).joinpath(filename).absolute()
        return unwrapped_path

    def unwrap(self) -> subprocess.CompletedProcess:
        """Unwrap robot package using RCC.

        Returns:
            Completed process from RCC unwrap command.

        Raises:
            RobotError: If unwrapping fails.
        """
        robot_path = self.get_robot_filename()
        unwrapped_path = self.get_unwrapped_path()

        Path(unwrapped_path).mkdir(parents=True, exist_ok=True)

        cmd = ["rcc", "robot", "unwrap", "-z", str(robot_path), "-d", str(unwrapped_path), "--force"]

        completed_process = subprocess.run(cmd, capture_output=True, text=True)

        if completed_process.returncode != 0:
            raise RobotError("unwrap", f"unwrap {robot_path} to {unwrapped_path} failed with return code {completed_process.returncode}\nStderr: {completed_process.stderr}")

        return completed_process

    def run_robot(self) -> subprocess.CompletedProcess:
        """Execute robot using RCC.

        Returns:
            Completed process from RCC run command.

        Raises:
            RobotError: If robot execution fails.
        """
        unwrapped_path = self.get_unwrapped_path().joinpath('robot.yaml').absolute()

        cmd = ["rcc", "run", "-r", str(unwrapped_path)]

        completed_process = subprocess.run(cmd, capture_output=True, text=True)

        if completed_process.returncode != 0:
            output_xml = self.read_output_xml(unwrapped_path)
            raise RobotError(f"return_code_{completed_process.returncode}", completed_process.stdout, details=output_xml)

        return completed_process

    def execute(self, payload: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute robot task with given payload.

        Orchestrates the complete robot execution pipeline:
        1. Validates RCC availability
        2. Creates work items from payload
        3. Unpacks robot package
        4. Executes robot
        5. Extracts and returns output

        Args:
            payload: Input data for the robot.
            task: Task metadata.

        Returns:
            Dictionary with robot output.

        Raises:
            RobotError: If any step fails.
        """
        result: Dict[str, Any] = {}

        self.check_rcc()

        with tempfile.TemporaryDirectory() as tmpdirname:
            self.create_input_data(tmpdirname, payload, task)
            self.unwrap()
            self.run_robot()
            result = self.read_output_data(tmpdirname, task)

        return result

    def read_output_xml(self, rcc_robot_yaml_path: Path) -> str:
        """Read output XML from robot execution.

        Args:
            rcc_robot_yaml_path: Path to robot.yaml file.

        Returns:
            Content of output.xml or empty string if not found.
        """
        output_xml_path = rcc_robot_yaml_path.parent.joinpath('output').joinpath('output.xml')

        if output_xml_path.is_file():
            content = output_xml_path.read_text()
            return content

        return ""