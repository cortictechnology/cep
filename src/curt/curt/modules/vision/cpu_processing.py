""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

from curt.modules.vision.base_vision_processing import BaseVisionProcessing

class CPUProcessing(BaseVisionProcessing):
    def __init__(self):
        super().__init__("cpu")

    def config_worker(self, params):
        pass

    def preprocess_input(self, input_data):
        pass

    def process_data(self, data):
        pass

    def postprocess_result(self, processed_data):
        pass

    def run_inference(self, params):
        preprocessed_data = self.preprocess_input(params)
        if preprocessed_data is None:
            return None
        processed_data = self.process_data(preprocessed_data)
        postprocessed_data = self.postprocess_result(processed_data)
        return postprocessed_data