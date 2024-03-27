import os
import sys

print(os.getcwd())
current_path = os.getcwd()
error_log = f"{current_path}/error.log"

def resource_path(*relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, *relative_path)
    print(f"relative_path: {relative_path}")
    print(os.path.join(os.path.abspath("."), *relative_path))
    with open(error_log, "a") as f:
        f.write(f"From resource_path\n")
        f.write(f"meipass: {sys._MEIPASS}\n")
        f.write(f"relative_path: {relative_path}\n")
        f.write(f"os.path.abspath('.'): {os.path.abspath('.')}\n")
        f.write(f"os.path.join(os.path.abspath('.'), *relative_path): {os.path.join(os.path.abspath('.'), *relative_path)}\n")
    return os.path.join(os.path.abspath("."), *relative_path)


os.environ["PATH"] = resource_path("lib") + os.pathsep + os.environ["PATH"]

with open(error_log, "a") as f:
    f.write(f"From hook\n")
    f.write(f"PATH: {str(os.environ['PATH'])}\n")
    f.write(f"From resource_path\n")
    f.write(f"meipass: {sys._MEIPASS}\n")
    f.write(f"os.path.abspath('.'): {os.path.abspath('.')}\n")
