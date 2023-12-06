from yaml import load, Loader


class ConfigParser:
    CONFIG_PATH = "config.yaml"

    def __init__(self, config_path=None):
        if config_path is not None:
            self.CONFIG_PATH = config_path

    def validate(self, config: dict):
        pass

    def parse(self):
        with open(self.CONFIG_PATH) as f:
            config: dict = load(f, Loader=Loader)
            # self.validate(config)
            return config.get("mapping")
