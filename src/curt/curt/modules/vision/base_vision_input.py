""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""


from abc import abstractmethod


class BaseVisionInput:
    def __init__(self, source_type):
        self.source_type = source_type
        self.input_width = None
        self.input_height = None
        self.input_handler = None
        self.friendly_name = ""

    @abstractmethod
    def config_input_handler(self, params):
        pass

    @abstractmethod
    def capture_image(self, gray=False):
        pass

    @abstractmethod
    def release_input_handler(self):
        pass
