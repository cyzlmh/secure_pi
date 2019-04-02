import io, os
from time import sleep
from datetime import datetime, timedelta
import picamera
import cv2
import numpy as np
import imutils

MIN_AREA = 100
WIDTH = 1024
HIGTH = 768
email_freq = 30*60
sample_rate = 3
storage_path = '/home/pi/Pictures'
prior_image = None

def ts_str():
    return datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')

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
    return objs

def stream_to_gray(stream):
    image = np.frombuffer(stream.read(), dtype=np.uint8).reshape(HIGTH, WIDTH, 3)
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
        result = len(diff(prior_image, current_image)) > 0
        # Once motion detection is done, make the prior image the current
        prior_image = current_image
        return result

if __name__ == '__main__':
    with picamera.PiCamera() as camera:
        camera.resolution = (WIDTH, HIGTH)
        stream = picamera.PiCameraCircularIO(camera, seconds=10)
        print('start recording')
        camera.start_recording(stream, format='h264', quality=25)
        camera.wait_recording(2)
        last_detect = datetime.now() - timedelta(0, email_freq)
        try:
            while True:
                camera.wait_recording(sample_rate)
                if detect_motion(camera):
                    print('Motion detected!')
                    prefix = os.path.join(storage_path, ts_str())
                    camera.capture(prefix+'.jpg', use_video_port=True)
                    if datetime.now() - last_detect > timedelta(0, email_freq):
                        os.system('python3 /home/pi/scripts/send_email.py anto_nozomi@126.com '\
                            +ts_str()+'-motion-detect null')
                        last_detect = datetime.now()
                    # As soon as we detect motion, split the recording to
                    # record the frames "after" motion
                    camera.split_recording(prefix+'-after.h264')
                    # Write the 10 seconds "before" motion to disk as well
                    #write_video(stream)
                    stream.copy_to(prefix+'-before.h264', seconds=10)
                    stream.clear()
                    # Wait until motion is no longer detected, then split
                    # recording back to the in-memory circular buffer
                    camera.wait_recording(sample_rate)
                    while detect_motion(camera):
                        camera.wait_recording(sample_rate)
                    print('Motion stopped!')
                    camera.split_recording(stream)
                else:
                    print('No motion')
        finally:
            camera.stop_recording()
