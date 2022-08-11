import subprocess

from ..error import RobotError

class RccRunner:
    def check_rcc(self):

        cmd = f"rcc version"

        completed_process = subprocess.run(cmd, shell=True, capture_output=True)

        if completed_process.returncode != 0:
            raise RobotError("rcc", f"rcc --version failed with return code {completed_process.returncode}")

        return completed_process
