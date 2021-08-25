""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, March 2021

Implementation reference: 

https://github.com/geaxgx/depthai_hand_tracker

"""

from curt.modules.vision.oakd_processing import OAKDProcessingWorker
import depthai as dai
from curt.modules.vision.utils import *
import curt.modules.vision.mediapipe_utils as mpu
import numpy as np
import logging


class OAKDHandLandmarks(OAKDProcessingWorker):
    def __init__(self):
        super().__init__()
        self.pd_score_thresh = 0.46
        self.pd_nms_thresh = 0.3
        self.lm_score_threshold = 0.5

        anchor_options = mpu.SSDAnchorOptions(
            num_layers=4,
            min_scale=0.1484375,
            max_scale=0.75,
            input_size_height=128,
            input_size_width=128,
            anchor_offset_x=0.5,
            anchor_offset_y=0.5,
            strides=[8, 16, 16, 16],
            aspect_ratios=[1.0],
            reduce_boxes_in_lowest_layer=False,
            interpolated_scale_aspect_ratio=1.0,
            fixed_anchor_size=True,
        )

        self.anchors = mpu.generate_anchors(anchor_options)
        self.nb_anchors = self.anchors.shape[0]

    def preprocess_input(self, params):
        if "palm_detection" not in self.oakd_pipeline.xlink_nodes:
            logging.warning("No such node: palm_detection in the pipeline")
            return None
        if "hand_landmarks" not in self.oakd_pipeline.xlink_nodes:
            logging.warning("No such node: hand_landmarks in the pipeline")
            return None
        self.pd_nn_node_names = self.oakd_pipeline.xlink_nodes["palm_detection"]
        self.pm_nn_node_names = self.oakd_pipeline.xlink_nodes["hand_landmarks"]
        img = params[0]

        # self.pd_nn_node_name = pd_nn_node_name
        # self.pm_nn_node_name = pm_nn_node_name
        self.lm_input_length = self.oakd_pipeline.nn_node_input_sizes["hand_landmarks"][
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
        palm_regions = self.get_palms(self.pd_nn_node_names, image)
        return palm_regions, image

    def execute_nn_operation(self, preprocessed_data):
        palm_regions, image = preprocessed_data
        raw_inference_results = []
        for i, r in enumerate(palm_regions):
            img_hand = mpu.warp_rect_img(
                r.rect_points,
                image,
                self.oakd_pipeline.nn_node_input_sizes["hand_landmarks"][0],
                self.oakd_pipeline.nn_node_input_sizes["hand_landmarks"][1],
            )
            frame_nn = dai.ImgFrame()
            frame_nn.setWidth(
                self.oakd_pipeline.nn_node_input_sizes["hand_landmarks"][0]
            )
            frame_nn.setHeight(
                self.oakd_pipeline.nn_node_input_sizes["hand_landmarks"][1]
            )
            frame_nn.setData(
                to_planar(
                    img_hand,
                    (
                        self.oakd_pipeline.nn_node_input_sizes["hand_landmarks"][0],
                        self.oakd_pipeline.nn_node_input_sizes["hand_landmarks"][1],
                    ),
                )
            )
            self.oakd_pipeline.set_input(self.pm_nn_node_names[0], frame_nn)
        for i, r in enumerate(palm_regions):
            inference = self.oakd_pipeline.get_output(self.pm_nn_node_names[1])
            raw_inference_results.append(inference)
        return palm_regions, raw_inference_results

    def postprocess_result(self, inference_results):
        palm_regions, raw_inference_results = inference_results
        hand_landmarks = []
        for i, r in enumerate(palm_regions):
            inference = raw_inference_results[i]
            region = self.lm_postprocess(r, inference)
            if region.lm_score > self.lm_score_threshold:
                src = np.array([(0, 0), (1, 0), (1, 1)], dtype=np.float32)
                dst = np.array(
                    [(x, y) for x, y in region.rect_points[1:]], dtype=np.float32
                )  # region.rect_points[0] is left bottom point !
                mat = cv2.getAffineTransform(src, dst)
                lm_xy = np.expand_dims(
                    np.array([(l[0], l[1]) for l in region.landmarks]), axis=0
                )
                lm_xy = np.squeeze(cv2.transform(lm_xy, mat))
                for lm in lm_xy:
                    lm[0] = lm[0] - self.pad_w
                    lm[1] = lm[1] - self.pad_h
                max_x = 0
                max_y = 0
                min_x = self.img.shape[1]
                min_y = self.img.shape[0]
                for x, y in lm_xy:
                    if x < min_x:
                        min_x = x
                    if x > max_x:
                        max_x = x
                    if y < min_y:
                        min_y = y
                    if y > max_y:
                        max_y = y

                for lm in lm_xy:
                    lm[0] = float(lm[0] / self.img.shape[1])
                    lm[1] = float(lm[1] / self.img.shape[0])

                box_width = max_x - min_x
                box_height = max_y - min_y
                x_center = min_x + box_width / 2
                y_center = min_y + box_height / 2

                new_width = box_width / 2 * 1.5
                new_height = box_height / 2 * 1.5
                new_size = max(new_width, new_height)

                min_x = x_center - new_size
                min_y = y_center - new_size
                max_x = x_center + new_size
                max_y = y_center + new_size

                if min_x < 0:
                    min_x = 0
                if min_y < 0:
                    min_y = 0
                if max_x > self.img.shape[1]:
                    max_x = self.img.shape[1] - 1
                if max_y > self.img.shape[0]:
                    max_y = self.img.shape[0] - 1
                hand_bbox = [
                    float(min_x / self.img.shape[1]),
                    float(min_y / self.img.shape[0]),
                    float(max_x / self.img.shape[1]),
                    float(max_y / self.img.shape[0]),
                ]
                hand_landmarks.append([lm_xy.tolist(), hand_bbox, region.handedness])
        return hand_landmarks

    def pd_postprocess(self, inference):
        scores = np.array(
            inference.getLayerFp16("classificators"), dtype=np.float16
        )  # 896
        bboxes = np.array(
            inference.getLayerFp16("regressors"), dtype=np.float16
        ).reshape(
            (self.nb_anchors, 18)
        )  # 896x18
        # Decode bboxes
        regions = mpu.decode_bboxes(self.pd_score_thresh, scores, bboxes, self.anchors)
        # Non maximum suppression
        regions = mpu.non_max_suppression(regions, self.pd_nms_thresh)
        mpu.detections_to_rect(regions)
        mpu.rect_transformation(regions, self.frame_size, self.frame_size)
        return regions

    def lm_postprocess(self, region, inference):
        region.lm_score = inference.getLayerFp16("Identity_1")[0]
        region.handedness = inference.getLayerFp16("Identity_2")[0]
        lm_raw = np.array(inference.getLayerFp16("Identity_dense/BiasAdd/Add"))
        lm = []
        for i in range(int(len(lm_raw) / 3)):
            # x,y,z -> x/w,y/h,z/w (here h=w)
            lm.append(lm_raw[3 * i : 3 * (i + 1)] / self.lm_input_length)
        region.landmarks = lm
        return region

    def get_palms(self, nn_node_names, image):
        frame_nn = dai.ImgFrame()
        frame_nn.setWidth(self.oakd_pipeline.nn_node_input_sizes["palm_detection"][0])
        frame_nn.setHeight(self.oakd_pipeline.nn_node_input_sizes["palm_detection"][1])
        frame_nn.setData(
            to_planar(
                image,
                (
                    self.oakd_pipeline.nn_node_input_sizes["palm_detection"][0],
                    self.oakd_pipeline.nn_node_input_sizes["palm_detection"][1],
                ),
            )
        )
        self.oakd_pipeline.set_input(nn_node_names[0], frame_nn)
        inference = self.oakd_pipeline.get_output(nn_node_names[1])
        return self.pd_postprocess(inference)
