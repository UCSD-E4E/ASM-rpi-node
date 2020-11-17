import picamera 
from time import sleep
from subprocess import call 
from datetime import datetime 

# Camera Setup
with picamera.PiCamera() as camera:
    datetime1 = datetime.now()
    camera.start_recording("test_video.h264")
    sleep(5)
    camera.stop_recording()
    datetime2 = datetime.now()
# Converting the video to mp4

command = "MP4Box -add test_video.h264 converted.mp4"
call([command], shell=True)


