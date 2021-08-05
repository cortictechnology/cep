""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, March 2021

"""

from curt.modules.vision.oakd_processing_worker import OAKDProcessingWorker
import depthai as dai
from curt.modules.vision.utils import *
from curt.modules.vision.utils import decode_image_byte
import numpy as np
import logging
import os
import time


class OAKDFaceMesh(OAKDProcessingWorker):
    def __init__(self):
        super().__init__()

    def preprocessing(self, params):
        img, detected_faces = params
        if img is None:
            return None
        if isinstance(img, str):
            img = decode_image_byte(img)
        if "facemesh" not in self.oakd_pipeline.xlink_nodes:
            logging.warning("No such node: facemesh in the pipeline")
            return []
        self.fm_nn_node_names = self.oakd_pipeline.xlink_nodes["facemesh"]
        self.width = img.shape[1]
        self.height = img.shape[0]
        face_frames = []
        lefts = []
        tops = []
        xmin_crops = []
        ymin_crops = []
        scale_xs = []
        scale_ys = []
        for detection in np.array(detected_faces):
            detection[0] = int(detection[0] * img.shape[1])
            detection[1] = int(detection[1] * img.shape[0])
            detection[2] = int(detection[2] * img.shape[1])
            detection[3] = int(detection[3] * img.shape[0])

            box_width = detection[2] - detection[0]
            box_height = detection[3] - detection[1]

            x_center = detection[0] + box_width / 2
            y_center = detection[1] + box_height / 2

            new_width = box_width / 2 * 1.5
            new_height = box_height / 2 * 1.5

            xmin_crop = int(x_center - new_width)
            ymin_crop = int(y_center - new_height)
            xmax_crop = int(x_center + new_width)
            ymax_crop = int(y_center + new_height)

            top = 0
            bottom = 0
            left = 0
            right = 0
            if ymin_crop < 0:
                top = ymin_crop * -1
                ymin_crop = 0
            if xmin_crop < 0:
                left = xmin_crop * -1
                xmin_crop = 0
            if ymax_crop >= img.shape[0]:
                bottom = ymax_crop - (img.shape[0] - 1)
                ymax_crop = img.shape[0] - 1
            if xmax_crop >= img.shape[1]:
                right = xmax_crop - (img.shape[1] - 1)
                xmax_crop = img.shape[1] - 1

            crop_img = img[ymin_crop:ymax_crop, xmin_crop:xmax_crop, :]
            crop_img = cv2.copyMakeBorder(
                crop_img,
                top,
                bottom,
                left,
                right,
                cv2.BORDER_CONSTANT,
                None,
                [0, 0, 0],
            )
            scale_x = crop_img.shape[1] / float(
                self.oakd_pipeline.nn_node_input_sizes["facemesh"][0]
            )
            scale_y = crop_img.shape[0] / float(
                self.oakd_pipeline.nn_node_input_sizes["facemesh"][1]
            )
            face_frames.append(crop_img)
            lefts.append(left)
            tops.append(top)
            xmin_crops.append(xmin_crop)
            ymin_crops.append(ymin_crop)
            scale_xs.append(scale_x)
            scale_ys.append(scale_y)

        return face_frames, lefts, tops, xmin_crops, ymin_crops, scale_xs, scale_ys

    def execute_nn_operation(self, preprocessed_data):
        (
            face_frames,
            lefts,
            tops,
            xmin_crops,
            ymin_crops,
            scale_xs,
            scale_ys,
        ) = preprocessed_data
        raw_facemeshes = []
        for face_frame in face_frames:
            facemesh = self.get_facemesh_single(self.fm_nn_node_names, face_frame)
            raw_facemeshes.append(facemesh)
        return raw_facemeshes, lefts, tops, xmin_crops, ymin_crops, scale_xs, scale_ys

    def postprocessing(self, inference_results):
        (
            raw_facemeshes,
            lefts,
            tops,
            xmin_crops,
            ymin_crops,
            scale_xs,
            scale_ys,
        ) = inference_results
        facemeshes = []
        for i in range(len(raw_facemeshes)):
            facemesh = raw_facemeshes[i]
            left = lefts[i]
            top = tops[i]
            xmin_crop = xmin_crops[i]
            ymin_crop = ymin_crops[i]
            scale_x = scale_xs[i]
            scale_y = scale_ys[i]
            coordinates = np.squeeze(facemesh).reshape((-1, 3))
            coordinates[:, 0] = (
                coordinates[:, 0] * scale_x + xmin_crop - left
            ) / self.width
            coordinates[:, 1] = (
                coordinates[:, 1] * scale_y + ymin_crop - top
            ) / self.height
            coordinates[:, 2] = coordinates[:, 2] * scale_x

            facemeshes.append(coordinates.tolist())
        return facemeshes

    def get_facemesh_single(self, nn_node_names, aligned_face):
        frame_fm = dai.ImgFrame()
        frame_fm.setWidth(self.oakd_pipeline.nn_node_input_sizes["facemesh"][0])
        frame_fm.setHeight(self.oakd_pipeline.nn_node_input_sizes["facemesh"][1])
        frame_fm.setData(
            to_planar(
                aligned_face,
                (
                    self.oakd_pipeline.nn_node_input_sizes["facemesh"][0],
                    self.oakd_pipeline.nn_node_input_sizes["facemesh"][1],
                ),
            )
        )
        self.oakd_pipeline.set_input(nn_node_names[0], frame_fm)
        facemesh = self.oakd_pipeline.get_output(nn_node_names[1]).getFirstLayerFp16()
        return facemesh
