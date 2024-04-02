import os
import sys
import subprocess, shlex


class Command:
    """a class to invoke commands in a chained manner"""

    def __init__(self, cmd : [str, list[str]]):
        if isinstance(cmd, str):
            cmd = shlex.split(cmd)
        assert isinstance(cmd, list), "invalid input type"
        self.cmd = cmd
        self.result = subprocess.run(cmd)

    def __bool__(self):
        return self.result.returncode == 0

    def __repr__(self):
        return shlex.join(self.cmd)

