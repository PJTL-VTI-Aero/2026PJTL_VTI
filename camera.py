from gz.transport13 import Node
from gz.msgs10.image_pb2 import Image
import numpy as np
import cv2
import time

WINDOW_NAME = "Gazebo Camera Stream"

def image_callback(msg: Image):
    """
    Convert the incoming Gazebo Image message to an OpenCV image and display it.
    Assumes RGB8 format.
    """

    width = msg.width
    height = msg.height
    channels = msg.step // width  # calculate number of channels from step

    # Convert raw data to numpy array
    img_np = np.frombuffer(msg.data, dtype=np.uint8)
    img_np = img_np.reshape((height, width, channels))

    # If more than 3 channels, take only first 3
    if channels > 3:
        img_np = img_np[:, :, :3]

    img_np = cv2.resize(img_np, (350, 350))

    cv2.imshow(WINDOW_NAME, img_np)
    cv2.waitKey(1)

def main():
    node = Node()

    topic_name = "/world/baylands/model/x500_mono_cam_down_0/link/camera_link/sensor/camera/image"

    if node.subscribe(Image, topic_name, image_callback):
        print(f"Subscribed to image topic: {topic_name}")
    else:
        print(f"Error subscribing to topic {topic_name}")
        return

    # Keep script alive
    try:
        while True:
            time.sleep(0.001)
    except KeyboardInterrupt:
        print("Shutting down subscriber.")
    finally:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()