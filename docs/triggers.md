# Triggers

## FacialExpressionTrigger
A trigger that detects facial expressions based on blendshape names and confidence levels.

#### Inputs

- **data**: The list of blendshapes detected in the frame.

#### Returns

- **dict**: The detected blendshape and the confidence level.

#### Arguments

| Name | Description |
| ---- | ----------- |
| name (str) | The name of the blendshape to detect. |
| confidence (float, optional) | The confidence level required to trigger the expression. Defaults to 0.5. |
| trigger_once (bool, optional) | Whether the trigger should only be activated once. Defaults to True. |

## Throughput
A trigger that passes through the data without any modifications and hence always triggers. This is useful for
testing and debugging purposes.

## RegionOfInterest
A trigger that detects when a landmark is within a region of interest. The region of interest is defined by a
position and size. The trigger can be set to keep triggering as long as the landmark is within the region.

#### Inputs

- **LandmarkData**: The landmark data.

#### Returns

- **dict**: The triggered landmarks.

#### Arguments

| Name | Description |
| ---- | ----------- |
| landmarks (list) | The list of landmarks to be checked. |
| position (tuple) | The position of the region of interest in normalized coordinates. |
| size (tuple) | The size of the region of interest. |
| keep_triggering (bool, optional) | Whether the trigger should keep triggering as long as the landmark is within the region. Defaults to False. |

## LandmarkDistance
The LandmarkDistance class is a subclass of Trigger and is used to check the distance between two landmarks.
It triggers when the distance between the two landmarks exceeds a threshold.

#### Arguments

| Name | Description |
| ---- | ----------- |
| landmarks | A list of two landmarks between which the distance should be checked. |
| threshold | The threshold value for the distance between the landmarks. |
| timer | The time duration (in milliseconds) for which the distance should exceed the threshold before triggering (default: 0.0). |
| direction | The direction of the trigger. Can be "greater" or "smaller" (default: "greater"). |
| normalize | A boolean value to normalize the distance with respect to a reference distance (default: False). |
| ref_landmarks | A list of two landmarks to be used as reference for normalizing the distance (default: None). |

## AbsoluteCursorControl
A trigger that moves the cursor to the position of the nose tip in the 2D space. We project a vector from a specific
landmark first using the normal vector and then translate the nose tip to the screen space.

!! This trigger only works with facial landmarks !!

#### Inputs

- **NormalVectorData**: The normal vector of the landmark.

#### Returns

- **dict**: The x and y coordinates of the landmark tip in the screen space.

#### Arguments

| Name | Description |
| ---- | ----------- |
| rect_width | The width of the rectangle around the nose tip (default: 0.8). |
| head_width | The width of the head (default: 0.3). |

## RelativeCursorControl
A trigger that moves the cursor to the position of the nose tip in 2D space. The distance from the nose tip to a
computed head center is used to move the cursor relative to the current position of the cursor.

!! This trigger only works with facial landmarks !!

#### Inputs

- **LandmarkData**: The landmark data.

#### Returns

- **dict**: The x and y coordinates of the landmark tip in the screen space.

#### Arguments

| Name | Description |
| ---- | ----------- |
| x_threshold | The threshold for the x axis (default: 0.05). |
| y_threshold | The threshold for the y axis (default: 0.03). |
| velocity_compensation_x | The velocity compensation for the x axis (default: 0.15). |
| velocity_compensation_y | The velocity compensation for the y axis (default: 3.5). |
