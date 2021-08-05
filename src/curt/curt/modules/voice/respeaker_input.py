""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, April 2021

"""

import logging
import numpy as np
import sys
import time
import threading
from collections import deque
import webrtcvad
from curt.modules.voice.mic_array import MicArray
from curt.modules.voice.base_voice_input import BaseVoiceInput
import wave
import base64

BEAM_WIDTH = 500
DEFAULT_SAMPLE_RATE = 16000


class RespeakerInput(BaseVoiceInput):

    RATE = 16000
    CHANNELS = 4
    VAD_FRAMES = 10  # ms
    DOA_FRAMES = 200  # ms
    RESPEAKER_WIDTH = 2

    def __init__(self):
        super().__init__("respaker")
        self.audio_index = -1
        self.started_recording = False
        self.vad = webrtcvad.Vad(2)
        self.speech_count = 0
        self.chunks = []
        self.speech_chunks = deque(maxlen=1024)
        self.reset_speech_chunks = False
        self.doa_chunks = int(self.DOA_FRAMES / self.VAD_FRAMES)
        self.recording_thread = threading.Thread(
            target=self.recording_thread, daemon=True
        )
        self.last_speech_chunk_time = time.monotonic()
        self.time_since_last_speech = 99999
        self.collecting_speech = False
        self.direction = -1

    def config_input_handler(self, params):
        if self.audio_index != -1:
            logging.warning("Please release the current audio input device first")
            return False
        else:
            self.audio_index = params["audio_in_index"]
            return True

    def recording_thread(self):
        try:
            print("Starting to record")
            with MicArray(
                self.RATE, self.CHANNELS, self.RATE * self.VAD_FRAMES / 1000
            ) as mic:
                for chunk in mic.read_chunks():
                    if self.started_recording:
                        # Use single channel audio to detect voice activity
                        if self.vad.is_speech(
                            chunk[0 :: self.CHANNELS].tobytes(), self.RATE
                        ):
                            self.time_since_last_speech = 0
                            self.speech_count += 1
                            self.speech_chunks.append(chunk)
                            self.last_speech_chunk_time = time.monotonic()
                        else:
                            self.time_since_last_speech = (
                                time.monotonic() - self.last_speech_chunk_time
                            )

                        self.chunks.append(chunk)
                        if len(self.chunks) == self.doa_chunks:
                            if self.speech_count > (self.doa_chunks / 2):
                                frames = np.concatenate(self.chunks)
                                self.direction = mic.get_direction(frames)
                                # print('\n{}'.format(int(direction)))

                            self.speech_count = 0
                            self.chunks = []

        except KeyboardInterrupt:
            pass

    def start_recording(self):
        if self.audio_index != -1:
            if not self.started_recording:
                self.recording_thread.start()
                self.started_recording = True
                return []
            else:
                print("already recording, pass")
                return []
        else:
            logging.warning("No audio input device is configured")
            return []

    def get_current_recording(self):
        # print("Since last time:", self.time_since_last_speech)
        speech = b""
        if (
            self.time_since_last_speech > 1
            and len(self.speech_chunks) > 0
            and self.started_recording
        ):
            # print("Silence now")
            speech = speech.join(self.speech_chunks)
            # print("Got speech bytes")
            # wf = wave.open("voice.wav", 'wb')
            # wf.setnchannels(4)
            # wf.setsampwidth(2)
            # wf.setframerate(self.RATE)
            # wf.writeframes(speech)
            # wf.close()
            self.speech_chunks.clear()
            self.direction = -1
        # else:
        # print("last silence time:", self.time_since_last_speech)
        encoded_speech = base64.b64encode(speech)
        return encoded_speech.decode("ascii")

    def get_speech_direction(self):
        return self.direction

    def pause_recording(self):
        self.started_recording = False
        self.speech_chunks.clear()
        return True

    def resume_recording(self):
        self.started_recording = True
        return True

    def release_input_handler(self):
        self.audio_index = -1
        self.stop_recording = True
        self.recording_thread.join()
