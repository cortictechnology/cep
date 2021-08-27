""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

import pyaudio
import logging
import numpy as np
from curt.modules.voice.vad_utils import Audio, VADAudio

from curt.modules.voice.base_voice_input import BaseVoiceInput

BEAM_WIDTH = 500
DEFAULT_SAMPLE_RATE = 16000

class LiveInput(BaseVoiceInput):

    def __init__(self):
        super().__init__("live")
        self.audio_index = -1
        self.started_recording = False


    def config_input_handler(self, params):
        if self.audio_index != -1:
            logging.warning("Please release the current audio input device first")
            return False
        else:
            self.audio_index = params['audio_in_index'] 
            return True


    def start_recording(self):
        if self.audio_index != -1:
            input_handler = VADAudio(self.audio_index, aggressiveness=3, input_rate=DEFAULT_SAMPLE_RATE)
            if not self.started_recording:
                frames = input_handler.vad_collector()
                print("start recording now")
                self.started_recording = True
                audio_frame_buffer = []
                for frame in frames:
                    if frame is not None:
                        audio_frame_buffer.append(np.frombuffer(frame, np.int16))
                    else:
                        print("end recording")
                        input_handler.destroy()
                        self.started_recording = False
                        return audio_frame_buffer
            else:
                print("already recording, pass")
                pass
        else:
            logging.warning("No audio input device is configured")
            return []

    
    def release_input_handler(self):
        self.audio_index = -1


