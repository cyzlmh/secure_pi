from time import sleep
from datetime import datetime
import cv2
import imutils
from imutils.video import VideoStream

MIN_AREA = 500

def detect_motion(frame1, frame2):
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

if __name__ == '__main__':
    vs = VideoStream(src=0, usePiCamera=True).start()
    sleep(2)
    print('camera ready')
    firstFrame = None
    try:
        while True:
            frame = vs.read()
            frame = imutils.resize(frame, width=500)
            cv2.imwrite(datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')+'-o.jpg', frame)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            cv2.imwrite(datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')+'-g.jpg', gray)
            if firstFrame is None:
                firstFrame = gray
                continue
            detected_objs, diff = detect_motion(firstFrame, gray)
            if len(detected_objs) > 0:
                cv2.imwrite(datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')+'-d.jpg', diff)
                print('motion detected')
            else:
                print('no motion')
            sleep(2)
            firstFrame = gray
    finally:
        vs.stop()

