""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, October 2020

"""

import cv2
import logging
import time
from curt.modules.vision.base_vision_input import BaseVisionInput


class ImageInput(BaseVisionInput):
    def __init__(self):
        super().__init__("image_input")
        self.image_source = None

    def config_input_handler(self, params):
        self.image_source = params["image_source"]

    def capture_image(self):
        img = None
        if self.image_source is not None:
            img = cv2.imread(self.image_source)
        else:
            logging.warning("Please configure the image source first")

        return img

    def release_input_handler(self):
        if self.image_source is not None:
            self.image_source = None
        else:
            logging.warning("Please configure the image source first")
