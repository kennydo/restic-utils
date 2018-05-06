import subprocess
from typing import List


def run_command(args: List[str]) -> (str, str):
    proc = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf8",
    )
    return proc.communicate()
