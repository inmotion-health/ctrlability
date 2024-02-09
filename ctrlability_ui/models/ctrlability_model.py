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
        log.debug(f"--------------Updating state: {key} = {value}")
        self.state[key] = value
        self.save_state()
        if key == "cam_selected_index":
            self.update_processingunit_dict(["mapping", "VideoStream", "args", "webcam_id"], value)
        CtrlAbilityStateObserver.notify(self.state)

    # def update_processingunit_dict(self, path, value):
    #     # Updates the config dictionary based on a given path.
    #     # e.g. update_config(['mapping', 'VideoStream', 'args', 'webcam_id'], 1)

    #     from ctrlability.core.config_parser import ConfigParser

    #     self.config = ConfigParser().get_config_as_dict()
    #     temp_config = self.config

    #     for key in path[:-1]:  # Gehe zum vorletzten Schlüssel
    #         temp_config = temp_config[key]
    #     temp_config[path[-1]] = value  # Setze den neuen Wert

    #     print(self.config)

    #     self.save_config(self.config)

    def update_processingunit_dict(self, path, value):
        from ctrlability.core.config_parser import ConfigParser

        self.config = ConfigParser().get_config_as_dict()

        print(self.config)

        # Use a temporary pointer to navigate the dictionary without altering the original reference
        temp_config = self.config
        for key in path[:-1]:  # Navigate to the target container
            if key not in temp_config:
                # Optionally, handle missing keys (e.g., by creating them or logging an error)
                print(f"Key {key} not found in configuration.")
                return
            temp_config = temp_config[key]

        # Update the target value
        if path[-1] in temp_config:
            temp_config[path[-1]] = value
        else:
            # Optionally, handle the case where the final key is not found
            print(f"Final key {path[-1]} not found in configuration.")
            return

        # Save the updated configuration
        self.save_config(self.config)
