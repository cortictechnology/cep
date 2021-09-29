""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""


import tvm
from tvm.contrib import graph_runtime
import numpy as np
import time
#from scipy.special import expit
import cv2
import math
import os

from curt.modules.vision.tvm_processing import TVMProcessing

class FaceDetection(TVMProcessing):

    def __init__(self):
        super().__init__("cpu", 
                           "tuned_blazeface_graph.json", 
                           "tuned_blazeface_lib.tar", 
                           "tuned_blazeface_param.params", 
                           "input", 
                           2)
        self.input_width = 128
        self.input_height = 128
        self.value = [0, 0, 0]
        self.borderType = cv2.BORDER_CONSTANT
        self.anchors = np.load(os.path.dirname(os.path.realpath(__file__)) + "/../../../models/modules/vision/platforms/rpi32/anchors.npy")
        self.one_face_mode = False

    
    def config_worker(self, params):
        if params['Mode'] == "OneFace":
            self.one_face_mode = True
        elif params['Mode'] == "MultiFace":
            self.one_face_mode = False
        return True


    def preprocess_input(self, input_data):
        self.top = 0
        self.bottom = 0
        self.right = 0
        self.left = 0
        self.dim = None
        self.resize_ratio = 1

        img = input_data[0]

        self.img_width = img.shape[1]
        self.img_height = img.shape[0]

        if img.shape[0] < img.shape[1]:
            self.resize_ratio = img.shape[1] / self.input_width
            width = int(img.shape[1] / self.resize_ratio)
            height = int(img.shape[0] / self.resize_ratio)
            dim = (width, height)
            self.right = int(self.input_width - width)
            self.top = int((width - height) /2 )
            self.bottom = int(width - (height + self.top))
        else:
            self.resize_ratio = img.shape[0] / self.input_height
            width = int(img.shape[1] / self.resize_ratio)
            height = int(img.shape[0] / self.resize_ratio)
            dim = (width, height)
            self.top = int(self.input_height - height)
            self.right = int((height - width) / 2)
            self.left = int(height - (width + self.right))

        img = cv2.resize(img, dim, interpolation=cv2.INTER_NEAREST)
        img = cv2.copyMakeBorder(img, self.top, self.bottom, self.left, self.right, self.borderType, None, self.value)
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

        x_center = raw_boxes[..., 0] / 128.0 * anchors[:, 2] + anchors[:, 0]
        y_center = raw_boxes[..., 1] / 128.0 * anchors[:, 3] + anchors[:, 1]

        w = raw_boxes[..., 2] / 128.0 * anchors[:, 2]
        h = raw_boxes[..., 3] / 128.0 * anchors[:, 3]

        boxes[..., 0] = y_center - h / 2.  # ymin
        boxes[..., 1] = x_center - w / 2.  # xmin
        boxes[..., 2] = y_center + h / 2.  # ymax
        boxes[..., 3] = x_center + w / 2.  # xmax

        for k in range(6):
            offset = 4 + k*2
            keypoint_x = raw_boxes[..., offset    ] / 128.0 * anchors[:, 2] + anchors[:, 0]
            keypoint_y = raw_boxes[..., offset + 1] / 128.0 * anchors[:, 3] + anchors[:, 1]
            boxes[..., offset    ] = keypoint_x
            boxes[..., offset + 1] = keypoint_y

        return boxes


    def tensors_to_detections(self, raw_box_tensor, raw_score_tensor, anchors):
        assert raw_box_tensor.ndim == 3
        assert raw_box_tensor.shape[1] == 896
        assert raw_box_tensor.shape[2] == 16

        assert raw_score_tensor.ndim == 3
        assert raw_score_tensor.shape[1] == 896
        assert raw_score_tensor.shape[2] == 1

        assert raw_box_tensor.shape[0] == raw_score_tensor.shape[0]
        
        detection_boxes = self.decode_boxes(raw_box_tensor, anchors)
        
        thresh = 100.0
        raw_score_tensor = np.clip(raw_score_tensor, -thresh, thresh)
        #detection_scores = expit(raw_score_tensor).squeeze(axis=2)
        detection_scores = (1.0 / (1 + np.exp(-raw_score_tensor))).squeeze(axis=2)
        
        # Note: we stripped off the last dimension from the scores tensor
        # because there is only has one class. Now we can simply use a mask
        # to filter out the boxes with too low confidence.
        mask = detection_scores >= 0.85
        # Because each image from the batch can have a different number of
        # detections, process them one at a time using a loop.
        output_detections = []
        for i in range(raw_box_tensor.shape[0]):
            boxes = detection_boxes[i, mask[i]]
            scores = detection_scores[i, mask[i]][:, np.newaxis]
            output_detections.append(np.concatenate((boxes, scores), axis=1))

        #print(output_detections)
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
        #print("AAAAAAAAAAAA")
        np.broadcast_to(box_a[:, 2:][:, np.newaxis, :], (A, B, 2))
        max_xy = np.minimum(np.broadcast_to(box_a[:, 2:][:, np.newaxis, :], (A, B, 2)),
                        np.broadcast_to(box_b[:, 2:][np.newaxis, :], ((A, B, 2))))
        #print("------------------------------")
        #print(max_xy)
        #print("AAAAAAAAAAAA")
        #print(np.broadcast_to(box_a[:, :2][:, np.newaxis, :], (A, B, 2)))
        min_xy = np.maximum(np.broadcast_to(box_a[:, :2][:, np.newaxis, :], (A, B, 2)),
                        np.broadcast_to(box_b[:, :2][np.newaxis, :], ((A, B, 2))))
        #print("+++++++++++++++++++++++++++++++")
        #print(min_xy)
        inter = np.clip((max_xy - min_xy), 0, None)
        #print("******************************")
        #print(inter)
        return inter[:, :, 0] * inter[:, :, 1]


    def jaccard(self, box_a, box_b):
        """Compute the jaccard overlap of two sets of boxes.  The jaccard overlap
        is simply the intersection over union of two boxes.  Here we operate on
        ground truth boxes and default boxes.
        E.g.:
            A â© B / A âª B = A â© B / (area(A) + area(B) - A â© B)
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
            """The alternative NMS method as mentioned in the BlazeFace paper:
            "We replace the suppression algorithm with a blending strategy that
            estimates the regression parameters of a bounding box as a weighted
            mean between the overlapping predictions."
            The original MediaPipe code assigns the score of the most confident
            detection to the weighted detection, but we take the average score
            of the overlapping detections.
            The input detections should be a Tensor of shape (count, 17).
            Returns a list of PyTorch tensors, one for each detected face.
            
            This is based on the source code from:
            mediapipe/calculators/util/non_max_suppression_calculator.cc
            mediapipe/calculators/util/non_max_suppression_calculator.proto
            """
            if len(detections) == 0: return []

            output_detections = []

            # Sort the detections from highest to lowest score.
            remaining = np.argsort(-detections[:, 16])

            while len(remaining) > 0:
                detection = detections[remaining[0]]
                # Compute the overlap between the first box and the other 
                # remaining boxes. (Note that the other_boxes also include
                # the first_box.)
                first_box = detection[:4]
                other_boxes = detections[remaining, :4]
                ious = self.overlap_similarity(first_box, other_boxes)

                # If two detections don't overlap enough, they are considered
                # to be from different faces.
                mask = ious > 0.4
                overlapping = remaining[mask]
                remaining = remaining[~mask]

                # Take an average of the coordinates from the overlapping
                # detections, weighted by their confidence scores.
                weighted_detection = np.copy(detection)
                if len(overlapping) > 1:
                    coordinates = detections[overlapping, :16]
                    scores = detections[overlapping, 16:17]
                    total_score = scores.sum()
                    weighted = (coordinates * scores).sum(axis=0) / total_score
                    weighted_detection[:16] = weighted
                    weighted_detection[16] = total_score / len(overlapping)

                output_detections.append(weighted_detection)

            return output_detections  


    def postprocess_result(self, inference_outputs):
        raw_box_tensor = inference_outputs[0]
        #print(raw_box_tensor)
        raw_score_tensor = inference_outputs[1]

        detections = self.tensors_to_detections(raw_box_tensor, raw_score_tensor, self.anchors)
        filtered_detections = []
        for i in range(len(detections)):
            faces = self.weighted_non_max_suppression(detections[i])
            for face in faces:
                face_info = {}
                scaled_coordinates = []
                ymin = float((face[0] * 128 - self.top) * self.resize_ratio)
                xmin = float((face[1] * 128 - self.left) * self.resize_ratio)
                ymax = float((face[2] * 128 - self.top) * self.resize_ratio)
                xmax = float((face[3] * 128 - self.left) * self.resize_ratio)
                
                scaled_coordinates.append(xmin / self.img_width)
                scaled_coordinates.append(ymin / self.img_height)
                scaled_coordinates.append(xmax / self.img_width)
                scaled_coordinates.append(ymax / self.img_height)
                face_info['face_coordinates'] = scaled_coordinates
                scaled_coordinates = []
                raw_coordinates = []
                for k in range(6):
                    #kp_x = int((face[4+k*2] * 128 - self.left) * self.resize_ratio)
                    #scaled_coordinates.append(kp_x)
                    raw_coordinates.append(face[4+k*2])
                    #kp_y = int((face[4+k*2+1] * 128 - self.top) * self.resize_ratio)
                    #scaled_coordinates.append(kp_y)
                    raw_coordinates.append(face[4+k*2+1])
                #face_info['landmark_coordinates'] = scaled_coordinates
                face_info['landmark_coordinates'] = raw_coordinates
                filtered_detections.append(face_info)

        return filtered_detections
