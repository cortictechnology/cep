""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, August 2020

"""

import traceback
import logging

from curt.base_service import BaseService


class VisionRenderService(BaseService):
    def __init__(self):
        super().__init__("VisionRender")

    def execute_function(self, worker, data):
        config_module = data[-1]
        try:
            if config_module:
                return worker.config_module(data[0])
            else:
                result = worker.render(data[0])
                return result
        except Exception as e:
            logging.error(traceback.format_exc())
