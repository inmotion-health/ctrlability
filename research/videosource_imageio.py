import imageio
import cv2


def display_webcam_with_imageio():
    # Create a reader object to capture video from the default webcam
    reader = imageio.get_reader(
        "<video1>"
    )  # '<video0>' is a special URI for the default webcam

    # Loop to continuously capture and display frames
    for frame in reader:
        # Display the frame using OpenCV
        cv2.imshow("Webcam", frame)

        # Break the loop if the 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Release OpenCV windows
    cv2.destroyAllWindows()


# Call the function
display_webcam_with_imageio()
