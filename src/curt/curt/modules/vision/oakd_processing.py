""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, March 2021

"""

from curt.modules.vision.base_vision_processing import BaseVisionProcessing

class OAKDProcessingWorker(BaseVisionProcessing):
    def __init__(self):
        self.oakd_pipeline = None
        self.friendly_name = ""

    def config_worker(self, params):
        pass

    def preprocess_input(self, params):
        pass

    def execute_nn_operation(self, preprocessed_data):
        pass

    def postprocess_result(self, inference_result):
        pass

    def run_inference(self, params):
        preprocessed_data = self.preprocess_input(params)
        if preprocessed_data is None:
            return None
        inference_result = self.execute_nn_operation(preprocessed_data)
        postprocessed_data = self.postprocess_result(inference_result)
        return postprocessed_data
