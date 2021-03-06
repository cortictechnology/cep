""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

import pyaudio
import logging
import numpy as np
import subprocess
import os

from curt.modules.voice.base_voice_generation import BaseVoiceGeneration


class OfflineVoiceGeneration(BaseVoiceGeneration):
    def __init__(self):
        super().__init__()
        self.voice = (
            "/models/cmu_us_rms.flitevox"
        )
        self.duration_stretch = 1.0

    def config_module(self, params):
        self.voice = params["voice"]
        self.duration_stretch = params["duration_stretch"]

    def start_playing(self, input_data):
        logging.warning("Offline voice generation, data: " + input_data)
        if input_data == "notification_tone":
            tone = (
                "/models/siri.wav"
            )
            os.system("mplayer " + tone)
        else:
            os.system('mimic -t "' + input_data + '" -voice ' + self.voice)

    def stop_playing(self):
        pass

    def release_output_handler(self):
        pass
