from ctrlability.core import Trigger, bootstrapper


@bootstrapper.add()
class FacialExpressionTrigger(Trigger):
    """
    A trigger that detects facial expressions based on blendshape names and confidence levels.

    Inputs:
        data: The list of blendshapes detected in the frame.

    Returns:
        dict: The detected blendshape and the confidence level.

    Args:
        name (str): The name of the blendshape to detect.
        confidence (float, optional): The confidence level required to trigger the expression. Defaults to 0.5.
        trigger_once (bool, optional): Whether the trigger should only be activated once. Defaults to True.
    """

    def __init__(self, name: str, confidence: float = 0.5, trigger_once: bool = True):
        self.blendshape_name = name
        self.confidence_level = confidence
        self.trigger_once = trigger_once
        self.triggered = False
        self.score = 0.0

    def check(self, data) -> dict | None:
        if data is None:
            return None

        for category in data:
            self.score = category.score
            if category.category_name == self.blendshape_name:
                if category.score >= self.confidence_level:
                    if self.trigger_once and self.triggered:
                        return None

                    self.triggered = True
                    return {"trigger": self.blendshape_name, "score": category.score}

                self.triggered = False

        return None
