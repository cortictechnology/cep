""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""


import tvm
from tvm.contrib import graph_runtime
import numpy as np
import time
import cv2
import math
import os

from curt.modules.vision.tvm_processing import TVMProcessing
from curt.data import M_PI, triangulation 

class FaceMesh(TVMProcessing):

    def __init__(self):
        super().__init__(  "cpu", 
                           "tuned_facemesh_graph.json", 
                           "tuned_facemesh_lib.tar", 
                           "tuned_facemesh_param.params",
                           "input_1",
                           2)
        self.input_width = 192
        self.input_height = 192
        self.value = [0, 0, 0]
        self.borderType = cv2.BORDER_CONSTANT

    def preprocess_input(self, input_data):
        self.scale_xs = []
        self.scale_ys = []
        self.xmin_crops = []
        self.ymin_crops = []
        self.lefts = []
        self.tops = []
        img = input_data['camera_input']
        detected_faces = input_data['face_detection']
        if len(detected_faces) == 0:
            return []
        top = 0
        bottom = 0
        left = 0
        right = 0
        preprocessed_data = []
        for face in detected_faces:
            #t1 = time.time()
            ymin = face['face_coordinates'][0]
            xmin = face['face_coordinates'][1]
            ymax = face['face_coordinates'][2]
            xmax = face['face_coordinates'][3]
        
            box_width = xmax - xmin
            box_height = ymax - ymin

            x_center = xmin + box_width / 2
            y_center = ymin + box_height / 2

            new_width = box_width/2 * 1.5
            new_height = box_height/2 * 1.85

            xmin_crop = int(x_center - new_width)
            ymin_crop = int(y_center - new_height)
            xmax_crop = int(x_center + new_width)
            ymax_crop = int(y_center + new_height)

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

            crop_img = img[ymin_crop:ymax_crop , xmin_crop:xmax_crop , :]
            crop_img = cv2.copyMakeBorder(crop_img, top, bottom, left, right, self.borderType, None, self.value)
            dim = (self.input_width, self.input_height)
            scale_x = crop_img.shape[1] / float(self.input_width)
            scale_y = crop_img.shape[0] / float(self.input_height)
            image = cv2.resize(crop_img, dim, interpolation=cv2.INTER_NEAREST)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = image.astype("float32")
            image = cv2.normalize(image, None, 0, 1, cv2.NORM_MINMAX)
            image = image[np.newaxis, :]
            preprocessed_data.append(image)
            self.scale_xs.append(scale_x)
            self.scale_ys.append(scale_y)
            self.xmin_crops.append(xmin_crop)
            self.ymin_crops.append(ymin_crop)
            self.lefts.append(left)
            self.tops.append(top)

        return preprocessed_data


    def postprocess_result(self, inference_outputs, index=0):
        scale_x = self.scale_xs[index]
        scale_y = self.scale_ys[index]
        xmin_crop = self.xmin_crops[index]
        ymin_crop = self.ymin_crops[index]
        left = self.lefts[index]
        top = self.tops[index]
        coordinates = np.squeeze(inference_outputs[0]).reshape((-1, 3))
        flag = inference_outputs[1][0,0,0,0]
        coordinates[:,0] = coordinates[:,0] * scale_x + xmin_crop - left
        coordinates[:,1] = coordinates[:,1] * scale_y + ymin_crop - top
        coordinates[:,2] = coordinates[:,2]  * scale_x

        face_info = {}
        face_info['mesh_coordinates'] = coordinates.tolist()
        return face_info