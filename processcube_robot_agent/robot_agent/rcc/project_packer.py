
import logging
from pathlib import Path
import subprocess

from processcube_sdk.configuration import Config

from .rcc_runner import RccRunner

logger = logging.getLogger("processcube_robot_agent.robot_agent.project_packer")


class ProjectPacker(RccRunner):
    """Packs robot projects into installable ZIP packages.

    Uses RCC (Robot Code Compiler) to wrap robot projects
    into distributable .zip packages.
    """

    def __init__(self, config: Config) -> None:
        """Initialize ProjectPacker.

        Args:
            config: ProcessCube configuration object.
        """
        self._config = config
        self._absolute_project_dir = Path(self._config.get('rcc', 'project_dir')).absolute()
        self._wrap_dir = Path(self._config.get('rcc', 'wrap_dir')).absolute()

    def pack_folder(self, robot_yaml_path: Path) -> Path:
        """Pack a single robot project into a ZIP file.

        Args:
            robot_yaml_path: Path to robot.yaml file.

        Returns:
            Path to the created .zip package.
        """
        logger.debug(f"pack robot {robot_yaml_path}")
        current_folder = robot_yaml_path.parent

        relative_robot_path = current_folder.relative_to(self._absolute_project_dir)
        wrap_robot_path = self._wrap_dir.joinpath(relative_robot_path)
        wrap_robot_dir = wrap_robot_path.parent

        logger.debug(f"relative_robot_path: {relative_robot_path}")
        logger.debug(f"wrap_robot_path: {wrap_robot_path}")
        logger.debug(f"wrap_robot_dir: {wrap_robot_dir}")

        if not wrap_robot_dir.exists():
            logger.debug(f"create folder {wrap_robot_dir}")
            wrap_robot_dir.mkdir(parents=True)

        # rcc robot wrap --directory windows/ui --zipfile ../../installed/rcc/windows/ui.zip
        relative_wrap_robot_path = wrap_robot_path.relative_to(self._wrap_dir)
        cmd = ["rcc", "robot", "wrap", "--directory", str(relative_robot_path), "--zipfile", f"{str(wrap_robot_path)}.zip"]
        logger.info(f"Create robot {str(relative_wrap_robot_path)}.zip from {str(relative_robot_path)} in {str(self._wrap_dir.relative_to(Path().cwd()))}.")

        completed_process = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self._absolute_project_dir))

        logger.debug(f"'{cmd}' finished with '{completed_process.returncode}'")

        return Path(f"{str(wrap_robot_path)}.zip").absolute()

    def pack_all(self, absolute_start_folder: Path) -> None:
        """Recursively pack all robot projects in a folder.

        Args:
            absolute_start_folder: Root folder to search for robot.yaml files.
        """
        for robot_yaml_path in absolute_start_folder.rglob('robot.yaml'):
            self.pack_folder(robot_yaml_path)

    def start(self) -> None:
        """Start the packing process.

        Checks RCC availability and packs all robots
        in the configured project directory.
        """
        self.check_rcc()
        self.pack_all(self._absolute_project_dir)