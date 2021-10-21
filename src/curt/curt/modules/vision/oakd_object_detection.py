""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

from curt.modules.vision.oakd_processing import OAKDProcessingWorker
import depthai as dai
from curt.modules.vision.utils import *
from curt.modules.vision.utils import decode_image_byte
import numpy as np
import logging
import os
import time


class OAKDObjectDetection(OAKDProcessingWorker):
    def __init__(self):
        super().__init__()
        self.spatial_detection = False

    def preprocess_input(self, params):
        if "object_detection" not in self.oakd_pipeline.xlink_nodes:
            logging.warning("No such node: object_detection in the pipeline")
            return []
        self.od_nn_node_names = self.oakd_pipeline.xlink_nodes["object_detection"]
        operation = params[0]
        if operation == "get_spatial_object_detections":
            self.spatial_detection = True
            return True
        elif operation == "detect_object":
            img = params[1]
            if img is None:
                return None
            if isinstance(img, str):
                img = decode_image_byte(img)
            return img
        elif operation == "detect_object_pipeline":
            return True
            
    def execute_nn_operation(self, preprocessed_data):
        detections = []
        if isinstance(preprocessed_data, bool):
            if self.od_nn_node_names[1] in self.oakd_pipeline.stream_nodes:
                detections = self.oakd_pipeline.stream_nodes[
                    self.od_nn_node_names[1]
                ]
            else:
                detections = self.oakd_pipeline.get_output(
                    self.od_nn_node_names[1]
                )
        else:
            frame_fd = dai.ImgFrame()
            frame_fd.setWidth(
                self.oakd_pipeline.nn_node_input_sizes["object_detection"][0]
            )
            frame_fd.setHeight(
                self.oakd_pipeline.nn_node_input_sizes["object_detection"][1]
            )
            frame_fd.setData(
                to_planar(
                    preprocessed_data,
                    (
                        self.oakd_pipeline.nn_node_input_sizes["object_detection"][0],
                        self.oakd_pipeline.nn_node_input_sizes["object_detection"][1],
                    ),
                )
            )
            self.oakd_pipeline.set_input(self.od_nn_node_names[0], frame_fd)
            detections = self.oakd_pipeline.get_output(
                self.od_nn_node_names[1]
            )
        if detections is None:
            detections = []
        else:
            detections = detections.detections
        return detections

    def postprocess_result(self, inference_result):
        bboxes = []
        for detection in inference_result:
            if self.spatial_detection:
                bbox = [
                    detection.xmin,
                    detection.ymin,
                    detection.xmax,
                    detection.ymax,
                    detection.spatialCoordinates.x,
                    detection.spatialCoordinates.y,
                    detection.spatialCoordinates.z,
                    detection.label,
                ]
            else:
                bbox = [
                    detection.xmin,
                    detection.ymin,
                    detection.xmax,
                    detection.ymax,
                    detection.label,
                ]
            bboxes.append(bbox)
        return bboxes
