import json
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Any, Dict

from processcube_sdk.configuration import Config

from ..base_agent import BaseAgent
from ..error import RobotError

from .uv_runner import UvRunner


class RobotAgent(BaseAgent, UvRunner):
    """Robot execution agent using UV (Python package manager).

    Handles unpacking, executing, and managing Python robot tasks
    that use UV for dependency management.
    """

    def __init__(self, filename: str, config: Config) -> None:
        """Initialize RobotAgent.

        Args:
            filename: Robot package filename (e.g., 'myrobot.zip').
            config: ProcessCube configuration object.
        """
        self._filename = filename
        self._config = config
        self._wrap_dir = self._config.get('uv', 'wrap_dir', default="robots/installed/uv")
        self._unwrap_dir = self._config.get('uv', 'unwrap_dir', default="temp/robots/uv/unwrapped")

    def create_input_data(self, temp_dirname: str, payload: Dict[str, Any], task: Dict[str, Any]) -> None:
        """Create input work items for robot execution.

        Args:
            temp_dirname: Temporary directory for work items.
            payload: Input data for the robot.
            task: Task metadata.
        """
        input_file = Path(temp_dirname).joinpath(f"{task['id']}.json").absolute()
        output_file = Path(temp_dirname).joinpath(f"{task['id']}.output.json").absolute()

        # Work items via JSON files (compatible with Robot Framework / RPA Framework)
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

    def _extract_dependencies(self, pyproject_path: Path) -> list:
        """Extract dependencies from pyproject.toml.

        Args:
            pyproject_path: Path to pyproject.toml file.

        Returns:
            List of dependency strings suitable for pip install.
        """
        if not pyproject_path.exists():
            return []

        try:
            import tomllib
        except ImportError:
            # Python < 3.11
            import tomli as tomllib

        try:
            with open(pyproject_path, 'rb') as f:
                pyproject_data = tomllib.load(f)

            dependencies = pyproject_data.get('project', {}).get('dependencies', [])
            return list(dependencies) if dependencies else []
        except Exception:
            return []

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
        """Unwrap robot package (extract ZIP and install dependencies with UV).

        Returns:
            Completed process from UV install command.

        Raises:
            RobotError: If unwrapping or dependency installation fails.
        """
        robot_path = self.get_robot_filename()
        unwrapped_path = self.get_unwrapped_path()

        # Extract ZIP
        import zipfile
        Path(unwrapped_path).mkdir(parents=True, exist_ok=True)
        
        try:
            with zipfile.ZipFile(robot_path, 'r') as zip_ref:
                zip_ref.extractall(unwrapped_path)
        except Exception as e:
            raise RobotError("unwrap", f"Failed to extract {robot_path} to {unwrapped_path}: {str(e)}")

        # Install dependencies using UV
        # Create a virtual environment and install from pyproject.toml or uv.lock
        venv_path = unwrapped_path.joinpath('.venv')
        python_path = venv_path / "bin" / "python"

        # Create virtual environment
        cmd_venv = ["uv", "venv", str(venv_path)]
        completed_process = subprocess.run(cmd_venv, capture_output=True, text=True)

        if completed_process.returncode != 0:
            raise RobotError("unwrap", f"Creating virtual environment failed with return code {completed_process.returncode}\nStderr: {completed_process.stderr}")

        # Install dependencies using uv pip install with the dependencies from pyproject.toml
        # This installs only the declared dependencies, not the project itself
        # Extract dependencies from pyproject.toml
        dependencies = self._extract_dependencies(unwrapped_path / "pyproject.toml")

        if dependencies:
            cmd_install = ["uv", "pip", "install", "--python", str(python_path)] + dependencies
        else:
            # If no dependencies found, still create the venv but don't install anything
            completed_process = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
            return completed_process

        completed_process = subprocess.run(cmd_install, capture_output=True, text=True)

        if completed_process.returncode != 0:
            raise RobotError("unwrap", f"Installing dependencies failed with return code {completed_process.returncode}\nStderr: {completed_process.stderr}")

        return completed_process

    def run_robot(self) -> subprocess.CompletedProcess:
        """Execute robot using UV.

        Expects to find main.py in the unpacked robot directory.

        Returns:
            Completed process from UV run command.

        Raises:
            RobotError: If robot execution fails.
        """
        unwrapped_path = self.get_unwrapped_path()
        main_py = unwrapped_path.joinpath('main.py')

        if not main_py.exists():
            raise RobotError("run_robot", f"main.py not found in {unwrapped_path}")

        venv_path = unwrapped_path.joinpath('.venv')
        
        cmd = ["uv", "run", "--python", str(venv_path / "bin" / "python"), "main.py"]

        completed_process = subprocess.run(cmd, capture_output=True, text=True, cwd=str(unwrapped_path))

        if completed_process.returncode != 0:
            raise RobotError(f"return_code_{completed_process.returncode}", completed_process.stdout)

        return completed_process

    def execute(self, payload: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute robot task with given payload.

        Orchestrates the complete robot execution pipeline:
        1. Validates UV availability
        2. Creates work items from payload
        3. Unpacks robot package and installs dependencies
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

        self.check_uv()

        with tempfile.TemporaryDirectory() as tmpdirname:
            self.create_input_data(tmpdirname, payload, task)
            self.unwrap()
            self.run_robot()
            result = self.read_output_data(tmpdirname, task)

        return result
