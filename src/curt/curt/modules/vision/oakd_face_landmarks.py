""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, March 2021

"""

from curt.modules.vision.oakd_processing_worker import OAKDProcessingWorker
import depthai as dai
from curt.modules.vision.utils import *
import numpy as np
import logging
import os
import time


class OAKDFaceLandmarks(OAKDProcessingWorker):
    def __init__(self):
        super().__init__()

    def preprocessing(self, params):
        img, detected_faces = params
        if img is None:
            return None
        if "face_landmarks" not in self.oakd_pipeline.xlink_nodes:
            logging.warning("No such node: face_landmarks in the pipeline")
            return []
        self.fl_nn_node_names = self.oakd_pipeline.xlink_nodes["face_landmarks"]
        face_frames = []
        detections = []
        for detection in np.array(detected_faces):
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
            detections.append(detection)
        return face_frames, detections

    def execute_nn_operation(self, preprocessed_data):
        face_frames, detections = preprocessed_data
        all_landmarks = []
        for i in range(len(face_frames)):
            face_frame = face_frames[i]
            face_landmarks = self.get_face_landmarks_single(
                self.fl_nn_node_names, face_frame
            )
            all_landmarks.append(face_landmarks)
        return all_landmarks, detections

    def postprocessing(self, inference_results):
        all_landmarks, detections = inference_results
        all_face_landmarks = []
        for i in range(len(all_landmarks)):
            face_landmarks = all_landmarks[i]
            # logging.warning(str(face_landmarks) + ", " + str(detections))
            for j in range(5):
                face_landmarks[j * 2] = face_landmarks[j * 2] + detections[i][0]
                face_landmarks[j * 2 + 1] = face_landmarks[j * 2 + 1] + detections[i][1]
            face_landmarks = face_landmarks.reshape((-1, 2))
            all_face_landmarks.append(face_landmarks.tolist())
        return all_face_landmarks

    def get_face_landmarks_single(self, nn_node_names, face_frame):
        frame_lm = dai.ImgFrame()
        frame_lm.setWidth(self.oakd_pipeline.nn_node_input_sizes["face_landmarks"][0])
        frame_lm.setHeight(self.oakd_pipeline.nn_node_input_sizes["face_landmarks"][1])
        frame_lm.setData(
            to_planar(
                face_frame,
                (
                    self.oakd_pipeline.nn_node_input_sizes["face_landmarks"][0],
                    self.oakd_pipeline.nn_node_input_sizes["face_landmarks"][1],
                ),
            )
        )
        self.oakd_pipeline.set_input(nn_node_names[0], frame_lm)
        face_landmarks = self.oakd_pipeline.get_output(
            nn_node_names[1]
        ).getFirstLayerFp16()
        face_landmarks = frame_norm(face_frame, face_landmarks)
        return np.array(face_landmarks)

    # def get_face_landmarks(self, img, detected_faces):
    #     if img is None:
    #         return []
    #     if "face_landmarks" not in self.oakd_pipeline.xlink_nodes:
    #         logging.warning("No such node: face_landmarks in the pipeline")
    #         return []
    #     fl_nn_node_names = self.oakd_pipeline.xlink_nodes["face_landmarks"]
    #     all_face_landmarks = []
    #     for detection in np.array(detected_faces):
    #         detection[0] = int(detection[0] * img.shape[1])
    #         detection[1] = int(detection[1] * img.shape[0])
    #         detection[2] = int(detection[2] * img.shape[1])
    #         detection[3] = int(detection[3] * img.shape[0])

    #         if detection[0] < 0:
    #             detection[0] = 0
    #         if detection[1] < 0:
    #             detection[1] = 0
    #         if detection[2] > img.shape[1]:
    #             detection[2] = img.shape[1] - 1
    #         if detection[3] > img.shape[0]:
    #             detection[3] = img.shape[0] - 1

    #         face_frame = img[
    #             int(detection[1]) : int(detection[3]),
    #             int(detection[0]) : int(detection[2]),
    #         ]
    #         face_landmarks = self.get_face_landmarks_single(
    #             fl_nn_node_names, face_frame
    #         )
    #         for i in range(5):
    #             face_landmarks[i * 2] = face_landmarks[i * 2] + detection[0]
    #             face_landmarks[i * 2 + 1] = face_landmarks[i * 2 + 1] + detection[1]
    #         face_landmarks = face_landmarks.reshape((-1, 2))
    #         all_face_landmarks.append(face_landmarks.tolist())
    #     return all_face_landmarks
