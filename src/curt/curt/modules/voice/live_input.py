""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

import pyaudio
import logging
import numpy as np
import threading
import base64
from collections import deque
from curt.modules.voice.vad_utils import Audio, VADAudio

from curt.modules.voice.base_voice_input import BaseVoiceInput

DEFAULT_SAMPLE_RATE = 16000


class LiveInput(BaseVoiceInput):
    def __init__(self):
        super().__init__("live")
        self.audio_index = -1
        self.started_recording = False
        self.no_microphone = False
        self.input_handler = None
        self.stop_recording = False

    def config_input_handler(self, params):
        if self.audio_index != -1:
            logging.warning("Please release the current audio input device first")
            return False
        elif self.no_microphone:
            logging.warning("No microphone attached")
            return False
        else:
            self.audio_index = params["audio_in_index"]
            logging.warning("Creating VADAudio")
            self.input_handler = VADAudio(
                self.audio_index, aggressiveness=3, input_rate=DEFAULT_SAMPLE_RATE
            )
            return True

    def get_current_recording(self):
        logging.warning("Call get recording function")
        if self.audio_index != -1:
            if not self.started_recording:
                self.started_recording = True
                speech_chunks = []
                frames = self.input_handler.vad_collector()
                logging.warning("Recording now")
                for frame in frames:
                    if frame is not None:
                        speech_chunks.append(np.frombuffer(frame, np.int16))
                    else:
                        logging.warning("Recording ended")
                        # self.input_handler.destroy()
                        self.started_recording = False
                        speech = b""
                        speech = speech.join(speech_chunks)
                        encoded_speech = base64.b64encode(speech)
                        return encoded_speech.decode("ascii")
                return b""
            else:
                print("already recording, pass")
                return b""
        else:
            logging.warning("No audio input device is configured")
            return b""

    def pause_recording(self):
        self.started_recording = False
        return True

    def release_input_handler(self):
        logging.warning("Releasing recording handler")
        self.started_recording = False
        self.audio_index = -1
        if self.input_handler is not None:
            self.input_handler.destroy()
            self.input_handler = None
        logging.warning("Recording handler released")
        return True
