""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, March 2021

"""

import depthai as dai
from curt.modules.vision.utils import *
import numpy as np
import logging
import os
import time


class OAKDStereoCamera:
    def __init__(self):
        self.oakd_pipeline = None
        self.friendly_name = ""

    def config_pipeline(self, config_data):
        pass

    def config_pipeline_version(self, version):
        pass

    def run_inference(self, request_data):
        if request_data[0] == "get_stereo_frame":
            img = self.get_stereo_frame()
            if img is not None:
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 40]
                _, buffer = cv2.imencode(".jpg", img, encode_param)
                imgByteArr = base64.b64encode(buffer)
                imgByte = imgByteArr.decode("ascii")
                return (img, imgByte)
            else:
                return None

    def get_stereo_frame(self):
        if "stereo_camera" not in self.oakd_pipeline.xlink_nodes:
            logging.warning("No such node: stereo_camera in the pipeline")
            return None
        stereo_cam_node_names = self.oakd_pipeline.xlink_nodes["stereo_camera"]
        if stereo_cam_node_names[1] in self.oakd_pipeline.stream_nodes:
            frame = self.oakd_pipeline.stream_nodes[stereo_cam_node_names[1]]
        else:
            frame = self.oakd_pipeline.get_output(stereo_cam_node_names[1])
        if frame is not None:
            depthFrame = frame.getFrame()
            depthFrame = cv2.resize(
                depthFrame, (640, 360), interpolation=cv2.INTER_NEAREST
            )
            depthFrameColor = cv2.normalize(
                depthFrame, None, 255, 0, cv2.NORM_INF, cv2.CV_8UC1
            )
            depthFrameColor = cv2.equalizeHist(depthFrameColor)
            depthFrameColor = cv2.applyColorMap(depthFrameColor, cv2.COLORMAP_JET)
            return depthFrameColor
        else:
            return None
