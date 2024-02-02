import toml
import os

import ctrlability.streams
import ctrlability.processors
import ctrlability.actions
import ctrlability.triggers


def get_version():
    here = os.path.abspath(os.path.dirname(__file__))
    pyproject_path = os.path.join(here, "..", "pyproject.toml")
    with open(pyproject_path, "r") as pyproject:
        pyproject_data = toml.load(pyproject)
    return pyproject_data["project"]["version"]


__version__ = get_version()


__all__ = ["__version__"]
