""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, October 2020

"""

from abc import abstractmethod

class BaseResponseGenerator:

    def __init__(self):
        self.story_model = None


    @abstractmethod
    def config_module(self, params):
        pass


    @abstractmethod
    def run_inference(self, input_data):
        pass

