""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, August 2020

"""

from os import SCHED_IDLE
import cv2
import logging
import time
import base64
import subprocess as sp
import numpy as np
import threading
import collections
from curt.modules.vision.base_vision_input import BaseVisionInput


class VideoInput(BaseVisionInput):
    def __init__(self):
        super().__init__("video_input")
        self.frame_buffer = collections.deque(maxlen=2)
        self.streaming_thread = None
        self.stop_streaming = False

    def config_input_handler(self, params):
        if self.input_handler is not None:
            logging.warning("Please release the current video first")
        else:
            video_source = params["video_source"]
            print("Video Source:", video_source)
            self.input_handler = cv2.VideoCapture(video_source)
            self.input_handler.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            self.streaming_thread = threading.Thread(
                target=self.grab_frame_func, daemon=True
            )
            self.streaming_thread.start()
            self.stream_rtsp = True
            self.stop_streaming = False

    def grab_frame_func(self):
        while self.input_handler.isOpened():
            if self.stop_streaming:
                break
            _, img = self.input_handler.read()
            if img is not None:
                self.frame_buffer.append(img)

    def capture_image(self, gray=False):
        img = None
        imgByteArr = None
        if self.input_handler is not None:
            if len(self.frame_buffer) > 0:
                img = self.frame_buffer.popleft()
            if img is not None:
                img = cv2.resize(img, (576, 324))
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 10]
                _, buffer = cv2.imencode(".jpg", img, encode_param)
                imgByteArr = base64.b64encode(buffer)
        else:
            logging.warning("Please configure a video source first")

        return (img, imgByteArr.decode("ascii"))

    def release_input_handler(self):
        self.stop_streaming = True
        if self.input_handler is not None:
            self.input_handler.release()
            self.input_handler = None
        else:
            logging.warning("Please configure a video soruce first")
