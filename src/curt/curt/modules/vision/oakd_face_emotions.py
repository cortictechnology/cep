""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

from curt.modules.vision.oakd_processing import OAKDProcessingWorker
import depthai as dai
from curt.modules.vision.utils import *
import numpy as np
import logging
import os
import time


class OAKDFaceEmotions(OAKDProcessingWorker):
    def __init__(self):
        super().__init__()

    def preprocess_input(self, params):
        img, detected_faces = params
        if img is None:
            return None
        if "face_emotions" not in self.oakd_pipeline.xlink_nodes:
            logging.warning("No such node: face_emotions in the pipeline")
            return []
        self.fe_nn_node_names = self.oakd_pipeline.xlink_nodes["face_emotions"]
        face_frames = []
        detections = []
        for detection in np.array(detected_faces):
            detections.append([detection[0], detection[1], detection[2], detection[3]])
            detection[0] = int(detection[0] * img.shape[1])
            detection[1] = int(detection[1] * img.shape[0])
            detection[2] = int(detection[2] * img.shape[1])
            detection[3] = int(detection[3] * img.shape[0])

            if detection[0] < 0:
                detection[0] = 0
            if detection[1] < 0:
                detection[1] = 0
            if detection[2] > img.shape[1]:
                detection[2] = img.shape[1] - 1
            if detection[3] > img.shape[0]:
                detection[3] = img.shape[0] - 1

            face_frame = img[
                int(detection[1]) : int(detection[3]),
                int(detection[0]) : int(detection[2]),
            ]
            face_frames.append(face_frame)
        return face_frames, detections

    def execute_nn_operation(self, preprocessed_data):
        face_frames, detections = preprocessed_data
        all_emotions = []
        for i in range(len(face_frames)):
            face_frame = face_frames[i]
            emotions = self.get_face_emotion(self.fe_nn_node_names, face_frame)
            all_emotions.append([emotions, detections[i]])
        return all_emotions

    def postprocess_result(self, inference_results):
        return inference_results

    def get_face_emotion(self, nn_node_names, aligned_face):
        frame_fe = dai.ImgFrame()
        frame_fe.setWidth(self.oakd_pipeline.nn_node_input_sizes["face_emotions"][0])
        frame_fe.setHeight(self.oakd_pipeline.nn_node_input_sizes["face_emotions"][1])
        frame_fe.setData(
            to_planar(
                aligned_face,
                (
                    self.oakd_pipeline.nn_node_input_sizes["face_emotions"][0],
                    self.oakd_pipeline.nn_node_input_sizes["face_emotions"][1],
                ),
            )
        )
        self.oakd_pipeline.set_input(nn_node_names[0], frame_fe)
        face_emotions = self.oakd_pipeline.get_output(
            nn_node_names[1]
        ).getFirstLayerFp16()
        return face_emotions
