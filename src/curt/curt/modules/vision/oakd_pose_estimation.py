""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

Implementation reference: 

https://github.com/geaxgx/depthai_blazepose/blob/main/BlazeposeDepthai.py

"""

from curt.modules.vision.oakd_processing import OAKDProcessingWorker
import depthai as dai
from curt.modules.vision.utils import *
import curt.modules.vision.mediapipe_utils_pose as mpu
import numpy as np
import logging
import time
from math import sin, cos


class OAKDPoseEstimation(OAKDProcessingWorker):
    def __init__(self):
        super().__init__()
        self.pd_score_thresh = 0.5
        self.pd_nms_thresh = 0.3
        self.lm_score_thresh = 0.6

        anchor_options = mpu.SSDAnchorOptions(
            num_layers=5,
            min_scale=0.1484375,
            max_scale=0.75,
            input_size_height=224,
            input_size_width=224,
            anchor_offset_x=0.5,
            anchor_offset_y=0.5,
            strides=[8, 16, 32, 32, 32],
            aspect_ratios=[1.0],
            reduce_boxes_in_lowest_layer=False,
            interpolated_scale_aspect_ratio=1.0,
            fixed_anchor_size=True,
        )

        self.anchors = mpu.generate_anchors(anchor_options)
        self.nb_anchors = self.anchors.shape[0]
        self.force_detection = False
        self.use_previous_landmarks = False
        self.smoothing = True
        self.rect_transf_scale = 1.25
        self.nb_kps = 33

        self.filter_landmarks = mpu.LandmarksSmoothingFilter(
            frequency=10, min_cutoff=0.05, beta=80, derivate_cutoff=1
        )
        self.filter_landmarks_aux = mpu.LandmarksSmoothingFilter(
            frequency=10, min_cutoff=0.01, beta=10, derivate_cutoff=1
        )
        self.filter_landmarks_world = mpu.LandmarksSmoothingFilter(
            frequency=10,
            min_cutoff=0.1,
            beta=40,
            derivate_cutoff=1,
            disable_value_scaling=True,
        )

    def preprocess_input(self, params):
        if "body_detection" not in self.oakd_pipeline.xlink_nodes:
            logging.warning("No such node: body_detection in the pipeline")
            return None
        if "body_landmarks" not in self.oakd_pipeline.xlink_nodes:
            logging.warning("No such node: body_landmarks in the pipeline")
            return None
        self.pd_nn_node_names = self.oakd_pipeline.xlink_nodes["body_detection"]
        self.pm_nn_node_names = self.oakd_pipeline.xlink_nodes["body_landmarks"]
        img = params[0]

        # self.pd_nn_node_name = pd_nn_node_name
        # self.pm_nn_node_name = pm_nn_node_name
        self.lm_input_length = self.oakd_pipeline.nn_node_input_sizes["body_landmarks"][
            0
        ]
        if img is None:
            return None
        self.img = img
        self.h, self.w = img.shape[:2]
        self.frame_size = max(self.h, self.w)
        self.pad_h = int((self.frame_size - self.h) / 2)
        self.pad_w = int((self.frame_size - self.w) / 2)
        image = cv2.copyMakeBorder(
            img,
            self.pad_h,
            self.pad_h,
            self.pad_w,
            self.pad_w,
            cv2.BORDER_CONSTANT,
        )
        body = None
        if self.force_detection or not self.use_previous_landmarks:
            body = self.get_body(self.pd_nn_node_names, image)
        else:
            body = self.body_from_landmarks
            mpu.detections_to_rect(body)
            mpu.rect_transformation(
                body, self.frame_size, self.frame_size, self.rect_transf_scale
            )
        if body is None:
            self.use_previous_landmarks = False
            if self.smoothing:
                self.filter_landmarks.reset()
                self.filter_landmarks_aux.reset()
                self.filter_landmarks_world.reset()
            return None
        return body, image

    def execute_nn_operation(self, preprocessed_data):
        body, image = preprocessed_data
        img = mpu.warp_rect_img(
            body.rect_points, image, self.lm_input_length, self.lm_input_length
        )
        frame_nn = dai.ImgFrame()
        frame_nn.setData(to_planar(img, (self.lm_input_length, self.lm_input_length)))
        frame_nn.setTimestamp(time.monotonic())
        frame_nn.setWidth(self.lm_input_length)
        frame_nn.setHeight(self.lm_input_length)
        self.oakd_pipeline.set_input(self.pm_nn_node_names[0], frame_nn)

        raw_inference_results = self.oakd_pipeline.get_output(self.pm_nn_node_names[1])

        return body, raw_inference_results

    def postprocess_result(self, inference_results):
        body, raw_inference_results = inference_results
        body = self.lm_postprocess(body, raw_inference_results)
        if body.lm_score < self.lm_score_thresh:
            body = None
            self.use_previous_landmarks = False
            if self.smoothing:
                self.filter_landmarks.reset()
                self.filter_landmarks_aux.reset()
                self.filter_landmarks_world.reset()
        else:
            self.use_previous_landmarks = True
        if body is not None:
            return body.landmarks.tolist()
        else:
            return None

    def pd_postprocess(self, inference):
        scores = np.array(
            inference.getLayerFp16("Identity_1"), dtype=np.float16
        )  # 2254
        bboxes = np.array(inference.getLayerFp16("Identity"), dtype=np.float16).reshape(
            (self.nb_anchors, 12)
        )  # 2254x12
        # Decode bboxes
        bodies = mpu.decode_bboxes(
            self.pd_score_thresh, scores, bboxes, self.anchors, best_only=True
        )
        if bodies:
            body = bodies[0]
        else:
            return None
        # Non maximum suppression
        mpu.detections_to_rect(body)
        mpu.rect_transformation(
            body, self.frame_size, self.frame_size, self.rect_transf_scale
        )
        return body

    def lm_postprocess(self, body, inference):
        body.lm_score = inference.getLayerFp16("output_poseflag")[0]
        if body.lm_score > self.lm_score_thresh:
            lm_raw = np.array(inference.getLayerFp16("ld_3d")).reshape(-1, 5)
            lm_raw[:, :3] /= self.lm_input_length
            body.visibility = 1 / (1 + np.exp(-lm_raw[:, 3]))
            body.presence = 1 / (1 + np.exp(-lm_raw[:, 4]))
            body.norm_landmarks = lm_raw[:, :3]
            src = np.array([(0, 0), (1, 0), (1, 1)], dtype=np.float32)
            dst = np.array([(x, y) for x, y in body.rect_points[1:]], dtype=np.float32)
            mat = cv2.getAffineTransform(src, dst)
            lm_xy = np.expand_dims(body.norm_landmarks[: self.nb_kps + 2, :2], axis=0)
            lm_xy = np.squeeze(cv2.transform(lm_xy, mat))
            lm_z = body.norm_landmarks[: self.nb_kps + 2, 2:3] * body.rect_w_a / 4
            lm_xyz = np.hstack((lm_xy, lm_z))
            body.landmarks_world = np.array(
                inference.getLayerFp16("Identity_4")
            ).reshape(-1, 3)[: self.nb_kps]
            sin_rot = sin(body.rotation)
            cos_rot = cos(body.rotation)
            rot_m = np.array([[cos_rot, sin_rot], [-sin_rot, cos_rot]])
            body.landmarks_world[:, :2] = np.dot(body.landmarks_world[:, :2], rot_m)
            if self.smoothing:
                timestamp = time.perf_counter()
                object_scale = body.rect_w_a
                lm_xyz[: self.nb_kps] = self.filter_landmarks.apply(
                    lm_xyz[: self.nb_kps], timestamp, object_scale
                )
                lm_xyz[self.nb_kps :] = self.filter_landmarks_aux.apply(
                    lm_xyz[self.nb_kps :], timestamp, object_scale
                )
                body.landmarks_world = self.filter_landmarks_world.apply(
                    body.landmarks_world, timestamp
                )

            body.landmarks = lm_xyz.astype(np.float32)
            self.body_from_landmarks = mpu.Body(
                pd_kps=body.landmarks[self.nb_kps : self.nb_kps + 2, :2]
                / self.frame_size
            )

            if self.pad_h > 0:
                body.landmarks[:, 1] -= self.pad_h
                for i in range(len(body.rect_points)):
                    body.rect_points[i][1] -= self.pad_h
            if self.pad_w > 0:
                body.landmarks[:, 0] -= self.pad_w
                for i in range(len(body.rect_points)):
                    body.rect_points[i][0] -= self.pad_w

            body.landmarks[:, 0] = body.landmarks[:, 0] / self.w
            body.landmarks[:, 1] = body.landmarks[:, 1] / self.h

        return body

    def get_body(self, nn_node_names, image):
        frame_nn = dai.ImgFrame()
        frame_nn.setWidth(self.oakd_pipeline.nn_node_input_sizes["body_detection"][0])
        frame_nn.setHeight(self.oakd_pipeline.nn_node_input_sizes["body_detection"][1])
        frame_nn.setData(
            to_planar(
                image,
                (
                    self.oakd_pipeline.nn_node_input_sizes["body_detection"][0],
                    self.oakd_pipeline.nn_node_input_sizes["body_detection"][1],
                ),
            )
        )
        self.oakd_pipeline.set_input(nn_node_names[0], frame_nn)
        inference = self.oakd_pipeline.get_output(nn_node_names[1])
        return self.pd_postprocess(inference)
