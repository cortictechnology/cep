""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, June 2021

"""


from curt.modules.vision.utils import *
from curt.modules.vision.utils import decode_image_byte
import numpy as np
import logging
import os
import time
import collections


class HeartrateMeasure:
    def __init__(self):
        self.fps = 0
        self.buffer_size = 250
        self.essential_frame_accumulated = 30
        self.data_buffer_a = collections.deque(maxlen=self.buffer_size)
        self.data_buffer_b = collections.deque(maxlen=self.buffer_size)
        self.current_buffer = "a"
        self.times_a = collections.deque(maxlen=self.buffer_size)
        self.times_b = collections.deque(maxlen=self.buffer_size)

        self.freqs = []
        self.fft = []
        self.t0 = time.time()
        self.bpms = circularlist(self.essential_frame_accumulated)
        self.bpm = 0
        self.pixel_threshold = 1.5

        self.face_rect = None

    def config_module(self, data):
        if data[0] == "pixel_threshold":
            self.pixel = data[1]

    def get_subface_coord(self, fh_x, fh_y, fh_w, fh_h):
        x, y, w, h = self.face_rect
        return [
            int(x + w * fh_x - (w * fh_w / 2.0)),
            int(y + h * fh_y - (h * fh_h / 2.0)),
            int(w * fh_w),
            int(h * fh_h),
        ]

    def get_subface_means(self, frame, coord):
        x, y, w, h = coord
        subframe = frame[y : y + h, x : x + w, :]
        v1 = np.mean(subframe[:, :, 0])
        v2 = np.mean(subframe[:, :, 1])
        v3 = np.mean(subframe[:, :, 2])
        return v1, v2, v3
        # return (v1 + v2 + v3) / 3.0

    def select_storing_buffer(self, current_value, threshold):
        selected_buffer = None
        selected_times = None
        if self.current_buffer == "a":
            selected_buffer = self.data_buffer_a
            selected_times = self.times_a
        else:
            selected_buffer = self.data_buffer_b
            selected_times = self.times_b

        if len(selected_buffer) > 0:
            diff = abs(current_value - selected_buffer[-1])
            if diff > threshold:
                print(
                    "Change exceeds pixel threshold, may need to switch to new data buffer"
                )
                if self.current_buffer == "a":
                    if len(self.data_buffer_a) < self.buffer_size:
                        # No need to switch buffer, just need to clear existing data of current buffer
                        self.data_buffer_a = collections.deque(maxlen=self.buffer_size)
                        self.times_a = collections.deque(maxlen=self.buffer_size)
                        selected_buffer = self.data_buffer_a
                        selected_times = self.times_a
                    else:
                        # Switch to another buffer to preserve the current steady signal
                        self.current_buffer = "b"
                        self.data_buffer_b = collections.deque(maxlen=self.buffer_size)
                        self.times_b = collections.deque(maxlen=self.buffer_size)
                        selected_buffer = self.data_buffer_b
                        selected_times = self.times_b

                else:
                    if len(self.data_buffer_b) < self.buffer_size:
                        # No need to switch buffer, just need to clear existing data of current buffer
                        self.data_buffer_b = collections.deque(maxlen=self.buffer_size)
                        self.times_b = collections.deque(maxlen=self.buffer_size)
                        selected_buffer = self.data_buffer_b
                        selected_times = self.times_b
                    else:
                        # Switch to another buffer to preserve the current steady signal
                        self.current_buffer = "a"
                        self.data_buffer_a = collections.deque(maxlen=self.buffer_size)
                        self.times_a = collections.deque(maxlen=self.buffer_size)
                        selected_buffer = self.data_buffer_a
                        selected_times = self.times_a
        return selected_buffer, selected_times

    def update_storing_buffer(self, buffer, times):
        if self.current_buffer == "a":
            self.data_buffer_a = buffer
            self.times_a = times
        else:
            self.data_buffer_b = buffer
            self.times_b = times

    def calculate_bpm(self, buffer, times):
        processed = np.array(buffer)
        bpm = 0
        L = len(buffer)
        if L > self.essential_frame_accumulated:
            fps = float(L) / (times[-1] - times[0])
            even_times = np.linspace(times[0], times[-1], L)
            interpolated = np.interp(even_times, times, processed)
            interpolated = np.hamming(L) * interpolated
            interpolated = interpolated - np.mean(interpolated)
            raw = np.fft.rfft(interpolated)
            phase = np.angle(raw)
            fft = np.abs(raw)
            freqs = float(fps) / L * np.arange(L / 2 + 1)
            freqs = 60.0 * freqs
            idx = np.where((freqs > 50) & (freqs < 240))
            pruned = fft[idx]
            phase = phase[idx]

            pfreq = freqs[idx]
            freqs = pfreq
            fft = pruned
            idx2 = np.argmax(pruned)

            gap = (self.buffer_size - L) / fps
            if gap:
                bpm = 0
            else:
                bpm = freqs[idx2]
        return bpm

    def run_inference(self, data):
        img, bbox = data
        if isinstance(img, str):
            img = decode_image_byte(img)
        forehead_x = 0.5
        y_start = 0.2
        width = 0.3
        height = 0.15
        if len(bbox) > 0:
            bbox = bbox[0]
            self.face_rect = [
                bbox[0],
                bbox[1],
                bbox[2] - bbox[0],
                bbox[3] - bbox[1],
            ]
        if self.face_rect is None:
            # BPM is set to 0 if not face is present
            return 0

        forehead1 = self.get_subface_coord(forehead_x, y_start, width, height)
        _, v2, v3 = self.get_subface_means(img, forehead1)

        selected_buffer, selected_times = self.select_storing_buffer(
            v2, self.pixel_threshold
        )

        selected_buffer.append(v2)
        selected_times.append(time.time() - self.t0)

        # Update the data buffer with latest measurement
        self.update_storing_buffer(selected_buffer, selected_times)

        other_bpm = 0
        other_data_length = 0

        # If there is already a steady signal stored in another data buffer, obtain its bpm value for later use.
        if self.current_buffer == "a":
            other_bpm = self.calculate_bpm(self.data_buffer_b, self.times_b)
            other_data_length = len(self.data_buffer_b)
        else:
            other_bpm = self.calculate_bpm(self.data_buffer_a, self.times_a)
            other_data_length = len(self.data_buffer_a)

        total_data_length = other_data_length + len(selected_buffer)

        processed = np.array(selected_buffer)

        L = len(selected_buffer)
        # Start heartrate estimation only if there are enough measurements stored in the data buffer
        if L > self.essential_frame_accumulated:
            self.fps = float(L) / (selected_times[-1] - selected_times[0])
            even_times = np.linspace(selected_times[0], selected_times[-1], L)
            interpolated = np.interp(even_times, selected_times, processed)
            interpolated = np.hamming(L) * interpolated
            interpolated = interpolated - np.mean(interpolated)
            raw = np.fft.rfft(interpolated)
            phase = np.angle(raw)
            self.fft = np.abs(raw)
            self.freqs = float(self.fps) / L * np.arange(L / 2 + 1)
            freqs = 60.0 * self.freqs
            idx = np.where((freqs > 50) & (freqs < 220))
            pruned = self.fft[idx]
            phase = phase[idx]

            pfreq = freqs[idx]
            self.freqs = pfreq
            self.fft = pruned
            idx2 = np.argmax(pruned)

            t = (np.sin(phase[idx2]) + 1.0) / 2.0
            t = 0.9 * t + 0.1
            self.alpha = t

            gap = (self.buffer_size - L) / self.fps

            # If the selected data buffer is not completely filled, we don't consider it a steady signal.
            if gap:
                # Since the signal is not considered steady, we use a steady signal from the other data buffer to
                # perform weighting on the final result
                this_bpm = self.freqs[idx2]
                other_portion = (other_data_length / total_data_length) * other_bpm
                this_portion = (len(selected_buffer) / total_data_length) * this_bpm
                self.bpm = other_portion + this_portion
                self.bpms.append(self.bpm)
                if other_bpm == 0:
                    # If there isn't a steady signal in the other data buffer, we don't return the current value.
                    return 0
                else:
                    # If a weighted value is obtained, we return the moving average of the value.
                    return self.bpms.calc_average()
            else:
                self.bpm = self.freqs[idx2]
                self.bpms.append(self.bpm)
                return self.bpms.calc_average()
        else:
            if other_data_length >= self.buffer_size:
                return self.bpms.calc_average()
            else:
                return 0
