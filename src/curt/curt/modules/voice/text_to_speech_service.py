""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, November 2020

"""

import traceback
import logging

from curt.base_service import BaseService


class TextToSpeechService(BaseService):
    def __init__(self):
        super().__init__()
        self.service_type = "TextToSpeech"

    def execute_function(self, worker, data):
        config_hardware = data[-1]
        print("service raw data:", data)
        try:
            if config_hardware:
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
                    return worker.start_playing(data_list[0])
        except Exception as e:
            logging.error(traceback.format_exc())
