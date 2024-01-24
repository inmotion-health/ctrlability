import time

from ctrlability.core import Processor, bootstrapper, MappingEngine
from ctrlability.math.one_euro_filter import OneEuroFilter


@bootstrapper.add()
class LandmarkEuroFilter(Processor):
    def __init__(self, mapping_engine: MappingEngine, min_cutoff=1.0, beta=0.0, d_cutoff=1.0):
        super().__init__(mapping_engine)
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff

        self.filters_x = []
        self.filters_y = []
        self.initialized = False

    def compute(self, landmarks):
        if landmarks is None:
            return

        if not self.initialized:
            t = time.time()

            for i, landmark in enumerate(landmarks):
                self.filters_x.append(
                    OneEuroFilter(t, landmark.x, min_cutoff=self.min_cutoff, beta=self.beta, d_cutoff=self.d_cutoff)
                )
                self.filters_y.append(
                    OneEuroFilter(t, landmark.y, min_cutoff=self.min_cutoff, beta=self.beta, d_cutoff=self.d_cutoff)
                )
            self.initialized = True

        # overwrite landmarks and apply filter to each landmark
        for i, landmark in enumerate(landmarks):
            landmark.x = self.filters_x[i](time.time(), landmark.x)
            landmark.y = self.filters_y[i](time.time(), landmark.y)

        return landmarks
