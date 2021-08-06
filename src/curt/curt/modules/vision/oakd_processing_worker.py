""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

from abc import abstractmethod


class OAKDProcessingWorker:
    def __init__(self):
        self.oakd_pipeline = None
        self.friendly_name = ""

    def config_pipeline(self, params):
        pass

    @abstractmethod
    def preprocessing(self, params):
        pass

    @abstractmethod
    def execute_nn_operation(self, preprocessed_data):
        pass

    @abstractmethod
    def postprocessing(self, inference_result):
        pass

    def run_inference(self, params):
        preprocessed_data = self.preprocessing(params)
        if preprocessed_data is None:
            return None
        inference_result = self.execute_nn_operation(preprocessed_data)
        postprocessed_data = self.postprocessing(inference_result)
        return postprocessed_data
