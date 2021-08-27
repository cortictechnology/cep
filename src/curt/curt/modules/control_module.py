""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

from curt.base_module import BaseModule
from curt.modules.control.control_factory import ControlFactory


class ControlModule(BaseModule):
    def __init__(self):
        super().__init__("control")

    def create_factory(self):
        self.worker_factory = ControlFactory()

    def process_remote_data(self, data):
        return data
