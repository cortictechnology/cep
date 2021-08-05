""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, November 2020

"""

import pyaudio
import logging
import numpy as np
from curt.modules.voice.vad_utils import Audio, VADAudio

from curt.modules.voice.base_voice_input import BaseVoiceInput

BEAM_WIDTH = 500
DEFAULT_SAMPLE_RATE = 16000

class RecordedInput(BaseVoiceInput):

    def __init__(self):
        super().__init__("recorded")


    def config_input_handler(self, params):
        pass


    def start_recording(self):
        pass

    
    def stop_recording(self):
        pass

    
    def release_input_handler(self):
        pass


