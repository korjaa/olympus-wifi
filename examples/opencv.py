import time
import cv2
import numpy
from olympus_wifi import OlympusCamera
from olympus_wifi.rtp_receiver import RtpReceiver

port = 40_000
camera = OlympusCamera()
camera.send_command('switch_cammode', mode='play')
camera.get_commands()["switch_cammode"].args["mode"]["rec"]["lvqty"].keys()
camera.start_liveview(port=port, lvqty='1024x0768')
# ['0320x0240', '0640x0480', '0800x0600', '1024x0768', '1280x0960']

try:
    with RtpReceiver(port) as rtp:
        cap = cv2.VideoCapture(rtp.file)
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                cv2.imshow('frame', frame)
                if cv2.waitKey(1) == ord("q"):
                    break
            else:
                break

        cap.release()
        cv2.destroyAllWindows()
finally:
    camera.stop_liveview()
