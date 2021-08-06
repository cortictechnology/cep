""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, August 2020

"""

from curt.base_module import BaseModule
from curt.modules.smarthome.smarthome_factory import SmartHomeFactory


class SmartHomeModule(BaseModule):
    def __init__(self):
        super().__init__("smarthome")

    def create_factory(self):
        self.worker_factory = SmartHomeFactory()

    def process_remote_data(self, data):
        return data

