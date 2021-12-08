""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Michael Ng <michaelng@cortic.ca>, March 2020

Code based on https://github.com/mozilla/DeepSpeech-examples/blob/r0.8/mic_vad_streaming/mic_vad_streaming.py
"""

import pyaudio
import wave
import webrtcvad
from halo import Halo
from scipy import signal
from datetime import datetime
import threading, collections, queue, os, os.path
import numpy as np
from six.moves import queue
import time, logging


class Audio(object):
    """Streams raw audio from microphone. Data is received in a separate thread, and stored in a buffer, to be read from."""

    FORMAT = pyaudio.paInt16
    # Network/VAD rate-space
    RATE_PROCESS = 16000

    def __init__(
        self,
        mic_index,
        callback=None,
        device=None,
        input_rate=RATE_PROCESS,
        file=None,
        blocks_per_second=50,
        channels=1,
    ):
        def proxy_callback(in_data, frame_count, time_info, status):
            # pylint: disable=unused-argument
            if self.chunk is not None:
                in_data = self.wf.readframes(self.chunk)
            callback(in_data)
            return (None, pyaudio.paContinue)

        if callback is None:
            callback = lambda in_data: self.buffer_queue.put(in_data)
        self.buffer_queue = queue.Queue()
        self.device = device
        self.input_rate = input_rate
        self.sample_rate = self.RATE_PROCESS
        self.block_size = int(self.RATE_PROCESS / float(blocks_per_second))
        self.block_size_input = int(self.input_rate / float(blocks_per_second))
        self.mic_index = mic_index
        self.pa = pyaudio.PyAudio()

        kwargs = {
            "format": self.FORMAT,
            "channels": channels,
            "rate": self.input_rate,
            "input": True,
            "frames_per_buffer": self.block_size_input,
            "stream_callback": proxy_callback,
            "input_device_index": self.mic_index,
        }

        self.chunk = None
        # if not default device
        if self.device:
            kwargs["input_device_index"] = self.device
        elif file is not None:
            self.chunk = 320
            self.wf = wave.open(file, "rb")

        self.stream = self.pa.open(**kwargs)
        self.stream.start_stream()

    def resample(self, data, input_rate):
        """
        Microphone may not support our native processing sampling rate, so
        resample from input_rate to RATE_PROCESS here for webrtcvad and
        deepspeech
        Args:
            data (binary): Input audio stream
            input_rate (int): Input audio rate to resample from
        """
        data16 = np.fromstring(string=data, dtype=np.int16)
        resample_size = int(len(data16) / self.input_rate * self.RATE_PROCESS)
        resample = signal.resample(data16, resample_size)
        resample16 = np.array(resample, dtype=np.int16)
        return resample16.tostring()

    def read_resampled(self):
        """Return a block of audio data resampled to 16000hz, blocking if necessary."""
        return self.resample(data=self.buffer_queue.get(), input_rate=self.input_rate)

    def read(self):
        """Return a block of audio data, blocking if necessary."""
        return self.buffer_queue.get()

    def destroy(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()

    frame_duration_ms = property(
        lambda self: 1000 * self.block_size // self.sample_rate
    )

    def write_wav(self, filename, data):
        logging.info("write wav %s", filename)
        wf = wave.open(filename, "wb")
        wf.setnchannels(self.CHANNELS)
        # wf.setsampwidth(self.pa.get_sample_size(FORMAT))
        assert self.FORMAT == pyaudio.paInt16
        wf.setsampwidth(2)
        wf.setframerate(self.sample_rate)
        wf.writeframes(data)
        wf.close()


class VADAudio(Audio):
    """Filter & segment audio with voice activity detection."""

    def __init__(
        self,
        mic_index,
        aggressiveness=3,
        device=None,
        input_rate=None,
        file=None,
        blocks_per_second=50,
        channels=1,
    ):
        super().__init__(
            mic_index,
            device=device,
            input_rate=input_rate,
            file=file,
            blocks_per_second=blocks_per_second,
            channels=channels,
        )
        self.vad = webrtcvad.Vad(aggressiveness)
        self.channels = channels

    def frame_generator(self):
        """Generator that yields all audio frames from microphone."""
        if self.input_rate == self.RATE_PROCESS:
            while True:
                yield self.read()
        else:
            while True:
                yield self.read_resampled()

    def vad_collector(self, padding_ms=300, ratio=0.75, frames=None):
        """Generator that yields series of consecutive audio frames comprising each utterence, separated by yielding a single None.
        Determines voice activity by ratio of frames in padding_ms. Uses a buffer to include padding_ms prior to being triggered.
        Example: (frame, ..., frame, None, frame, ..., frame, None, ...)
                  |---utterence---|        |---utterence---|
        """
        if frames is None:
            frames = self.frame_generator()
        num_padding_frames = padding_ms // self.frame_duration_ms
        ring_buffer = collections.deque(maxlen=num_padding_frames)
        triggered = False

        for frame in frames:
            if len(frame) < 640:
                return
            is_speech = False
            if self.channels > 1:
                frame = np.fromstring(frame, dtype="int16")
                is_speech = self.vad.is_speech(
                    frame[0 :: self.channels].tobytes(), self.sample_rate
                )
            else:
                is_speech = self.vad.is_speech(frame, self.sample_rate)

            if not triggered:
                ring_buffer.append((frame, is_speech))
                num_voiced = len([f for f, speech in ring_buffer if speech])
                if num_voiced > ratio * ring_buffer.maxlen:
                    triggered = True
                    for f, s in ring_buffer:
                        yield f
                    ring_buffer.clear()

            else:
                yield frame
                ring_buffer.append((frame, is_speech))
                num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                if num_unvoiced > ratio * ring_buffer.maxlen:
                    triggered = False
                    yield None
                    ring_buffer.clear()
