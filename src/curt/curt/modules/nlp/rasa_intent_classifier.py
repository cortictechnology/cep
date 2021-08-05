""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, October 2020

"""

from rasa.nlu.model import Metadata, Interpreter
import json
import time
import logging
import os
import threading
from rasa.nlu.model import Metadata, Interpreter
from curt.modules.nlp.base_intent_classifier import BaseIntentClassifier


class RasaIntentClassifier(BaseIntentClassifier):
    def __init__(self):
        super().__init__()
        self.nlu_model = None
        self.interpreter = None

    def config_module(self, params):
        nlu_model = params["model"]
        if self.nlu_model != nlu_model:
            self.nlu_model = params["model"]
            logging.warning("Loading " + str(self.nlu_model))
            self.interpreter = Interpreter.load("/models/" + self.nlu_model)
            logging.warning("Done loading model")
        return True

    def classify_intent(self, input_data):
        logging.warning("Analyzing: " + str(input_data[0]))
        intent = self.interpreter.parse(input_data[0])
        intent_data = {
            "topic": intent["intent"]["name"],
            "confidence": intent["intent"]["confidence"],
            "entities": intent["entities"],
        }
        intent_data = json.dumps(intent_data)
        return intent_data
