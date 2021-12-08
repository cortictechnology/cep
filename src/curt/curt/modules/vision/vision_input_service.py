""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

import traceback
import logging

from curt.base_service import BaseService

class VisionInputService(BaseService):
    def __init__(self):
        super().__init__("VisionInput")

    def execute_function(self, worker, data):
        config_hardware = data[-1]
        try:
            if config_hardware:
                return worker.config_input_handler(data[0])
            else:
                if isinstance(data[0], list):
                    return worker.capture_image(data[0])
                elif isinstance(data[0], dict):
                    data_list = []
                    for param in data[0]["ready_data"]:
                        data_list.append(param)
                    for guid in data[0].keys():
                        if guid != "ready_data":
                            data_list.append(data[0][guid])
                    return worker.capture_image(data_list)
        except Exception as e:
            logging.error(traceback.format_exc())
