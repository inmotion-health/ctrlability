import time

from ctrlability.core import Processor, bootstrapper, MappingEngine
from ctrlability.core.data_types import LandmarkData
from ctrlability.math.one_euro_filter import OneEuroFilter


@bootstrapper.add()
class LandmarkEuroFilter(Processor):
    """
    A Processor that takes in a LandmarkData object and applies a one euro filter to each landmark.

    Inputs:
        LandmarkData: The landmarks to which the one euro filter should be applied.

    Returns:
        LandmarkData: The landmarks after applying the one euro filter.

    Args:
        min_cutoff: The minimum cutoff frequency for the one euro filter (default: 1.0).
        beta: The beta value for the one euro filter (default: 0.0).
        d_cutoff: The cutoff frequency for the derivative filter in the one euro filter (default: 1.0).
    """

    def __init__(self, mapping_engine: MappingEngine, min_cutoff=1.0, beta=0.0, d_cutoff=1.0):
        super().__init__(mapping_engine)
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff

        self.filters_x = []
        self.filters_y = []
        self.initialized = False

    def compute(self, landmark_data: LandmarkData):
        if landmark_data.landmarks is None:
            return

        if not self.initialized:
            t = time.time()

            for i, landmark in enumerate(landmark_data.landmarks):
                self.filters_x.append(
                    OneEuroFilter(t, landmark.x, min_cutoff=self.min_cutoff, beta=self.beta, d_cutoff=self.d_cutoff)
                )
                self.filters_y.append(
                    OneEuroFilter(t, landmark.y, min_cutoff=self.min_cutoff, beta=self.beta, d_cutoff=self.d_cutoff)
                )
            self.initialized = True

        # overwrite landmarks and apply filter to each landmark
        for i, landmark in enumerate(landmark_data.landmarks):
            landmark.x = self.filters_x[i](time.time(), landmark.x)
            landmark.y = self.filters_y[i](time.time(), landmark.y)

        return landmark_data
