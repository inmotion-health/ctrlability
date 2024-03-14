from ctrlability_ui.app import runAPP
import sys
import os


try:
    with open("/Users/sandi/codespace/ctrlability/error.log", "a") as f:
        f.write(f"PATH: {str(os.environ['PATH'])}\n")
    runAPP()
except Exception as e:
    with open("/Users/sandi/codespace/ctrlability/error.log", "a") as f:
        f.write(f"Error: {str(e)}\n")
