""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

from abc import abstractmethod

class BaseVoiceProcessing:

    def __init__(self):
        pass


    @abstractmethod
    def config_module(self, params):
        pass


    @abstractmethod
    def run_inference(self, input_data):
        pass

