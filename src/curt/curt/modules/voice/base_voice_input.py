""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, August 2020

"""

from abc import abstractmethod

class BaseVoiceInput:

    def __init__(self, source_type):
        self.source_type = source_type
        self.input_handler = None
        self.started_recording = False


    @abstractmethod
    def config_input_handler(self, params):
        pass


    @abstractmethod
    def start_recording(self):
        pass


    @abstractmethod
    def stop_recording(self):
        pass


    @abstractmethod
    def release_input_handler(self):
        pass
