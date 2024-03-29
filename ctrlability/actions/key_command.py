import pyautogui

from ctrlability.core import Action, bootstrapper


@bootstrapper.add()
class KeyCommand(Action):
    """
    Represents a key command action.

    Args:
        command (list): A list of strings representing the keys to be pressed.
    """

    def __init__(self, command):
        self.command = command

        # verify that the command is an array of strings
        if not isinstance(self.command, list):
            raise TypeError("command must be a list of strings")

    def execute(self, data):
        pyautogui.hotkey(self.command)

    def __repr__(self):
        return f"KeyCommand(command: {self.command})"
