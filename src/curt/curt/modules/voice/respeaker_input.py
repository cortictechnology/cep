""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

import logging
import numpy as np
import sys
import time
import threading
from collections import deque

# import webrtcvad
# from curt.modules.voice.mic_array import MicArray
from curt.modules.voice.vad_utils import Audio, VADAudio
from curt.modules.voice.base_voice_input import BaseVoiceInput
import wave
import base64

DEFAULT_SAMPLE_RATE = 16000


class RespeakerInput(BaseVoiceInput):
    def __init__(self):
        super().__init__("respeaker")
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
                self.audio_index,
                aggressiveness=3,
                input_rate=DEFAULT_SAMPLE_RATE,
                blocks_per_second=100,
                channels=4,
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
        self.speech_chunks.clear()
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

    # RATE = 16000
    # CHANNELS = 4
    # VAD_FRAMES = 10  # ms
    # DOA_FRAMES = 200  # ms
    # RESPEAKER_WIDTH = 2

    # def __init__(self):
    #     super().__init__("respaker")
    #     self.audio_index = -1
    #     self.started_recording = False
    #     self.stop_recording = False
    #     self.vad = webrtcvad.Vad(2)
    #     self.speech_count = 0
    #     self.chunks = []
    #     self.speech_chunks = deque(maxlen=1024)
    #     self.reset_speech_chunks = False
    #     self.doa_chunks = int(self.DOA_FRAMES / self.VAD_FRAMES)
    #     self.recording_thread_started = False
    #     self.no_microphone = False
    #     self.last_speech_chunk_time = time.monotonic()
    #     self.time_since_last_speech = 99999
    #     self.collecting_speech = False
    #     self.direction = -1

    # def config_input_handler(self, params):
    #     if self.no_microphone:
    #         logging.warning("No microphone attached")
    #         return False
    #     else:
    #         self.audio_index = params["audio_in_index"]
    #         return True

    # def recording_func(self):
    #     logging.warning("Starting to record")
    #     try:
    #         logging.warning("Creating MicArray")
    #         with MicArray(
    #             self.RATE, self.CHANNELS, -1, self.RATE * self.VAD_FRAMES / 1000
    #         ) as mic:
    #             for chunk in mic.read_chunks():
    #                 if self.stop_recording:
    #                     break
    #                 if self.started_recording:
    #                     # Use single channel audio to detect voice activity
    #                     if self.vad.is_speech(
    #                         chunk[0 :: self.CHANNELS].tobytes(), self.RATE
    #                     ):
    #                         self.time_since_last_speech = 0
    #                         self.speech_count += 1
    #                         self.speech_chunks.append(chunk)
    #                         self.last_speech_chunk_time = time.monotonic()
    #                     else:
    #                         self.time_since_last_speech = (
    #                             time.monotonic() - self.last_speech_chunk_time
    #                         )

    #                     self.chunks.append(chunk)
    #                     if len(self.chunks) == self.doa_chunks:
    #                         if self.speech_count > (self.doa_chunks / 2):
    #                             frames = np.concatenate(self.chunks)
    #                             self.direction = mic.get_direction(frames)
    #                             # print('\n{}'.format(int(direction)))

    #                         self.speech_count = 0
    #                         self.chunks = []
    #             mic.stop()
    #         logging.warning("recording thread quiting")
    #     except:
    #         logging.warning("Recording thread exception occurred")
    #         self.no_microphone = True
    #         self.audio_index = -1
    #         self.started_recording = False
    #         self.speech_chunks.clear()

    # def start_recording(self):
    #     logging.warning("Call start recording function")
    #     if self.audio_index != -1:
    #         if not self.started_recording:
    #             self.recording_thread = threading.Thread(
    #                 target=self.recording_func, daemon=True
    #             )
    #             logging.warning("Starting record in thread")
    #             self.recording_thread.start()
    #             self.started_recording = True
    #             return []
    #         else:
    #             print("already recording, pass")
    #             return []
    #     else:
    #         logging.warning("No audio input device is configured")
    #         return []

    # def get_current_recording(self):
    #     # print("Since last time:", self.time_since_last_speech)
    #     speech = b""
    #     if (
    #         self.time_since_last_speech > 1
    #         and len(self.speech_chunks) > 0
    #         and self.started_recording
    #     ):
    #         # print("Silence now")
    #         speech = speech.join(self.speech_chunks)
    #         self.speech_chunks.clear()
    #         self.direction = -1
    #     encoded_speech = base64.b64encode(speech)
    #     return encoded_speech.decode("ascii")

    # def get_speech_direction(self):
    #     return self.direction

    # def pause_recording(self):
    #     self.started_recording = False
    #     self.speech_chunks.clear()
    #     return True

    # def resume_recording(self):
    #     self.started_recording = True
    #     return True

    # def release_input_handler(self):
    #     logging.warning("Releasing recording handler")
    #     self.started_recording = False
    #     self.audio_index = -1
    #     self.stop_recording = True
    #     logging.warning("Waiting for recording thread to stop")
    #     self.recording_thread.join()
    #     logging.warning("Clearing speed chunks")
    #     self.speech_chunks.clear()
    #     self.stop_recording = False
    #     logging.warning("Recording handler released")
    #     return True
