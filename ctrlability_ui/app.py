import logging
import sys
import subprocess
import platform

from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet

import ctrlability.util.printing as printing
from ctrlability.util.argparser import parse_arguments

from ctrlability_ui.controllers.ctrlability_controller import CtrlAbilityController
from ctrlability_ui.models.ctrlability_model import CtrlAbilityModel
from ctrlability_ui.views.ctrlability_view import CtrlAbilityView

log = logging.getLogger(__name__)



def check_appearance():
    """Checks DARK/LIGHT mode of macos."""
    cmd = "defaults read -g AppleInterfaceStyle"
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    return bool(p.communicate()[0])


def runAPP():
    # initialize gui
    # ToDo: fix in deployment: currently development hack to show application name in menu bar
    if sys.platform == "darwin":
        from Foundation import NSBundle

        app_info = NSBundle.mainBundle().infoDictionary()
        app_info["CFBundleName"] = "CTRLABILITY"

    app = QApplication(sys.argv)
    app.setApplicationName("CTRLABILITY")  # Set the application name
    # app.setQuitOnLastWindowClosed(False)  # Keep the app running even if all windows are closed

    theme = "light_blue.xml"
    if platform.system() == "Darwin":
        if check_appearance():
            theme = "dark_blue.xml"
    apply_stylesheet(app, theme=theme)

    model = CtrlAbilityModel()
    view = CtrlAbilityView()
    controller = CtrlAbilityController(model, view)
    view.show()

    app.aboutToQuit.connect(controller.close)

    sys.exit(app.exec())


def setupParser():
    # set the config file path from the arguments
    from ctrlability.core.config_parser import ConfigParser

    ConfigParser.CONFIG_PATH = args.config_file


if __name__ == "__main__":
    args = parse_arguments()

    setupParser()
    runAPP()
