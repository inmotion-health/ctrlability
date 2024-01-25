from dataclasses import dataclass


@dataclass
class FrameData:
    frame: any
    width: any
    height: any


@dataclass
class LandmarkData:
    landmarks: any
    width: any
    height: any


@dataclass
class NormalVectorData:
    base: any
    tip: any
    width: any
    height: any
