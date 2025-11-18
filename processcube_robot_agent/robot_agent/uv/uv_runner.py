import subprocess

from ..error import RobotError


class UvRunner:
    """Base class for UV (Python package manager) operations."""

    def check_uv(self) -> subprocess.CompletedProcess:
        """Check if UV is installed and available.

        Returns:
            Completed process from UV self version command.

        Raises:
            RobotError: If UV is not available or check fails.
        """
        cmd = ["uv", "self", "version"]

        completed_process = subprocess.run(cmd, capture_output=True, text=True)

        if completed_process.returncode != 0:
            raise RobotError("uv", f"uv self version failed with return code {completed_process.returncode}\nStderr: {completed_process.stderr}")

        return completed_process
