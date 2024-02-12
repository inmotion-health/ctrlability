import logging
from ruamel.yaml import YAML
from ctrlability_ui.patterns.state_observer import CtrlAbilityStateObserver

log = logging.getLogger(__name__)


class CtrlAbilityModel:
    def __init__(self):
        self.state = {}
        self.config = {}
        self.yaml = YAML()
        self.yaml.preserve_quotes = True

    def load_state(self):
        try:
            with open("project_state.yaml", "r") as file:
                self.state = self.yaml.load(file) or {}
        except FileNotFoundError:
            self.state = {}

    def save_state(self):
        with open("project_state.yaml", "w") as file:
            self.yaml.dump(self.state, file)

    def save_config(self, config):
        print("---------------Saving config...")
        print(config)
        try:
            with open("config.yaml", "w") as file:
                self.yaml.dump(config, file)
            # If an exception was not raised, the dump was successful
        except Exception as e:
            # Handle any errors that occurred during the file operation
            log.error(f"Failed to save config: {e}")

        print("---------------Config saved.")

    def update_state(self, key, value):
        from ctrlability.core.config_parser import ConfigParser

        config = ConfigParser().get_config_as_dict()

        log.debug(f"--------------Updating state: {key} = {value}")
        self.state[key] = value

        if key == "cam_selected_index":
            config["mapping", "VideoStream", "args", "webcam_id"] = value
        elif key == "distance1_threshold":
            config["mapping"]["VideoStream"]["processors"][0]["FaceLandmarkProcessor"]["triggers"][1][
                "LandmarkDistance"
            ]["args"]["threshold"] = value

        self.save_state()
        self.save_config(config)
        CtrlAbilityStateObserver.notify(self.state)
