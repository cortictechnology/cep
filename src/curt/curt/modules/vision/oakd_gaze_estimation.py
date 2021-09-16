""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

Implementation reference: 

https://github.com/luxonis/depthai-experiments/tree/master/gen2-gaze-estimation

"""


from curt.modules.vision.oakd_processing_worker import OAKDProcessingWorker
from curt.modules.vision.utils import decode_image_byte
import depthai as dai
from curt.modules.vision.utils import *
import curt.modules.vision.mediapipe_utils as mpu
import cv2
import queue
import numpy as np
import logging
import time
import threading
from math import cos, sin


def frame_norm(frame, bbox):
    norm_vals = np.full(len(bbox), frame.shape[0])
    norm_vals[::2] = frame.shape[1]
    return (np.clip(np.array(bbox), 0, 1) * norm_vals).astype(int)


def to_planar(arr: np.ndarray, shape: tuple) -> np.ndarray:
    return [val for channel in cv2.resize(arr, shape).transpose(2, 0, 1) for y_col in channel for val in y_col]

def to_tensor_result(packet):
    # for tensor in packet.getRaw().tensors:
    #     logging.warning(str(tensor.name))
    #     logging.warning(str(tensor.dims))
    #     logging.warning(str(packet.getLayerFp16(tensor.name)))
    return {
        tensor.name: np.array(packet.getLayerFp16(tensor.name)).reshape(tensor.dims)
        for tensor in packet.getRaw().tensors
    }


def padded_point(point, padding, frame_shape=None):
    if frame_shape is None:
        return [
            point[0] - padding,
            point[1] - padding,
            point[0] + padding,
            point[1] + padding
        ]
    else:
        def norm(val, dim):
            return max(0, min(val, dim))
        if np.any(point - padding > np.array((frame_shape[1], frame_shape[0]))) or np.any(point + padding < 0):
            print(f"Unable to create padded box for point {point} with padding {padding} and frame shape {frame_shape[:2]}")
            return None

        return [
            norm(point[0] - padding, frame_shape[1]),
            norm(point[1] - padding, frame_shape[0]),
            norm(point[0] + padding, frame_shape[1]),
            norm(point[1] + padding, frame_shape[0])
        ]

class OAKDGazeEstimation(OAKDProcessingWorker):
    def __init__(self):
        super().__init__()
        self.frame = None
        self.face_box = None
        self.bboxes = []
        self.left_bbox = None
        self.right_bbox = None
        self.nose = None
        self.pose = None
        self.gaze = None

        self.running = True
        self.frame_count = 0
        self.start_time = time.monotonic()

    def preprocessing(self, params):
        if "face_landmarks" not in self.oakd_pipeline.xlink_nodes:
            logging.warning("No such node: face_landmarks in the pipeline")
            return None
        if "headpose" not in self.oakd_pipeline.xlink_nodes:
            logging.warning("No such node: headpose in the pipeline")
            return None
        if "gaze_estimation" not in self.oakd_pipeline.xlink_nodes:
            logging.warning("No such node: gaze_estimation in the pipeline")
            return None
        self.fl_nn_node_names = self.oakd_pipeline.xlink_nodes["face_landmarks"]
        self.hp_nn_node_names = self.oakd_pipeline.xlink_nodes["headpose"]
        self.ge_nn_node_names = self.oakd_pipeline.xlink_nodes["gaze_estimation"]
        img, detected_faces = params
        if img is None:
            return None
        if isinstance(img, str):
            img = decode_image_byte(img)
        if detected_faces is None:
            return None
        if len(detected_faces) == 0:
            return None
        #logging.warning("Frame size: " +  str(img.shape))
        detected_faces = np.array(detected_faces)
        largest_face_area = 0
        largest_face = None
        largest_detection = []

        for face in detected_faces:
            bbox = frame_norm(img, face)
            face_frame = img[bbox[1]:bbox[3], bbox[0]:bbox[2]]
            area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
            if area > largest_face_area:
                largest_face_area = area
                largest_face = face_frame
                largest_detection = bbox
        #logging.warning("Largest face: " + str(largest_detection))
        face_landmarks, headpose = self.get_face_landmarks_and_headpose(
                self.fl_nn_node_names, self.hp_nn_node_names, largest_face
            )
        #logging.warning("landmarks: " + str(face_landmarks))
        #logging.warning("Headpose: " + str(headpose))
        for i in range(5):
            face_landmarks[i * 2] = face_landmarks[i * 2] + largest_detection[0]
            face_landmarks[i * 2 + 1] = (
                face_landmarks[i * 2 + 1] + largest_detection[1]
            )
        face_landmarks = face_landmarks.reshape((-1, 2))

        raw_face_landmarks = face_landmarks.astype(np.float32)
        raw_face_landmarks[:,0] = raw_face_landmarks[:,0] / img.shape[1]
        raw_face_landmarks[:,1] = raw_face_landmarks[:,1] / img.shape[0]

        left_bbox = padded_point(face_landmarks[0], padding=30, frame_shape=img.shape)
        right_bbox = padded_point(face_landmarks[1], padding=30, frame_shape=img.shape)
        left_img = img[left_bbox[1]:left_bbox[3], left_bbox[0]:left_bbox[2]].copy()
        right_img = img[right_bbox[1]:right_bbox[3], right_bbox[0]:right_bbox[2]].copy()
        #cv2.imwrite("/data/left.jpg", left_img)
        #cv2.imwrite("/data/right.jpg", right_img)
        #logging.warning("Done preprocessing")
        return left_img, right_img, headpose, raw_face_landmarks

    def execute_nn_operation(self, preprocessed_data):
        left_img, right_img, headpose, raw_face_landmarks = preprocessed_data
        gaze_data = dai.NNData()
        gaze_data.setLayer("left_eye_image", to_planar(left_img, (60, 60)))
        gaze_data.setLayer("right_eye_image", to_planar(right_img, (60, 60)))
        gaze_data.setLayer("head_pose_angles", headpose)
        self.oakd_pipeline.set_input(self.ge_nn_node_names[0], gaze_data)
        #logging.warning("Send data to gaze nn")
        raw_gaze = np.array(self.oakd_pipeline.get_output(self.ge_nn_node_names[1]).getFirstLayerFp16())
        #logging.warning("Gaze: " + str(raw_gaze))
        return raw_gaze, raw_face_landmarks, headpose

    def postprocessing(self, inference_results):
        gaze, raw_face_landmarks, headpose = inference_results
        return [gaze.tolist(), raw_face_landmarks.tolist(), headpose.tolist()]

    def get_face_landmarks_and_headpose(self, fl_nn_node_names, hp_nn_node_names, face_frame):
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

        frame_hp = dai.ImgFrame()
        frame_hp.setWidth(self.oakd_pipeline.nn_node_input_sizes["headpose"][0])
        frame_hp.setHeight(self.oakd_pipeline.nn_node_input_sizes["headpose"][1])
        frame_hp.setData(
            to_planar(
                face_frame,
                (
                    self.oakd_pipeline.nn_node_input_sizes["headpose"][0],
                    self.oakd_pipeline.nn_node_input_sizes["headpose"][1],
                ),
            )
        )

        self.oakd_pipeline.set_input(fl_nn_node_names[0], frame_lm)
        self.oakd_pipeline.set_input(hp_nn_node_names[0], frame_hp)

        face_landmarks = self.oakd_pipeline.get_output(
            fl_nn_node_names[1]
        ).getFirstLayerFp16()
        face_landmarks = frame_norm(face_frame, face_landmarks)

        headposes = self.oakd_pipeline.get_output(
            hp_nn_node_names[1]
        )
        #logging.warning(str(headposes))
        values = to_tensor_result(headposes)

        poses = [values['angle_y_fc'][0][0],
                values['angle_p_fc'][0][0],
                values['angle_r_fc'][0][0]
                ]
        
        return np.array(face_landmarks), np.array(poses)
    