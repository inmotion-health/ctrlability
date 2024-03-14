import os
import sys


def resource_path(*relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, *relative_path)
    print(f"relative_path: {relative_path}")
    print(os.path.join(os.path.abspath("."), *relative_path))
    return os.path.join(os.path.abspath("."), *relative_path)


os.environ["PATH"] = resource_path("lib") + ":" + os.environ["PATH"]
