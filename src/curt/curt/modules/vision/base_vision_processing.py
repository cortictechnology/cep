""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, October 2020

"""

from abc import abstractmethod

class BaseVisionProcessing:
    def __init__(self, processor_type):
        self.processor_type = processor_type

    @abstractmethod
    def config_worker(self, params):
        pass

    @abstractmethod
    def preprocess_input(self, input_data):
        pass

    @abstractmethod
    def run_inference(self, params):
        pass

    @abstractmethod
    def postprocess_result(self, inference_outputs):
        pass
    