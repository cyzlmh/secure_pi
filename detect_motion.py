from io import BytesIO
import numpy as np
import cv2

MIN_AREA = 800
prior_image = None

def preprocess(image):
    #preprocess the image before detect motion
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.GaussianBlur(image, (21, 21), 0)
    return image

def find_moving_objs(image_1, image_2):
    # compute the absolute difference between the current frame and first frame
    imageDelta = cv2.absdiff(image_1, image_2)
    thresh = cv2.threshold(imageDelta, 25, 255, cv2.THRESH_BINARY)[1]
    
    # dilate the thresholded image to fill in holes, then find contours on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]
    objs = []
    for c in cnts:
        if cv2.contourArea(c) >= MIN_AREA:
            objs.append(cv2.boundingRect(c))
    return objs

def detect_motion(camera, width, highth, prior):
    if prior is None:
        return False
    stream = BytesIO()
    camera.capture(stream, format='bgr', use_video_port=True)
    stream.seek(0)
    image = np.frombuffer(stream.read(), dtype=np.uint8).reshape(highth, width, 3)
    image = preprocess(image)
    return len(find_moving_objs(prior, image)) > 0, image
