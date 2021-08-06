""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

from abc import abstractmethod

class BaseIntentClassifier:

    def __init__(self):
        self.nlu_model = None


    @abstractmethod
    def config_module(self, params):
        pass


    @abstractmethod
    def classify_intent(self, input_data):
        pass

