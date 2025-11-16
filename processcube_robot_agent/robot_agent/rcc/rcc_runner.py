import subprocess

from ..error import RobotError


class RccRunner:
    """Base class for RCC (Robot Code Compiler) operations."""

    def check_rcc(self) -> subprocess.CompletedProcess:
        """Check if RCC is installed and available.

        Returns:
            Completed process from RCC version command.

        Raises:
            RobotError: If RCC is not available or check fails.
        """
        cmd = ["rcc", "version"]

        completed_process = subprocess.run(cmd, capture_output=True, text=True)

        if completed_process.returncode != 0:
            raise RobotError("rcc", f"rcc version failed with return code {completed_process.returncode}\nStderr: {completed_process.stderr}")

        return completed_process
