from vidcontrol import VideoManager
import mediapipe as mp

class InputProcessing:
    def __init__(self):
        pass
    
    def process():
        pass
    
    def execute():
        pass
    
class LandmarkDistanceInputProcessing(InputProcessing):
    def __init__(self, landmark1, landmark2, threshold, mapping_engine):
        self.landmark1 = landmark1
        self.landmark2 = landmark2
        self.threshold = threshold
        
        
    def process(self, landmarks):
        return landmarks[self.landmark1].x - landmarks[self.landmark2].x > self.threshold
    
    def execute():
        if self.process():
            self.mapping_engine.notify("")
            
    
     
class OutputAction:
    def run():
        pass
    
class InputStream:
    def __init__(self):
        pass
        
    def get_next():
        return # some data
    
class DataAggregator:
    def process_block(self, block): 
        pass
    
class FaceLandmarkDataAggregator(DataAggregator):
    def __init__(self):     
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            min_detection_confidence=0.5, min_tracking_confidence=0.5
        )
        
    def process_block(self):
        frame = next(self.source)
        results = self.face_mesh.process(frame)
        return results.multi_face_landmarks
    
class MappingBootstrapper:
    def __init__(self, mapping_engine):
        self.mapping_engine = mapping_engine

    def parse_config():
        pass
        
    def bootstrap(self):
        for config in self.parse_config():
            # decide wich input processing to use
            input_processing = InputProcessing()
            
            # hey we seem to need face landmarks
            face_landmark_data_source = FaceLandmarkDataSource()
            
            # decide wich output action to use
            output_action = OutputAction()
            
FrameStreamProccesorAggregator.register(FaceLandmarkDataAggregator())
FrameStream.register_processor(FaceLandmarkDataAggregator())
FrameStream.register_processor(FaceLandmarkDataAggregator())




class MappingEngine:
    def register(self, input_processing, output_action):
        pass