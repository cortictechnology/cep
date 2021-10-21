""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

import os
import tvm
from tvm.contrib import graph_runtime
import numpy as np
from curt.modules.vision.base_vision_processing import BaseVisionProcessing
import logging

class TVMProcessing(BaseVisionProcessing):
    def __init__(
        self,
        processor_type,
        model_graph,
        model_lib,
        model_params,
        input_node,
        num_output,
    ):
        super().__init__(processor_type)
        if self.processor_type == "cpu":
            self.ctx = tvm.cpu()
        elif self.processor_type == "gpu":
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

    def config_worker(self, params):
        pass

    def preprocess_input(self, params):
        pass

    def tvm_process(self, data):
        # t1 = time.time()
        if isinstance(data, list):
            if len(data) > 0:
                results = []
                for i in range(len(data)):
                    data = data[i]
                    data = data.astype("float32")
                    self.inference_module.set_input(self.input_node, tvm.nd.array(data))
                    self.inference_module.run()
                    inference_outputs = []
                    for j in range(self.num_output):
                        inference_outputs.append(
                            self.inference_module.get_output(j).asnumpy()
                        )
                    results.append(inference_outputs)
                # print("Inference time:", time.time() - t1)
                return results
        else:
            if data is not None:
                data = data.astype("float32")
                self.inference_module.set_input(
                    self.input_node, tvm.nd.array(data.copy())
                )
                self.inference_module.run()
                inference_outputs = []
                for i in range(self.num_output):
                    inference_outputs.append(
                        self.inference_module.get_output(i).asnumpy()
                    )
                result = inference_outputs
                # print("Inference time:", time.time() - t1)
                return [result]
        return []

    def process_data(self, preprocessed_data):
        pass

    def postprocess_result(self, inference_outputs):
        pass

    def run_inference(self, params):
        postprocessed_data = []
        preprocessed_data = self.preprocess_input(params)
        if preprocessed_data is None:
            return None
        processed_data = self.process_data(preprocessed_data)
        postprocessed_data = self.postprocess_result(processed_data)
        return postprocessed_data
