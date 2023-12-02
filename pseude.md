register roi 
define action on landmark(s) in roi 
blendshape to action 
relative distance of landmarks position to action 
landmark to mous movment with config 
key word to action 


---
what is a action?
how do we define a action
-> inject custom actions

--- common:
video inputs 
how do we get frames 
do we get frames or doe we get the data produced by the frames

--- mapping:
data_source face_landmarks;
inputaction landmark_distance;

outputaction keycommand;

facelndmarks.connect(landmark_distance);
landmark_distance.connect(keycommand);
