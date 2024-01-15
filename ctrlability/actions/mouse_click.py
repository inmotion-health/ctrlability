from ctrlability.core import Action, bootstrapper


@bootstrapper.add()
class MouseClick(Action):
    def __init__(self, key_name):
        self.key = key_name

    def execute(self, data):
        print(f"triggered: {self.key} with {data}")

    def __repr__(self):
        return f"MouseClick(key: {self.key})"
