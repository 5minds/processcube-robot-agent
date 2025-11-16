import subprocess

from ..error import RobotError

class RccRunner:
    def check_rcc(self):

        cmd = ["rcc", "version"]

        completed_process = subprocess.run(cmd, capture_output=True, text=True)

        if completed_process.returncode != 0:
            raise RobotError("rcc", f"rcc version failed with return code {completed_process.returncode}\nStderr: {completed_process.stderr}")

        return completed_process
