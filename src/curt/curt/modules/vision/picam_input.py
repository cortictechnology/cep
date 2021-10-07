""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

import picamera
import picamera.array
import cv2
import logging
import time
import base64
import io
import threading
from curt.modules.vision.base_vision_input import BaseVisionInput
from collections import deque


class PicamInput(BaseVisionInput):
    def __init__(self):
        super().__init__("picam_input")
        self.stop_capturing = True
        self.frame_buffer = deque(maxlen=3)
        self.event = threading.Event()
        self.capture_thread = None

    def config_input_handler(self, params):
        if params["reset"]:
            self.release_input_handler()
            return True
        else:
            if not self.stop_capturing:
                self.stop_capturing = True
                self.capture_thread.join()
            # camera_index = params['camera_index']
            capture_width = params["capture_width"]
            capture_height = params["capture_height"]
            self.input_width = capture_width
            self.input_height = capture_height
            self.camera = picamera.PiCamera()
            self.camera.resolution = (self.input_width, self.input_height)
            self.camera.exposure_mode = "sports"
            self.camera.start_preview()
            self.capture_thread = threading.Thread(target=self.frame_capturing, daemon=True)
            # self.input_handler = self.frame_capturing()
            self.capture_thread.start()
            return True

    def frame_capturing(self):
        #stream = io.BytesIO()
        rawCapture = picamera.array.PiRGBArray(self.camera, size=(640, 480))
        self.stop_capturing = False
        for frame in self.camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        #for _ in self.camera.capture_continuous(stream, "jpeg", quality=50, use_video_port=True):
            #self.frame_buffer.append(stream.getvalue())
            self.frame_buffer.append(frame.array)
            # print("Appended new frame")
            # yield stream.getvalue()
            #stream.seek(0)
            #stream.truncate()
            rawCapture.truncate(0)
            self.event.set()
            if self.stop_capturing:
                break
        self.camera.close()
        self.camera = None

    def capture_image(self, data):
        # t1 = time.time()
        img = None
        imgByteArr = None
        if self.camera is not None:
            # print("check queue length")
            if self.event.wait(1):
                img = self.frame_buffer.popleft()
                if data[0] != "get_rgb_frame":
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                self.event.clear()
        else:
            logging.warning("Please configure a camera device first")
        if img is not None:
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 30]
            _, buffer = cv2.imencode(".jpg", img, encode_param)
            imgByteArr = base64.b64encode(buffer)
            return (img, imgByteArr.decode("ascii"))
        else:
            return (img, imgByteArr)

    def release_input_handler(self):
        self.stop_capturing = True
