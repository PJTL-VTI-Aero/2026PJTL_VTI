import pyzed.sl as sl
import cv2
import numpy as np

# Create camera object
zed = sl.CameraOne()

# Init parameters
init = sl.InitParametersOne()

# Open camera
err = zed.open(init)
if err != sl.ERROR_CODE.SUCCESS:
    print("Failed to open ZED camera")
    exit(1)

# Create image container
image = sl.Mat()

# gst_output = (
#     "appsrc ! "
#     "video/x-raw,format=BGR,width=640,height=480,framerate=30/1 ! "
#     "videoconvert ! "
#     "x264enc tune=zerolatency bitrate=2000 speed-preset=ultrafast byte-stream=true key-int-max=30 ! "
#     "video/x-h264,profile=baseline ! "
#     "rtph264pay config-interval=1 pt=96 ! "
#     "udpsink host=35.0.1.238 port=5000"
# )

gst_output = (
    "appsrc ! "
    "video/x-raw,format=BGR,width=640,height=480,framerate=30/1 ! "
    "videoconvert ! "
    "x264enc tune=zerolatency bitrate=2000 speed-preset=ultrafast byte-stream=true key-int-max=30 ! "
    "video/x-h264,profile=baseline ! "
    "rtph264pay config-interval=1 pt=96 ! "
    "udpsink host=35.0.1.238 port=5000"
)



out = cv2.VideoWriter(
    gst_output,
    cv2.CAP_GSTREAMER,
    0,  # let GStreamer handle encoding
    30,
    (640, 480),
    True
)

if not out.isOpened():
    print("Failed to open VideoWriter")




print("Streaming with red blob detection. Press Ctrl+C to stop.")

try:
    while True:
        if zed.grab() == sl.ERROR_CODE.SUCCESS:
            zed.retrieve_image(image, sl.VIEW.LEFT)
            frame = image.get_data()

            frame = cv2.resize(frame, (640, 480))
            # hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            if frame.dtype != np.uint8 or frame.shape[2] != 3:
                print("Converting")
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)  # convert if needed
            print(frame.dtype, frame.shape)

            lower_red = np.array([0, 0, 150])       # minimum B,G,R
            upper_red = np.array([120, 120, 255])   # maximum B,G,R

            # Create mask
            mask = cv2.inRange(frame, lower_red, upper_red)

            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Draw bounding box for the largest red blob
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                if cv2.contourArea(largest_contour) > 500:  # filter small noise
                    x, y, w, h = cv2.boundingRect(largest_contour)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # # Write frame to GStreamer
            out.write(frame)

except KeyboardInterrupt:
    print("Streaming stopped by user.")

# Cleanup
out.release()
zed.close()
