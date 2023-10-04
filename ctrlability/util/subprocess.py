import importlib
from typing import List
subprocess = importlib.import_module('subprocess')


def get_cmd_output(args: List[str]) -> str:
    try:
        output = subprocess.check_output(
            args,
            stderr=subprocess.STDOUT,
        ).decode("utf-8")
    except subprocess.CalledProcessError as e:
        output = e.output.decode("utf-8")
    return output
