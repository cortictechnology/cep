""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, October 2020

"""

import traceback
import logging

from curt.base_service import BaseService

class ControlService(BaseService):

    def __init__(self):
        super().__init__()
        self.service_type = "Control"


    def execute_function(self, worker, data):
        config_hardware = data[-1]
        try:
            if config_hardware:
                return worker.config_control_handler(data[0])
            else:
                return worker.command(data[0])
        except Exception as e:
            logging.error(traceback.format_exc())