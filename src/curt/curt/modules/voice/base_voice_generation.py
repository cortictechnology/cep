""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, August 2020

"""

from abc import abstractmethod

class BaseVoiceGeneration:

    def __init__(self):
        self.output_handler = None
        self.started_playing = False


    @abstractmethod
    def config_module(self, params):
        pass


    @abstractmethod
    def start_playing(self):
        pass


    @abstractmethod
    def stop_playing(self):
        pass


    @abstractmethod
    def release_output_handler(self):
        pass
