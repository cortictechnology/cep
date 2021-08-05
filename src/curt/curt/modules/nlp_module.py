""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, August 2020

"""

from curt.base_module import BaseModule
from curt.modules.nlp.nlp_factory import NLPFactory


class NLPModule(BaseModule):
    def __init__(self):
        super().__init__("nlp")

    def create_factory(self):
        self.worker_factory = NLPFactory()

    def processRemoteData(self, data):
        return data
