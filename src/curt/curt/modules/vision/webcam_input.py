""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, August 2020

"""

import cv2
import logging
import time
import base64
from curt.modules.vision.base_vision_input import BaseVisionInput


class WebcamInput(BaseVisionInput):
    def __init__(self):
        super().__init__("webcam_input")

    def config_input_handler(self, params):
        if self.input_handler is not None:
            logging.warning("Please release the current camera device first")
            return False
        else:
            camera_index = params["camera_index"]
            capture_width = params["capture_width"]
            capture_height = params["capture_height"]
            self.input_width = capture_width
            self.input_height = capture_height
            self.input_handler = cv2.VideoCapture(camera_index)
            self.input_handler.set(3, capture_width)
            self.input_handler.set(4, capture_height)
            return True

    def capture_image(self, gray=False):
        img = None
        imgByteArr = None
        if self.input_handler is not None:
            if self.input_handler.isOpened():
                _, img = self.input_handler.read()
            else:
                logging.warning("Camera Device is not Openeded")
        else:
            logging.warning("Please configure a camera device first")
        if gray:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if img is not None:
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 30]
            _, buffer = cv2.imencode(".jpg", img, encode_param)
            imgByteArr = base64.b64encode(buffer)
            return (img, imgByteArr.decode("ascii"))
        else:
            return (img, imgByteArr)
        # return img

    def release_input_handler(self):
        if self.input_handler is not None:
            self.input_handler.release()
            self.input_handler = None
        else:
            logging.warning("Please configure a camera device first")
