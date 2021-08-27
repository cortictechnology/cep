""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

import traceback
import logging

from curt.base_service import BaseService


class VoiceInputService(BaseService):
    def __init__(self):
        BaseService.__init__(self)
        self.service_type = "VoiceInput"

    def execute_function(self, worker, data):
        config_hardware = data[-1]
        try:
            if config_hardware:
                return worker.config_input_handler(data[0])
            else:
                processing_data = data[0]["ready_data"]
                if processing_data[0] == "start":
                    return worker.start_recording()
                elif processing_data[0] == "get":
                    return worker.get_current_recording()
                elif processing_data[0] == "direction":
                    return worker.get_speech_direction()
                elif processing_data[0] == "pause":
                    return worker.pause_recording()
                elif processing_data[0] == "resume":
                    return worker.resume_recording()
        except Exception as e:
            logging.error(traceback.format_exc())
