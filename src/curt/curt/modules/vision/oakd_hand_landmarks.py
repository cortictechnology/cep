""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

Implementation reference: 

https://github.com/geaxgx/depthai_hand_tracker

"""

from curt.modules.vision.oakd_processing import OAKDProcessingWorker
import depthai as dai
from curt.modules.vision.utils import *
import curt.modules.vision.mediapipe_utils as mpu
import numpy as np
import logging
import time

def to_planar_local(arr: np.ndarray, shape: tuple) -> np.ndarray:
    return cv2.resize(arr, shape).transpose(2,0,1)

class OAKDHandLandmarks(OAKDProcessingWorker):
    def __init__(self):
        super().__init__()
        self.pd_score_thresh = 0.5
        self.pd_nms_thresh = 0.3
        self.lm_score_thresh = 0.5
        self.pad_h = 0
        self.pad_w = 0

        self.anchors = mpu.generate_handtracker_anchors()
        self.nb_anchors = self.anchors.shape[0]

        self.use_previous_landmarks = False
        self.single_hand_count = 0
        self.single_handed = False
        self.no_hand_count = 0
        self.hand_from_landmarks = {"left": None, "right": None}

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
        if isinstance(img, str):
            img = decode_image_byte(img)
        self.lm_input_length = self.oakd_pipeline.nn_node_input_sizes["hand_landmarks"][
            0
        ]
        if img is None:
            return None
        self.img = img
        image = img
        self.h, self.w = img.shape[:2]
        self.frame_size = max(self.h, self.w)
        if self.h != self.w:
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
        if not self.use_previous_landmarks:
            hands = self.get_palms(self.pd_nn_node_names, image)
        else:
            hands = [self.hand_from_landmarks["right"], self.hand_from_landmarks["left"]]
        return hands, image

    def execute_nn_operation(self, preprocessed_data):
        hands, image = preprocessed_data
        raw_inference_results = []
        for i, r in enumerate(hands):
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
                to_planar_local(
                    img_hand,
                    (
                        self.oakd_pipeline.nn_node_input_sizes["hand_landmarks"][0],
                        self.oakd_pipeline.nn_node_input_sizes["hand_landmarks"][1],
                    ),
                )
            )
            self.oakd_pipeline.set_input(self.pm_nn_node_names[0], frame_nn)
        for i, r in enumerate(hands):
            inference = self.oakd_pipeline.get_output(self.pm_nn_node_names[1])
            raw_inference_results.append(inference)
        return hands, raw_inference_results

    def postprocess_result(self, inference_results):
        hands, raw_inference_results = inference_results
        hand_landmarks = []
        for i, h in enumerate(hands):
            inference = raw_inference_results[i]
            self.lm_postprocess(h, inference)

        hands = [ h for h in hands if h.lm_score > self.lm_score_thresh]

        if len(hands) == 2:
            if hands[0].handedness > 0.5:
                self.hand_from_landmarks['right'] = mpu.hand_landmarks_to_rect(hands[0])
                self.hand_from_landmarks['left'] = mpu.hand_landmarks_to_rect(hands[1])
            else:
                self.hand_from_landmarks['right'] = mpu.hand_landmarks_to_rect(hands[1])
                self.hand_from_landmarks['left'] = mpu.hand_landmarks_to_rect(hands[0])
            self.use_previous_landmarks = True
        else:
            self.hand_from_landmarks = {"left": None, "right": None}
            self.use_previous_landmarks = False

        for hand in hands:
            # If we added padding to make the image square, we need to remove this padding from landmark coordinates and from rect_points
            if self.pad_h > 0:
                hand.landmarks[:,1] -= self.pad_h
                for i in range(len(hand.rect_points)):
                    hand.rect_points[i][1] -= self.pad_h
            if self.pad_w > 0:
                hand.landmarks[:,0] -= self.pad_w
                for i in range(len(hand.rect_points)):
                    hand.rect_points[i][0] -= self.pad_w

            #logging.warning("Landmark shape" + str(hand.landmarks.shape))
     
            
            max_x = 0
            max_y = 0
            min_x = self.img.shape[1]
            min_y = self.img.shape[0]
            for x, y, _ in hand.landmarks:
                if x < min_x:
                    min_x = x
                if x > max_x:
                    max_x = x
                if y < min_y:
                    min_y = y
                if y > max_y:
                    max_y = y

            hand.landmarks = hand.landmarks.astype(np.float32)
            for lm in hand.landmarks:
                lm[0] = float(lm[0]) / self.img.shape[1]
                lm[1] = float(lm[1]) / self.img.shape[0]

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
            hand_landmarks.append([hand.landmarks.tolist(), hand_bbox, hand.handedness])
        
        return hand_landmarks

    def pd_postprocess(self, inference):
        scores = np.array(inference.getLayerFp16("classificators"), dtype=np.float16) # 896
        bboxes = np.array(inference.getLayerFp16("regressors"), dtype=np.float16).reshape((self.nb_anchors,18)) # 896x18
        # Decode bboxes
        hands = mpu.decode_bboxes(self.pd_score_thresh, scores, bboxes, self.anchors, best_only=False)
        # Non maximum suppression 
        hands = mpu.non_max_suppression(hands, self.pd_nms_thresh)
        mpu.detections_to_rect(hands)
        mpu.rect_transformation(hands, self.frame_size, self.frame_size)
        return hands

    def lm_postprocess(self, hand, inference):
        hand.lm_score = inference.getLayerFp16("Identity_1")[0]
        if hand.lm_score > self.lm_score_thresh:
            hand.handedness = inference.getLayerFp16("Identity_2")[0]
            lm_raw = np.array(inference.getLayerFp16("Identity_dense/BiasAdd/Add")).reshape(-1,3)
            hand.norm_landmarks = lm_raw / self.lm_input_length
            src = np.array([(0, 0), (1, 0), (1, 1)], dtype=np.float32)
            dst = np.array([ (x, y) for x,y in hand.rect_points[1:]], dtype=np.float32)
            mat = cv2.getAffineTransform(src, dst)
            lm_xy = np.expand_dims(hand.norm_landmarks[:,:2], axis=0)
            lm_z = hand.norm_landmarks[:,2:3] * hand.rect_w_a  / 0.4
            landmarks_xy = np.squeeze(cv2.transform(lm_xy, mat)).astype(np.int)
            hand.landmarks = np.concatenate((landmarks_xy, lm_z), axis=1)
            return hand

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
