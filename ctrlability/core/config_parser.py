import logging

# from yaml import load, Loader
from ruamel.yaml import YAML

log = logging.getLogger(__name__)


class ConfigParser:
    CONFIG_PATH = "config.yaml"

    def __init__(self, config_path=None):
        if config_path is not None:
            self.CONFIG_PATH = config_path

        self.yaml = YAML()
        self.yaml.preserve_quotes = True  # This is optional

        log.debug(f"Config path set to {ConfigParser.CONFIG_PATH}")

    def validate(self, config: dict):
        # TODO: validate config
        pass

    def parse(self):
        # check if config file exists
        try:
            with open(self.CONFIG_PATH) as f:
                config: dict = self.yaml.load(f)
                return config.get("mapping")
        except FileNotFoundError:
            raise RuntimeError(f"Config file {self.CONFIG_PATH} not found.")

    def get_config_as_dict(self):
        try:
            with open(self.CONFIG_PATH) as f:
                return self.yaml.load(f)
        except FileNotFoundError:
            raise RuntimeError(f"Config file {self.CONFIG_PATH} not found.")
