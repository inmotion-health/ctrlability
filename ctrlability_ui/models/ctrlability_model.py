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

        try:
            with open(ConfigParser.CONFIG_PATH, "w") as file:
                self.yaml.dump(config, file)
                log.debug("Config saved.")
        except Exception as e:
            log.error(f"Failed to save config: {e}")

    def update_state(self, category, key, value):
        from ctrlability.core.config_parser import ConfigParser

        config = ConfigParser().get_config_as_dict()

        log.debug(f"Updating state in model: {key} = {value}")

        if key == "side_menu_selected_index":
            return

        if category == "head_face":
            # ------ CAM CHANGED ------
            if key == "cam_selected_index":
                config["mapping"][0]["VideoStream"]["args"]["webcam_id"] = value

            # ------ TEST LANDMARK DISTANCE ------
            if key == "distance1_threshold":
                config["mapping"][0]["VideoStream"]["processors"][0]["FaceLandmarkProcessor"]["triggers"][1][
                    "LandmarkDistance"
                ]["args"]["threshold"] = value

            # ------ EXPRESSION COMPONENT CHANGED ------
            if key.__contains__("expression"):
                expression_id = int(re.split("_", key)[1]) - 1
                # change the expression name
                config["mapping"][0]["VideoStream"]["processors"][0]["FacialExpressionClassifier"]["processors"][0][
                    "SignalDivider"
                ]["triggers"][expression_id]["FacialExpressionTrigger"]["args"]["name"] = value[0]
                # change the expression confidence
                config["mapping"][0]["VideoStream"]["processors"][0]["FacialExpressionClassifier"]["processors"][0][
                    "SignalDivider"
                ]["triggers"][expression_id]["FacialExpressionTrigger"]["args"]["confidence"] = value[1]
                if value[2][0] == "key":
                    # change the key command
                    config["mapping"][0]["VideoStream"]["processors"][0]["FacialExpressionClassifier"]["processors"][0][
                        "SignalDivider"
                    ]["triggers"][expression_id]["FacialExpressionTrigger"]["action"][0] = {
                        "KeyCommand": {"args": {"command": value[2][1]}}
                    }
                elif value[2][0] == "mouse":
                    # change the mouse click
                    config["mapping"][0]["VideoStream"]["processors"][0]["FacialExpressionClassifier"]["processors"][0][
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
                    try:
                        x_threshold = float(value[1])
                        y_threshold = float(value[2])
                        velocity_compensation_x = float(value[3])
                        velocity_compensation_y = float(value[4])
                    except ValueError:
                        log.debug("ERROR – Mouse Settings – Cannot convert to float.")

                    config["mapping"][0]["VideoStream"]["processors"][0]["FacialExpressionClassifier"]["processors"][1][
                        "SignalDivider"
                    ]["processors"][0] = {
                        "LandmarkEuroFilter": {
                            "args": {"min_cutoff": 1, "beta": 0},
                            "triggers": [
                                {
                                    "RelativeCursorControl": {
                                        "args": {
                                            "x_threshold": x_threshold,
                                            "y_threshold": y_threshold,
                                            "velocity_compensation_x": velocity_compensation_x,
                                            "velocity_compensation_y": velocity_compensation_y,
                                        },
                                        "action": ["MoveMouse"],
                                    }
                                }
                            ],
                        }
                    }
                elif value[0] == "absolute":
                    config["mapping"][0]["VideoStream"]["processors"][0]["FacialExpressionClassifier"]["processors"][1][
                        "SignalDivider"
                    ]["processors"][0] = {
                        "LandmarkEuroFilter": {
                            "args": {"min_cutoff": 1, "beta": 0},
                            "processors": [
                                {
                                    "LandmarkNormalVector": {
                                        "args": {
                                            "landmark": 1,
                                            "ref_landmarks": [33, 263, 61, 291, 199],
                                            "tip_scale": 4,
                                        },
                                        "triggers": [{"AbsoluteCursorControl": {"action": ["MoveMouse"]}}],
                                    }
                                }
                            ],
                        }
                    }
        self.state.setdefault(category, {})[key] = value
        self.save_state()
        self.save_config(config)
        CtrlAbilityStateObserver.notify(self.state)
