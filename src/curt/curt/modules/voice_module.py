""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

from curt.base_module import BaseModule
from curt.modules.voice.voice_factory import VoiceFactory


class VoiceModule(BaseModule):
    def __init__(self):
        super().__init__("voice")

    def create_factory(self):
        self.worker_factory = VoiceFactory()

    def process_remote_data(self, data):
        return data
