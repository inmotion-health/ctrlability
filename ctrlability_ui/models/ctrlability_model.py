import logging
import re
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedSeq
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
        from ctrlability.core.config_parser import ConfigParser

        log.debug("---------------Saving config...")
        log.debug(config)
        try:
            with open(ConfigParser.CONFIG_PATH, "w") as file:
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

        # ------ CAM CHANGED ------
        if key == "cam_selected_index":
            config["mapping"]["VideoStream"]["args"]["webcam_id"] = value

        # ------ TEST LANDMARK DISTANCE ------
        if key == "distance1_threshold":
            config["mapping"]["VideoStream"]["processors"][0]["FaceLandmarkProcessor"]["triggers"][1][
                "LandmarkDistance"
            ]["args"]["threshold"] = value

        # ------ EXPRESSION COMPONENT CHANGED ------
        if key.__contains__("expression"):
            expression_id = int(re.split("_", key)[1]) - 1
            # change the expression name
            config["mapping"]["VideoStream"]["processors"][0]["FacialExpressionClassifier"]["processors"][0][
                "SignalDivider"
            ]["triggers"][expression_id]["FacialExpressionTrigger"]["args"]["name"] = value[0]
            # change the expression confidence
            config["mapping"]["VideoStream"]["processors"][0]["FacialExpressionClassifier"]["processors"][0][
                "SignalDivider"
            ]["triggers"][expression_id]["FacialExpressionTrigger"]["args"]["confidence"] = value[1]
            if value[2][0] == "key":
                # change the key command
                config["mapping"]["VideoStream"]["processors"][0]["FacialExpressionClassifier"]["processors"][0][
                    "SignalDivider"
                ]["triggers"][expression_id]["FacialExpressionTrigger"]["action"][0] = {
                    "KeyCommand": {"args": {"command": value[2][1]}}
                }
            elif value[2][0] == "mouse":
                # change the mouse click
                config["mapping"]["VideoStream"]["processors"][0]["FacialExpressionClassifier"]["processors"][0][
                    "SignalDivider"
                ]["triggers"][expression_id]["FacialExpressionTrigger"]["action"][0] = {
                    "MouseClick": {"args": {"key_name": value[2][1]}}
                }
            else:
                log.error(f"Invalid action type: {value[2][0]}")
                return

        # ------ MOUSE SETTINGS ------
        if key == "mouse_settings":
            if value[0] == "relative":
                print("----------relative")
                config["mapping"]["VideoStream"]["processors"][0]["FacialExpressionClassifier"]["processors"][1][
                    "SignalDivider"
                ]["processors"][0]["LandmarkEuroFilter"]["triggers"][0] = {
                    "RelativeCursorControl": {
                        "args": {
                            "x_threshold": float(value[1]),
                            "y_threshold": float(value[2]),
                            "velocity_compensation_x": float(value[3]),
                            "velocity_compensation_y": float(value[4]),
                        },
                        "action": ["MoveMouse"],
                    }
                }
            elif value[0] == "absolute":
                print("----------absolute")
                config["mapping"]["VideoStream"]["processors"][0]["FacialExpressionClassifier"]["processors"][1][
                    "SignalDivider"
                ]["processors"][0]["LandmarkEuroFilter"]["triggers"][0] = [
                    {
                        "LandmarkNormalVector": {
                            "args": {"landmark": 1, "ref_landmarks": [33, 263, 61, 291, 199], "tip_scale": 4},
                            "triggers": [{"AbsoluteCursorControl": {"action": ["MoveMouse"]}}],
                        }
                    }
                ]

        log.debug("---------------Updated config...")
        log.debug(config)

        self.state[key] = value
        self.save_state()
        self.save_config(config)
        CtrlAbilityStateObserver.notify(self.state)
