from yaml import load, Loader
import logging

log = logging.getLogger(__name__)


class ConfigParser:
    CONFIG_PATH = "config.yaml"

    def __init__(self, config_path=None):
        if config_path is not None:
            self.CONFIG_PATH = config_path

        log.debug(f"Config path set to {config_path}")

    def validate(self, config: dict):
        # TODO: validate config
        pass

    def parse(self):
        with open(self.CONFIG_PATH) as f:
            config: dict = load(f, Loader=Loader)

            return config.get("mapping")
