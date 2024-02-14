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
        log.debug("---------------Saving config...")
        log.debug(config)
        try:
            with open("config.yaml", "w") as file:
                self.yaml.dump(config, file)
                log.debug("---------------Config saved.")
        except Exception as e:
            log.error(f"Failed to save config: {e}")

    def update_state(self, key, value):
        from ctrlability.core.config_parser import ConfigParser

        config = ConfigParser().get_config_as_dict()
        log.debug(f"--------------Updating state in model: {key} = {value}")

        if key == "side_menu_selected_index":
            return

        if key == "cam_selected_index":
            config["mapping"]["VideoStream"]["args"]["webcam_id"] = value
        elif key == "distance1_threshold":
            config["mapping"]["VideoStream"]["processors"][0]["FaceLandmarkProcessor"]["triggers"][1][
                "LandmarkDistance"
            ]["args"]["threshold"] = value

        # expression settings
        elif key == "expression1":
            config["mapping"]["VideoStream"]["processors"][0]["FacialExpressionClassifier"]["processors"][0][
                "SignalDivider"
            ]["triggers"][0]["FacialExpressionTrigger"]["args"]["name"] = value[0]
            if value[2][0] == "key":
                config["mapping"]["VideoStream"]["processors"][0]["FacialExpressionClassifier"]["processors"][0][
                    "SignalDivider"
                ]["triggers"][0]["FacialExpressionTrigger"]["action"][0]["KeyCommand"]["args"]["command"] = value[2]
            elif value[2][0] == "mouse":
                config["mapping"]["VideoStream"]["processors"][0]["FacialExpressionClassifier"]["processors"][0][
                    "SignalDivider"
                ]["triggers"][0]["FacialExpressionTrigger"]["action"][0]["MouseClick"]["args"]["key_name"] = value[2]
            else:
                log.error(f"Invalid action type: {value[2][0]}")

        # mouse settings
        elif key == "mouse_settings_velocity_compensation_x":
            config["mapping"]["VideoStream"]["processors"][0]["processors"][1]["processors"][0]["triggers"][0]["args"][
                "compensation_x"
            ] = value
        elif key == "mouse_settings_velocity_compensation_y":
            config["mapping"]["VideoStream"]["processors"][0]["processors"][1]["processors"][0]["triggers"][0]["args"][
                "compensation_y"
            ] = value
        elif key == "mouse_settings_x_threshold":
            config["mapping"]["VideoStream"]["processors"][0]["processors"][1]["processors"][0]["triggers"][0]["args"][
                "x_threshold"
            ] = value
        elif key == "mouse_settings_y_threshold":
            config["mapping"]["VideoStream"]["processors"][0]["processors"][1]["processors"][0]["triggers"][0]["args"][
                "y_threshold"
            ] = value

        log.debug("---------------Updated config...")
        log.debug(config)

        self.state[key] = value
        self.save_state()
        self.save_config(config)
        CtrlAbilityStateObserver.notify(self.state)
