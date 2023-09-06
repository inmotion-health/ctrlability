import mediapipe as mp
from videosource import WebcamSource

mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic
mp_face_mesh_connections = mp.solutions.face_mesh_connections
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=3)


def add_landmarks_to_frame(frame, results):
    mp_drawing.draw_landmarks(
        frame,
        results.face_landmarks,
        connections=mp_face_mesh_connections.FACEMESH_TESSELATION,
        landmark_drawing_spec=drawing_spec,
        connection_drawing_spec=drawing_spec,
    )
    mp_drawing.draw_landmarks(
        frame,
        results.left_hand_landmarks,
        mp_holistic.HAND_CONNECTIONS,
        landmark_drawing_spec=drawing_spec,
        connection_drawing_spec=drawing_spec,
    )
    mp_drawing.draw_landmarks(
        frame,
        results.right_hand_landmarks,
        mp_holistic.HAND_CONNECTIONS,
        landmark_drawing_spec=drawing_spec,
        connection_drawing_spec=drawing_spec,
    )
    mp_drawing.draw_landmarks(
        frame,
        results.pose_landmarks,
        mp_holistic.POSE_CONNECTIONS,
        landmark_drawing_spec=drawing_spec,
        connection_drawing_spec=drawing_spec,
    )


def get_distances(results):
    left_ear = results.face_landmarks.landmark[93]
    right_ear = results.face_landmarks.landmark[323]
    head_top = results.face_landmarks.landmark[10]
    head_bottom = results.face_landmarks.landmark[152]

    left_should = results.pose_landmarks.landmark[6]
    right_should = results.pose_landmarks.landmark[5]
    nose = results.face_landmarks.landmark[4]

    shoulder_distance = abs(left_should.x - right_should.x)

    avg_should_height = (left_should.y + right_should.y) / 2

    head_width = abs(left_ear.x - right_ear.x)
    head_height = abs(head_top.y - head_bottom.y)

    distance_left = (nose.x - left_ear.x) / head_width
    distance_top = (nose.y - head_top.y) / head_height


    return distance_left, distance_top


def main():
    source = WebcamSource()

    with mp_holistic.Holistic(
        min_detection_confidence=0.5, min_tracking_confidence=0.5
    ) as holistic:
        for idx, (frame, frame_rgb) in enumerate(source):
            results = holistic.process(frame_rgb)

            values_exist = (
                results.face_landmarks is not None
                and results.pose_landmarks is not None
            )

            if values_exist:
                distance_left, distance_top = get_distances(
                    results
                )

                X_THRESHOLD = 0.1
                center = 0.5

                if distance_left < center - X_THRESHOLD:
                    print(f"left - {distance_left}")
                elif center - X_THRESHOLD < distance_left < center + X_THRESHOLD:
                    print(f"center - {distance_left}")
                elif center + X_THRESHOLD < distance_left:
                    print(f"right - {distance_left}")

                Y_THRESHOLD = 0.05
                if distance_top < center - Y_THRESHOLD:
                    print(f"top - {distance_top}")
                elif center - Y_THRESHOLD < distance_top < center + Y_THRESHOLD:
                    print(f"center - {distance_top}")
                elif center + Y_THRESHOLD < distance_top:
                    print(f"bottom - {distance_top}")

            add_landmarks_to_frame(frame, results)

            source.show(frame)


if __name__ == "__main__":
    main()
