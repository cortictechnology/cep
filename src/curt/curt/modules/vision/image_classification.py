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
import logging
from curt.modules.vision.utils import decode_image_byte, image_labels
from curt.modules.vision.tvm_processing import TVMProcessing

class ImageClassification(TVMProcessing):
    def __init__(self):
        super().__init__(  "cpu", 
                           "tuned32_efficientnet_lite.json", 
                           "tuned32_efficientnet_lite_lib.tar", 
                           "tuned32_efficientnet_lite_param.params",
                           "images",
                           1)
        self.input_width = 224
        self.input_height = 224
        self.friendly_name = "image_classification_pi"


    def preprocess_input(self, params):
        img = params[0]
        if img is None:
            logging.warning("Image Classification: " + "imgae is None")
            return None
        if isinstance(img, str):
            img = decode_image_byte(img)
        
        img = cv2.resize(img, (self.input_width, self.input_height), interpolation=cv2.INTER_NEAREST)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.astype("float32")
        img = cv2.normalize(img, None, -0.992188, 1, cv2.NORM_MINMAX)
        img = img[np.newaxis, :]

        return img

    def process_data(self, preprocessed_data):
        return self.tvm_process(preprocessed_data)

    def postprocess_result(self, data):
        inference_outputs = data[0][0].squeeze()
        top5 = (-inference_outputs).argsort()[:5]
        classified_results = []
        for idx in top5:
            label = image_labels[idx]
            probability = inference_outputs[idx]
            if label.find(",") != -1:
                label = label[0:label.find(",")]
            classified_results.append([label, probability.astype(float)])
        return classified_results
