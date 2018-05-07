import subprocess
from typing import List
from typing import Tuple


def run_command(args: List[str]) -> Tuple[str, str]:
    proc = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf8",
    )
    return proc.communicate()
