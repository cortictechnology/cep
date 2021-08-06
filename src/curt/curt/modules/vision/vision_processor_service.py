""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

# need to advertise different processor type, eg CPU, GPU, TPU
import traceback
import logging

from curt.base_service import BaseService


class VisionProcessorService(BaseService):
    def __init__(self):
        super().__init__("VisionProcessor")

    def execute_function(self, worker, data):
        config_module = data[-1]
        try:
            if config_module:
                return worker.config_module(data[0])
            else:
                if isinstance(data[0], list):
                    return worker.run_inference(data[0])
                elif isinstance(data[0], dict):
                    data_list = []
                    for param in data[0]["ready_data"]:
                        data_list.append(param)
                    for guid in data[0].keys():
                        if guid != "ready_data":
                            data_list.append(data[0][guid])
                    return worker.run_inference(data_list)
        except Exception as e:
            logging.error(traceback.format_exc())
