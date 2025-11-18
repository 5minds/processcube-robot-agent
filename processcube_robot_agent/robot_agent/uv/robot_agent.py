import json
import logging
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Any, Dict

from processcube_sdk.configuration import Config

from ..base_agent import BaseAgent
from ..error import RobotError

from .uv_runner import UvRunner

logger = logging.getLogger(__name__)


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
            logger.info(f"Installing {len(dependencies)} dependencies: {', '.join(dependencies)}")
            # Install only the declared dependencies, not the robot project itself
            # The robot pyproject.toml should not have a [build-system] section
            cmd_install = ["uv", "pip", "install", "--python", str(python_path)] + dependencies

            completed_process = subprocess.run(cmd_install, capture_output=True, text=True)

            if completed_process.returncode != 0:
                error_msg = f"Installing dependencies failed with return code {completed_process.returncode}"
                if completed_process.stderr:
                    error_msg += f"\nStderr: {completed_process.stderr}"
                if completed_process.stdout:
                    error_msg += f"\nStdout: {completed_process.stdout}"
                logger.error(error_msg)
                raise RobotError("unwrap", error_msg)
        else:
            logger.info("No dependencies found in pyproject.toml")

        # Install processcube_robot_agent in the venv so entry points are available
        # This is necessary for robot_runner entry point to work
        # Use editable install from the parent project directory
        logger.info("Installing processcube_robot_agent for entry point support")

        # Find the processcube_robot_agent package in the parent directories
        # It should be installed as editable (-e) in the main project venv
        # For the robot venv, we need to install it from the project root
        project_root = Path().cwd()
        cmd_install_agent = ["uv", "pip", "install", "--python", str(python_path), "-e", str(project_root)]
        completed_process = subprocess.run(cmd_install_agent, capture_output=True, text=True)

        if completed_process.returncode != 0:
            error_msg = f"Installing processcube_robot_agent failed with return code {completed_process.returncode}"
            if completed_process.stderr:
                error_msg += f"\nStderr: {completed_process.stderr}"
            if completed_process.stdout:
                error_msg += f"\nStdout: {completed_process.stdout}"
            logger.error(error_msg)
            raise RobotError("unwrap", error_msg)

        return completed_process

    def _get_entry_point_from_pyproject(self, pyproject_path: Path) -> str:
        """Extract entry point name from pyproject.toml [project.scripts].

        Args:
            pyproject_path: Path to pyproject.toml

        Returns:
            Entry point name (e.g., 'robot_runner') if found, None otherwise
        """
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib  # type: ignore
            except ImportError:
                logger.debug("tomllib/tomli not available - skipping entry point detection")
                return None

        try:
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
                scripts = data.get("project", {}).get("scripts", {})
                if scripts:
                    # Return first entry point name (usually there's only one)
                    return list(scripts.keys())[0]
        except Exception as e:
            logger.debug(f"Failed to parse entry point from pyproject.toml: {e}")

        return None

    def run_robot(self) -> subprocess.CompletedProcess:
        """Execute robot using UV via entry point from pyproject.toml.

        Robots must define [project.scripts] in pyproject.toml with an entry point.
        The entry point should reference a Python function that handles work items.

        Example pyproject.toml:
            [project.scripts]
            robot_runner = "processcube_robot_agent.tools.robot_runner:main"

        Returns:
            Completed process from UV run command.

        Raises:
            RobotError: If robot execution fails or entry point not configured.
        """
        unwrapped_path = self.get_unwrapped_path()
        venv_path = unwrapped_path.joinpath('.venv')
        pyproject_path = unwrapped_path.joinpath('pyproject.toml')

        # Extract entry point from pyproject.toml
        if not pyproject_path.exists():
            raise RobotError(
                "run_robot",
                f"pyproject.toml not found in {unwrapped_path}. "
                f"Robots must define [project.scripts] entry point in pyproject.toml"
            )

        entry_point = self._get_entry_point_from_pyproject(pyproject_path)
        if not entry_point:
            raise RobotError(
                "run_robot",
                f"No entry point found in [project.scripts] in {pyproject_path}. "
                f"Please define an entry point like: robot_runner = 'your_module:main'"
            )

        logger.info(f"Executing robot via entry point: {entry_point}")
        cmd = ["uv", "run", "--python", str(venv_path / "bin" / "python"), entry_point]

        completed_process = subprocess.run(cmd, capture_output=True, text=True, cwd=str(unwrapped_path))

        if completed_process.returncode != 0:
            # Combine stdout and stderr for better error diagnostics
            error_output = ""
            if completed_process.stdout:
                error_output += f"STDOUT:\n{completed_process.stdout}\n"
            if completed_process.stderr:
                error_output += f"STDERR:\n{completed_process.stderr}\n"
            if not error_output:
                error_output = f"Robot execution failed with return code {completed_process.returncode} but no output was captured."

            raise RobotError(f"return_code_{completed_process.returncode}", error_output)

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

        logger.info(f"Starting robot execution for task {task.get('id')} with filename {self._filename}")

        self.check_uv()
        logger.info("UV availability check passed")

        with tempfile.TemporaryDirectory() as tmpdirname:
            logger.info(f"Creating input data in {tmpdirname}")
            self.create_input_data(tmpdirname, payload, task)

            logger.info(f"Unwrapping robot from {self.get_robot_filename()}")
            self.unwrap()
            logger.info(f"Robot unwrapped to {self.get_unwrapped_path()}")

            logger.info("Running robot...")
            self.run_robot()
            logger.info("Robot execution completed successfully")

            logger.info("Reading output data...")
            result = self.read_output_data(tmpdirname, task)

        return result
