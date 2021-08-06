""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

import depthai as dai
from curt.modules.vision.utils import *
import numpy as np
import logging
import os
import time


class OAKDRgbCamera:
    def __init__(self):
        self.oakd_pipeline = None
        self.friendly_name = ""

    def config_pipeline(self, config_data):
        pass

    def config_pipeline_version(self, version):
        pass

    def run_inference(self, request_data):
        if request_data[0] == "get_rgb_frame":
            img = self.get_rgb_frame()
            if img is not None:
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 30]
                _, buffer = cv2.imencode(".jpg", img, encode_param)
                imgByteArr = base64.b64encode(buffer)
                imgByte = imgByteArr.decode()
                return (img, imgByte)
            else:
                return None

        elif request_data[0] == "get_still_frame":
            img = self.get_still_frame()
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
            _, buffer = cv2.imencode(".jpg", img, encode_param)
            imgByteArr = base64.b64encode(buffer)
            return (img, imgByteArr.decode())

    def get_still_frame(self):
        ctrl = dai.CameraControl()
        ctrl.setCaptureStill(True)
        self.oakd_pipeline.set_input("control", ctrl)
        time.sleep(1)
        stillFrame = self.oakd_pipeline.get_output("still")
        print("Got still frame")
        stillFrame = stillFrame.getCvFrame()
        return stillFrame

    def get_rgb_frame(self):
        if "rgb_camera" not in self.oakd_pipeline.xlink_nodes:
            logging.warning("No such node: rgb_camera in the pipeline")
            return None
        rgb_cam_node_names = self.oakd_pipeline.xlink_nodes["rgb_camera"]
        if rgb_cam_node_names[1] in self.oakd_pipeline.stream_nodes:
            frame = self.oakd_pipeline.stream_nodes[rgb_cam_node_names[1]]
        else:
            frame = self.oakd_pipeline.get_output(rgb_cam_node_names[1])
        if frame is not None:
            if not isinstance(frame, dai.NNData):
                if "isp" in rgb_cam_node_names[1]:
                    return frame.getCvFrame()
                else:
                    img = frame.getFrame()
                    img = img.transpose(2, 1, 0)
                    img = img.swapaxes(0, 1)
                    return img
            else:
                return frame.getFirstLayerFp16()
        else:
            return None
