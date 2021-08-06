""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""


import tvm
from tvm.contrib import graph_runtime
import numpy as np
import cv2
import base64
from abc import abstractmethod
import os
import time

from curt.modules.vision.utils import decode_image_byte


class BaseVisionProcessing:
    def __init__(
        self,
        processor_type,
        model_graph,
        model_lib,
        model_params,
        input_node,
        num_output,
    ):
        if processor_type == "cpu":
            self.ctx = tvm.cpu()
        elif processor_type == "gpu":
            self.ctx = tvm.gpu()

        self.input_node = input_node

        self.num_output = num_output

        loaded_json = open(
            os.path.dirname(os.path.realpath(__file__))
            + "/../../../models/modules/vision/platforms/rpi32/"
            + model_graph
        ).read()
        loaded_lib = tvm.runtime.load_module(
            os.path.dirname(os.path.realpath(__file__))
            + "/../../../models/modules/vision/platforms/rpi32/"
            + model_lib
        )
        loaded_params = bytearray(
            open(
                os.path.dirname(os.path.realpath(__file__))
                + "/../../../models/modules/vision/platforms/rpi32/"
                + model_params,
                "rb",
            ).read()
        )
        self.inference_module = graph_runtime.create(loaded_json, loaded_lib, self.ctx)
        self.inference_module.load_params(loaded_params)

        self.input_width = None
        self.input_height = None
        self.friendly_name = ""

    @abstractmethod
    def preprocess_input(self, input_data):
        pass

    @abstractmethod
    def postprocess(self, inference_outputs, index=0):
        pass

    @abstractmethod
    def config_module(self, params):
        pass

    def run_inference(self, input_data):
        # t1 = time.time()
        data = input_data
        if isinstance(data, str):
            data = decode_image_byte(data)
        preprocessed_data = self.preprocess_input(data)
        if isinstance(preprocessed_data, list):
            if len(preprocessed_data) > 0:
                results = []
                for i in range(len(preprocessed_data)):
                    data = preprocessed_data[i]
                    self.inference_module.set_input(self.input_node, tvm.nd.array(data))
                    self.inference_module.run()
                    inference_outputs = []
                    for j in range(self.num_output):
                        inference_outputs.append(
                            self.inference_module.get_output(j).asnumpy()
                        )
                    results.append(self.postprocess(inference_outputs, i))
                # print("Inference time:", time.time() - t1)
                return results
        else:
            if preprocessed_data is not None:
                self.inference_module.set_input(
                    self.input_node, tvm.nd.array(preprocessed_data)
                )
                self.inference_module.run()
                inference_outputs = []
                for i in range(self.num_output):
                    inference_outputs.append(
                        self.inference_module.get_output(i).asnumpy()
                    )
                result = self.postprocess(inference_outputs)
                # print("Inference time:", time.time() - t1)
                return result
        return []
