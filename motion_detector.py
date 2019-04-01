import io
from time import sleep
from datetime import datetime, timedelta
import picamera
import cv2
import numpy as np
import imutils

MIN_AREA = 500
WIDTH = 1024
HIGTH = 768
prior_image = None

def diff(frame1, frame2):
    # compute the absolute difference between the current frame and first frame
    frameDelta = cv2.absdiff(frame1, frame2)
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
    
    # dilate the thresholded image to fill in holes, then find contours on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    objs = []
    for c in cnts:
        if cv2.contourArea(c) >= MIN_AREA:
            objs.append(cv2.boundingRect(c))
    return objs, thresh

def stream_to_gray(stream):
    image = np.frombuffer(stream.read(), dtype=np.uint8).reshape(WIDTH, HIGTH, 3)
    image = imutils.resize(image, width=500)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.GaussianBlur(image, (21, 21), 0)
    return image

def detect_motion(camera):
    global prior_image
    stream = io.BytesIO()
    camera.capture(stream, format='bgr', use_video_port=True)
    stream.seek(0)
    if prior_image is None:
        prior_image = stream_to_gray(stream)
        return False
    else:
        current_image = stream_to_gray(stream)
        # Compare current_image to prior_image to detect motion. This is
        # left as an exercise for the reader!
        result = len(diff(prior_image, current_image)) == 0
        # Once motion detection is done, make the prior image the current
        prior_image = current_image
        return result

def write_video(stream):
    # Write the entire content of the circular buffer to disk. No need to
    # lock the stream here as we're definitely not writing to it simultaneously
    with io.open('before.h264', 'wb') as output:
        for frame in stream.frames:
            if frame.frame_type == picamera.PiVideoFrameType.sps_header:
                stream.seek(frame.position)
                break
        while True:
            buf = stream.read1()
            if not buf:
                break
            output.write(buf)
    # Wipe the circular stream once we're done
    stream.seek(0)
    stream.truncate()

if __name__ == '__main__':
    with picamera.PiCamera() as camera:
        camera.resolution = (1280, 720)
        stream = picamera.PiCameraCircularIO(camera, seconds=10)
        camera.start_recording(stream, format='h264')
        detect_time = datetime.now() - timedelta(0, 60*30)
        try:
            while True:
                camera.wait_recording(1)
                if detect_motion(camera):
                    print('Motion detected!')
                    # As soon as we detect motion, split the recording to
                    # record the frames "after" motion
                    camera.split_recording('after.h264')
                    # Write the 10 seconds "before" motion to disk as well
                    write_video(stream)
                    # Wait until motion is no longer detected, then split
                    # recording back to the in-memory circular buffer
                    while detect_motion(camera):
                        camera.wait_recording(1)
                    print('Motion stopped!')
                    camera.split_recording(stream)
        finally:
            camera.stop_recording()