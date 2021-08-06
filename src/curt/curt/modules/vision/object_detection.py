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

from curt.modules.vision.base_vision_processing import BaseVisionProcessing

class ObjectDetection(BaseVisionProcessing):

    def __init__(self):
        super().__init__(  "cpu", 
                           "tuned_facemesh_graph.json", 
                           "tuned_facemesh_lib.tar", 
                           "tuned_facemesh_param.params",
                           "input_1",
                           2)
        self.input_width = 320
        self.input_height = 320


    def preprocess_input(self, input_data):
        pass

    def postprocess(self, inference_outputs, index=0):
        pass
