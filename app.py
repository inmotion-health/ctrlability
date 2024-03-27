from ctrlability_ui.app import runAPP
import sys
import os

#get current path 
print(os.getcwd())
current_path = os.getcwd()
error_log = f"{current_path}/error.log"


def resource_path(*relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, *relative_path)
    return os.path.join(os.path.abspath("."), *relative_path)

os.environ["PATH"] = resource_path("lib") + os.pathsep + os.environ["PATH"]

try:
    with open(error_log, "a") as f:
        f.write(f"From app.py\n")
       
        f.write(f"meipass: {sys._MEIPASS}\n")
        f.write(f"PATH: {str(os.environ['PATH'])}\n")
        f.write(f"path {current_path}\n")
    runAPP()
except Exception as e:
    with open(error_log ,"a") as f:
        f.write(f"Error: {str(e)}\n")
