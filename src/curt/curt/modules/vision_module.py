""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, August 2020

"""

from curt.base_module import BaseModule
from curt.modules.vision.vision_factory import VisionFactory
from curt.modules.vision.utils import decode_image_byte


class VisionModule(BaseModule):
    def __init__(self):
        super().__init__("vision")
        self.enable_streaming = True

    def create_factory(self):
        self.worker_factory = VisionFactory()

    def process_remote_data(self, data):
        if isinstance(data, str):
            return decode_image_byte(data)
        else:
            return data

    def process_local_data(self, data):
        if isinstance(data, str):
            return decode_image_byte(data)
        else:
            return data
