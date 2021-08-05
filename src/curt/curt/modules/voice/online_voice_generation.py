""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, May 2021

"""

import logging
import numpy as np
from gtts import gTTS
import pygame
from io import BytesIO
import os

from curt.modules.voice.base_voice_generation import BaseVoiceGeneration


class OnlineVoiceGeneration(BaseVoiceGeneration):
    def __init__(self):
        super().__init__()
        pygame.mixer.init()
        self.language = "en"
        self.accents = "ca"

    def config_module(self, params):
        self.language = params["language"]
        self.accents = params["accents"]
        print("Config language and accents finished")

    def start_playing(self, input_data):
        print("Online voice generation, data:", input_data)
        if input_data != "" and input_data is not None:
            print("Text input:", input_data)
            if input_data == "notification_tone":
                tone = (
                    os.path.dirname(os.path.realpath(__file__))
                    + "/../../../models/modules/voice/siri.wav"
                )
                os.system("mplayer " + tone)
            else:
                if self.accents != "":
                    tts = gTTS(text=input_data, lang=self.language, tld=self.accents)
                else:
                    tts = gTTS(text=input_data, lang=self.language)
                fp = BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                pygame.mixer.music.load(fp)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
        print("Done playing")
        return True

    def stop_playing(self):
        pass

    def release_output_handler(self):
        pass
