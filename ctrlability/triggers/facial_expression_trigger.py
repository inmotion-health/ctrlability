from ctrlability.core import Trigger, bootstrapper


@bootstrapper.add()
class FacialExpressionTrigger(Trigger):
    def __init__(self, name: str, confidence: float = 0.5, trigger_once: bool = True):
        self.blendshape_name = name
        self.confidence_level = confidence
        self.trigger_once = trigger_once
        self.triggered = False

    def check(self, data) -> dict | None:
        if data is None:
            return None

        for category in data:
            if category.category_name == self.blendshape_name:
                if category.score >= self.confidence_level:
                    if self.trigger_once and self.triggered:
                        return None

                    self.triggered = True
                    return {"trigger": self.blendshape_name, "score": category.score}

                self.triggered = False

        return None
