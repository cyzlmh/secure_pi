import io, os, threading, picamera, cv2
from time import sleep
from datetime import datetime
import numpy as np
from detect_motion import *
from smb_storage import *
from send_email import send_email

WIDTH = 640
HIGTH = 480
sample_rate = 3
storage_path = '/home/pi/Pictures'

def wait(camera, sec):
    for i in range(sec):
        camera.annotate_text = datetime.now().strftime('%Y%m%d-%H%M%S')
        camera.wait_recording(1)

def swift_record(camera, conn, stream_1, stream_2, pos, filepath):
    stream_2.truncate(0)
    camera.split_recording(stream_2)
    stream_1.seek(0)
    pos = conn.storeFileFromOffset(share.name, filepath, stream_1, pos)
    return pos

if __name__ == '__main__':
    with picamera.PiCamera() as camera:
        # initiation
        camera.resolution = (WIDTH, HIGTH)
        camera.annotate_text_size = 20
        cache_stream = picamera.PiCameraCircularIO(camera, seconds=10)
        stream_1 = io.BytesIO()
        stream_2 = io.BytesIO() 
        prior = None
            
        try:
            # connect to smb server
            conn = H100Connection()
            conn.connect()
            share = conn.get_share()
            print('smb server connected')
            
            # warm up camera
            camera.start_recording(cache_stream, format='h264', quality=25)
            camera.wait_recording(2)
            print('start recording')

            # start monitoring
            while True:
                wait(camera, sample_rate)
                motion, prior = detect_motion(camera, WIDTH, HIGTH, prior)
                if motion:
                    print('Motion detected!')
                    # take a picture
                    ts = datetime.now().strftime('%Y%m%d-%H%M%S')
                    capture_path = os.path.join(storage_path, ts+'.jpg')
                    video_path = os.path.join('test/', ts+'.h264')
                    camera.capture(capture_path, use_video_port=True)
                    
                    stream_1.truncate(0)
                    camera.split_recording(stream_1)
                    # As soon as we detect motion, split the recording
                    # Write the 10 seconds "before" motion to disk as well
                    stream_2.truncate(0)
                    cache_stream.copy_to(stream_2, seconds=10)
                    stream_2.seek(0)
                    pos = conn.storeFileFromOffset(share.name, 'test/'+ts+'.h264', stream_2)
                    cache_stream.clear()
                    recording_on = 1

                    # send email alert
                    threading.Thread(target=send_email, args=(storage_path,))

                    wait(camera, sample_rate)
                    motion, prior = detect_motion(camera, WIDTH, HIGTH, prior)
                    # Wait until motion is no longer detected, then split
                    # recording back to the in-memory circular buffer
                    while motion:
                        if recording_on == 1:
                            pos = swift_record(camera, conn, stream_1, stream_2, pos, video_path)
                            recording_on = 2
                            wait(camera, sample_rate)
                        else:
                            pos = swift_record(camera, conn, stream_2, stream_1, pos, video_path)
                            recording_on = 1
                            wait(camera, sample_rate)
                        motion, prior = detect_motion(camera, WIDTH, HIGTH, prior)
                    camera.split_recording(cache_stream)
                    if recording_on == 1:
                        stream_1.seek(0)
                        pos = conn.storeFileFromOffset(share.name, video_path, stream_1, pos)
                    else:
                        stream_2.seek(0)
                        pos = conn.storeFileFromOffset(share.name, video_path, stream_2, pos)
                    print('Motion stopped!')
                else:
                    print('No motion')
        finally:
            conn.close()
            camera.stop_recording()
