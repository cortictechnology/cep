""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

import tvm
from tvm.contrib import graph_runtime
import numpy as np
import time
from scipy.special import expit, logit
import cv2
import math
import os
import logging
from curt.modules.vision.utils import decode_image_byte
from curt.modules.vision.tvm_processing import TVMProcessing

class ObjectDetection(TVMProcessing):

    def __init__(self):
        super().__init__(  "cpu", 
                           "tuned32_ssdlite.json", 
                           "tuned32_ssdlite_lib.tar", 
                           "tuned32_ssdlite_param.params",
                           "normalized_input_image_tensor",
                           2)
        self.input_width = 320
        self.input_height = 320
        self.detection_threshold = 0.5
        self.anchors = np.load(os.path.dirname(os.path.realpath(__file__)) + "/../../../models/modules/vision/platforms/rpi32/obj_anchors.npy")
        self.friendly_name = "object_detection_pi"


    def preprocess_input(self, params):
        img = params[0]
        if img is None:
            logging.warning("Object detection: " + "imgae is None")
            return None
        if isinstance(img, str):
            img = decode_image_byte(img)
        
        img = cv2.resize(img, (self.input_width, self.input_height), interpolation=cv2.INTER_NEAREST)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.astype("float32")
        img = cv2.normalize(img, None, -1, 1, cv2.NORM_MINMAX)
        img = img[np.newaxis, :]

        return img

    def decode_boxes(self, raw_boxes, anchors):
        """Converts the predictions into actual coordinates using
        the anchor boxes. Processes the entire batch at once.
        """
        boxes = np.zeros(raw_boxes.shape)

        x_center = raw_boxes[..., 1] / 10.0 * anchors[:, 2] + anchors[:, 0]
        y_center = raw_boxes[..., 0] / 10.0 * anchors[:, 3] + anchors[:, 1]

        w = np.exp(raw_boxes[..., 3] / 5.0) * anchors[:, 2]
        h = np.exp(raw_boxes[..., 2] / 5.0) * anchors[:, 3]

        boxes[..., 0] = y_center - h / 2.  # ymin
        boxes[..., 1] = x_center - w / 2.  # xmin
        boxes[..., 2] = y_center + h / 2.  # ymax
        boxes[..., 3] = x_center + w / 2.  # xmax

        return boxes


    def tensors_to_detections(self, raw_box_tensor, raw_score_tensor, anchors):
        assert raw_box_tensor.ndim == 3
        assert raw_box_tensor.shape[1] == 2034
        assert raw_box_tensor.shape[2] == 4

        assert raw_score_tensor.ndim == 3
        assert raw_score_tensor.shape[1] == 2034
        assert raw_score_tensor.shape[2] == 91

        assert raw_box_tensor.shape[0] == raw_score_tensor.shape[0]
        
        detection_boxes = self.decode_boxes(raw_box_tensor, anchors)

        detection_scores_exp = expit(raw_score_tensor)

        detection_classes = detection_scores_exp.argmax(axis=2)

        detection_scores = np.amax(detection_scores_exp, axis=2)

        mask = detection_scores >= self.detection_threshold

        output_detections = []
        for i in range(raw_box_tensor.shape[0]):
            boxes = detection_boxes[i, mask[i]]
            classes = detection_classes[i, mask[i]][:, np.newaxis]
            scores = detection_scores[i, mask[i]][:, np.newaxis]
            output_detections.append(np.concatenate((boxes, classes, scores), axis=1))

        return output_detections


    def intersect(self, box_a, box_b):
        """ We resize both tensors to [A,B,2] without new malloc:
        [A,2] -> [A,1,2] -> [A,B,2]
        [B,2] -> [1,B,2] -> [A,B,2]
        Then we compute the area of intersect between box_a and box_b.
        Args:
        box_a: (tensor) bounding boxes, Shape: [A,4].
        box_b: (tensor) bounding boxes, Shape: [B,4].
        Return:
        (tensor) intersection area, Shape: [A,B].
        """
        A = box_a.shape[0]
        B = box_b.shape[0]
        max_xy = np.minimum(np.broadcast_to(box_a[:, 2:][:, np.newaxis, :], (A, B, 2)),
                        np.broadcast_to(box_b[:, 2:][np.newaxis, :], ((A, B, 2))))
        min_xy = np.maximum(np.broadcast_to(box_a[:, :2][:, np.newaxis, :], (A, B, 2)),
                        np.broadcast_to(box_b[:, :2][np.newaxis, :], ((A, B, 2))))
        inter = np.clip((max_xy - min_xy), 0, None)
        return inter[:, :, 0] * inter[:, :, 1]


    def jaccard(self, box_a, box_b):
        """Compute the jaccard overlap of two sets of boxes.  The jaccard overlap
        is simply the intersection over union of two boxes.  Here we operate on
        ground truth boxes and default boxes.
        E.g.:
            A ∩ B / A ∪ B = A ∩ B / (area(A) + area(B) - A ∩ B)
        Args:
            box_a: (tensor) Ground truth bounding boxes, Shape: [num_objects,4]
            box_b: (tensor) Prior boxes from priorbox layers, Shape: [num_priors,4]
        Return:
            jaccard overlap: (tensor) Shape: [box_a.size(0), box_b.size(0)]
        """

        inter = self.intersect(box_a, box_b)
        area_a = np.broadcast_to(((box_a[:, 2]-box_a[:, 0]) *
                (box_a[:, 3]-box_a[:, 1]))[:, np.newaxis], inter.shape)  # [A,B]
        area_b = np.broadcast_to(((box_b[:, 2]-box_b[:, 0]) *
                (box_b[:, 3]-box_b[:, 1]))[np.newaxis, :], inter.shape)  # [A,B]
        union = area_a + area_b - inter
        return inter / union  # [A,B]


    def overlap_similarity(self, box, other_boxes):
        """Computes the IOU between a bounding box and set of other boxes."""
        return self.jaccard(box[np.newaxis, :], other_boxes).squeeze(axis=0)

    
    def weighted_non_max_suppression(self, detections):
        if len(detections) == 0: return []

        all_detections = {}
        
        filtered_detections = []

        for det in detections:
            if det[4] not in all_detections:
                all_detections[det[4]] = np.array([det])
            else:
                all_detections[det[4]] = np.vstack((all_detections[det[4]], np.array(det)))

        for class_id in all_detections:
            dets = all_detections[class_id]
            remaining = np.argsort(-dets[:, 5])
            while len(remaining) > 0:
                det = dets[remaining[0]]
                first_box = det[:4]
                other_boxes = dets[remaining, :4]
                ious = self.overlap_similarity(first_box, other_boxes)
                mask = ious > 0.4
                overlapping = remaining[mask]
                remaining = remaining[~mask]
                weighted_detection = np.copy(det)
                if len(overlapping) > 1:
                    coordinates = dets[overlapping, :4]
                    scores = dets[overlapping, 5:6]
                    total_score = scores.sum()
                    weighted = (coordinates * scores).sum(axis=0) / total_score
                    weighted_detection[:4] = weighted
                    weighted_detection[5] = total_score / len(overlapping)
                filtered_detections.append(weighted_detection)

        return filtered_detections

    def process_data(self, preprocessed_data):
        return self.tvm_process(preprocessed_data)

    def postprocess_result(self, data):
        inference_outputs = data[0]
        raw_box_tensor = inference_outputs[0]
        #print(raw_box_tensor)
        raw_score_tensor = inference_outputs[1]
        detections = self.tensors_to_detections(raw_box_tensor, raw_score_tensor, self.anchors)[0]
        filtered_detections = []
        objects = self.weighted_non_max_suppression(detections)
        for obj in objects:
            bbox = [obj[1], obj[0], obj[3], obj[2], obj[4]]
            filtered_detections.append(bbox)
        return filtered_detections
