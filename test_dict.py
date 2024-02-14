test_dict = {
    "version": 1.2,
    "mapping": {
        "VideoStream": {
            "args": {"webcam_id": 0},
            "processors": [
                {
                    "FaceLandmarkProcessor": {
                        "triggers": [
                            {
                                "RegionOfInterest": {
                                    "args": {"position": [0, 0], "size": [0.3, 0.3], "landmarks": [1]},
                                    "action": ["Logger"],
                                }
                            },
                            {
                                "LandmarkDistance": {
                                    "args": {"landmarks": [12, 15], "threshold": 0.02},
                                    "action": [{"MouseClick": {"args": {"key_name": "left_down"}}}],
                                }
                            },
                            {
                                "LandmarkDistance": {
                                    "args": {"landmarks": [12, 15], "threshold": 0.02, "direction": "smaller"},
                                    "action": [{"MouseClick": {"args": {"key_name": "left_up"}}}],
                                }
                            },
                            {
                                "LandmarkDistance": {
                                    "args": {"landmarks": [61, 291], "threshold": 0.09, "direction": "smaller"},
                                    "action": [{"MouseClick": {"args": {"key_name": "right"}}}],
                                }
                            },
                        ],
                        "processors": [
                            {
                                "LandmarkEuroFilter": {
                                    "args": {"min_cutoff": 1, "beta": 0},
                                    "triggers": [
                                        {
                                            "RelativeCursorControl": {
                                                "args": {
                                                    "x_threshold": 0.02,
                                                    "y_threshold": 0.03,
                                                    "velocity_compensation_x": 0.05,
                                                    "velocity_compensation_y": 0.5,
                                                },
                                                "action": ["MoveMouse"],
                                            }
                                        }
                                    ],
                                }
                            }
                        ],
                    }
                }
            ],
        }
    },
}

# my_dict = {"level1": {"level2": {"level3": "target_value"}}}
# my_dict["level1"]["level2"]["level3"] = "new_value"
# test_dict["mapping"]["VideoStream"]["processors"]["FaceLandmarkProcessor"],["triggers"] "LandmarkDistance", "args", "threshold"], value


def update_processingunit_dict(path, value):
    # Updates the config dictionary based on a given path.
    # e.g. update_config(['mapping', 'VideoStream', 'args', 'webcam_id'], 1)

    from ctrlability.core.config_parser import ConfigParser

    self.config = ConfigParser().get_config_as_dict()
    temp_config = self.config

    for key in path[:-1]:  # Gehe zum vorletzten Schlüssel
        temp_config = temp_config[key]
    temp_config[path[-1]] = value  # Setze den neuen Wert
    print("//////////////////////////")
    print(self.config)


def main():

    print("*******************************")
    print(test_dict)
    print("*******************************")

    print(
        test_dict["mapping"]["VideoStream"]["processors"][0]["FaceLandmarkProcessor"]["triggers"][1][
            "LandmarkDistance"
        ]["args"]["threshold"]
    )

    test_dict["mapping"]["VideoStream"]["processors"][0]["FaceLandmarkProcessor"]["triggers"][1]["LandmarkDistance"][
        "args"
    ]["threshold"] = -999

    print("*******************************")
    print(test_dict)
    print("*******************************")

    # for k, v in test_dict.items():
    #     if isinstance(v, dict):
    #         print(v)
    #     else:
    #         print("{0} : {1}".format(k, v))


if __name__ == "__main__":
    main()
