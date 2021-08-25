""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, April 2020

"""

from numpy.lib.arraysetops import isin
from curt.modules.vision.oakd_processing import OAKDProcessingWorker
import depthai as dai
from curt.modules.vision.utils import *
from curt.modules.vision.utils import decode_image_byte
import numpy as np
import logging

""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, March 2021

"""

import os
import time


class OAKDFaceDetection(OAKDProcessingWorker):
    def __init__(self):
        super().__init__()

    def preprocess_input(self, params):
        if "face_detection" not in self.oakd_pipeline.xlink_nodes:
            logging.warning("No such node: face_detection in the pipeline")
            return []
        self.fd_nn_node_names = self.oakd_pipeline.xlink_nodes["face_detection"]
        operation = params[0]
        if operation == "get_spatial_face_detections":
            return True
        elif operation == "detect_face":
            threshold, largest_only, img = params[1:]
            if img is None:
                return None
            return threshold, largest_only, img
        elif operation == "detect_face_pipeline":
            threshold, largest_only = params[1:]
            return threshold, largest_only

    def execute_nn_operation(self, preprocessed_data):
        if not isinstance(preprocessed_data, tuple):
            detections = []
            if self.fd_nn_node_names[1] in self.oakd_pipeline.stream_nodes:
                detections = self.oakd_pipeline.stream_nodes[
                    self.fd_nn_node_names[1]
                ].detections
            else:
                detections = self.oakd_pipeline.get_output(
                    self.fd_nn_node_names[1]
                ).detections
            return detections
        else:
            if len(preprocessed_data) == 2:
                threshold, largest_only = preprocessed_data
                if self.fd_nn_node_names[1] in self.oakd_pipeline.stream_nodes:
                    detections = self.oakd_pipeline.stream_nodes[
                        self.fd_nn_node_names[1]
                    ]
                else:
                    detections = self.oakd_pipeline.get_output(self.fd_nn_node_names[1])
                return detections, threshold, largest_only
            else:
                threshold, largest_only, img = preprocessed_data
                if isinstance(img, str):
                    img = decode_image_byte(img)
                frame_fd = dai.ImgFrame()
                frame_fd.setWidth(
                    self.oakd_pipeline.nn_node_input_sizes["face_detection"][0]
                )
                frame_fd.setHeight(
                    self.oakd_pipeline.nn_node_input_sizes["face_detection"][1]
                )
                frame_fd.setData(
                    to_planar(
                        img,
                        (
                            self.oakd_pipeline.nn_node_input_sizes["face_detection"][0],
                            self.oakd_pipeline.nn_node_input_sizes["face_detection"][1],
                        ),
                    )
                )
                self.oakd_pipeline.set_input(self.fd_nn_node_names[0], frame_fd)
                inference_result = self.oakd_pipeline.get_output(
                    self.fd_nn_node_names[1]
                )
                return inference_result, threshold, largest_only

    def postprocess_result(self, inference_result):
        bboxes = []
        if not isinstance(inference_result, tuple):
            for detection in inference_result:
                bbox = [
                    detection.xmin,
                    detection.ymin,
                    detection.xmax,
                    detection.ymax,
                    detection.spatialCoordinates.z,
                ]
                bboxes.append(bbox)
        else:
            detections, threshold, largest_only = inference_result
            bboxes = np.array(detections.getFirstLayerFp16())
            if bboxes.size > 0:
                # bboxes = bboxes[: np.where(bboxes == -1)[0][0]]
                bboxes = bboxes.reshape((bboxes.size // 7, 7))
                bboxes = bboxes[bboxes[:, 2] > threshold][:, 3:7]
                if largest_only:
                    largest_bbox = None
                    largest_area = 0
                    for raw_bbox in bboxes:
                        face_width = raw_bbox[2] - raw_bbox[0]
                        face_height = raw_bbox[3] - raw_bbox[1]
                        area = face_width * face_height
                        if area > largest_area:
                            largest_area = area
                            largest_bbox = raw_bbox
                    bboxes = largest_bbox
                else:
                    bboxes = bboxes.tolist()
        return bboxes
