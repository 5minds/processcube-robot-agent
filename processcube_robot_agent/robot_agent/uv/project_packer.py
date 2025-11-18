import logging
from pathlib import Path
import subprocess
import zipfile

from processcube_sdk.configuration import Config

from .uv_runner import UvRunner

logger = logging.getLogger("processcube_robot_agent.robot_agent.project_packer")


class ProjectPacker(UvRunner):
    """Packs Python robot projects into installable ZIP packages.

    Uses UV to manage dependencies and creates distributable .zip packages
    containing the robot code and uv.lock file for reproducible installs.
    """

    def __init__(self, config: Config) -> None:
        """Initialize ProjectPacker.

        Args:
            config: ProcessCube configuration object.
        """
        self._config = config
        self._absolute_project_dir = Path(self._config.get('uv', 'project_dir')).absolute()
        self._wrap_dir = Path(self._config.get('uv', 'wrap_dir')).absolute()

    def _find_pyproject_toml(self, start_path: Path) -> Path:
        """Find pyproject.toml file in directory hierarchy.

        Args:
            start_path: Directory to start search from.

        Returns:
            Path to pyproject.toml if found.

        Raises:
            FileNotFoundError: If pyproject.toml is not found.
        """
        current = start_path if start_path.is_dir() else start_path.parent
        
        while current >= self._absolute_project_dir:
            pyproject = current / "pyproject.toml"
            if pyproject.exists():
                return pyproject
            current = current.parent
        
        raise FileNotFoundError(f"pyproject.toml not found in {start_path} or parent directories")

    def pack_folder(self, pyproject_toml_path: Path) -> Path:
        """Pack a single robot project into a ZIP file.

        Args:
            pyproject_toml_path: Path to pyproject.toml file.

        Returns:
            Path to the created .zip package.

        Raises:
            RobotError: If packing fails.
        """
        logger.debug(f"pack robot {pyproject_toml_path}")
        current_folder = pyproject_toml_path.parent

        relative_robot_path = current_folder.relative_to(self._absolute_project_dir)
        wrap_robot_path = self._wrap_dir.joinpath(relative_robot_path)
        wrap_robot_dir = wrap_robot_path.parent

        logger.debug(f"relative_robot_path: {relative_robot_path}")
        logger.debug(f"wrap_robot_path: {wrap_robot_path}")
        logger.debug(f"wrap_robot_dir: {wrap_robot_dir}")

        if not wrap_robot_dir.exists():
            logger.debug(f"create folder {wrap_robot_dir}")
            wrap_robot_dir.mkdir(parents=True, exist_ok=True)

        # Create a ZIP file containing the project
        zip_path = Path(f"{str(wrap_robot_path)}.zip").absolute()

        # Ensure uv.lock exists before packing
        self._ensure_uv_lock(current_folder)

        # Create ZIP file
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                self._add_directory_to_zip(zipf, current_folder, current_folder)
            
            relative_zip_path = wrap_robot_path.relative_to(self._wrap_dir)
            try:
                relative_wrap_dir = self._wrap_dir.relative_to(Path().cwd())
            except ValueError:
                relative_wrap_dir = self._wrap_dir
            
            logger.info(f"Created robot {str(relative_zip_path)}.zip from {str(relative_robot_path)} in {str(relative_wrap_dir)}.")
        except Exception as e:
            logger.error(f"Failed to create ZIP file {zip_path}: {e}")
            raise

        return zip_path

    def _ensure_uv_lock(self, project_dir: Path) -> None:
        """Ensure uv.lock exists in the project directory.

        If uv.lock doesn't exist, create it using 'uv lock' command.

        Args:
            project_dir: Project directory containing pyproject.toml.

        Raises:
            RuntimeError: If uv lock fails.
        """
        uv_lock = project_dir / "uv.lock"
        
        if not uv_lock.exists():
            logger.info(f"Creating uv.lock in {project_dir}")
            cmd = ["uv", "lock"]
            completed_process = subprocess.run(cmd, capture_output=True, text=True, cwd=str(project_dir))
            
            if completed_process.returncode != 0:
                raise RuntimeError(f"Failed to create uv.lock: {completed_process.stderr}")

    def _add_directory_to_zip(self, zipf: zipfile.ZipFile, source_dir: Path, base_dir: Path) -> None:
        """Recursively add directory contents to ZIP file.

        Excludes __pycache__, .venv, and .git directories.

        Args:
            zipf: ZipFile object to add files to.
            source_dir: Current directory to process.
            base_dir: Base directory for relative paths in ZIP.
        """
        exclude_dirs = {'.venv', '__pycache__', '.git', '.pytest_cache', 'htmlcov', '.coverage'}
        
        for path in source_dir.iterdir():
            if path.name in exclude_dirs:
                continue
            
            relative_path = path.relative_to(base_dir)
            
            if path.is_file():
                zipf.write(path, arcname=relative_path)
            elif path.is_dir():
                self._add_directory_to_zip(zipf, path, base_dir)

    def pack_all(self, absolute_start_folder: Path) -> None:
        """Recursively pack all robot projects in a folder.

        Args:
            absolute_start_folder: Root folder to search for pyproject.toml files.
        """
        for pyproject_path in absolute_start_folder.rglob('pyproject.toml'):
            # Skip if this is in an excluded directory
            if any(part in {'.venv', '__pycache__', '.git'} for part in pyproject_path.parts):
                continue
            
            try:
                self.pack_folder(pyproject_path)
            except Exception as e:
                logger.error(f"Failed to pack {pyproject_path}: {e}", exc_info=True)

    def start(self) -> None:
        """Start the packing process.

        Checks UV availability and packs all robots
        in the configured project directory.
        """
        self.check_uv()
        self.pack_all(self._absolute_project_dir)
