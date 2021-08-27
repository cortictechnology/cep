""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

import traceback
import logging

from curt.base_service import BaseService

class NLPService(BaseService):

    def __init__(self):
        super().__init__()
        self.service_type = "NLP"


    def execute_function(self, worker, data):
        config_module = data[-1]
        try:
            if config_module:
                return worker.config_module(data[0])
            else:
                return worker.run_inference(data[0])
        except Exception as e:
            logging.error(traceback.format_exc())