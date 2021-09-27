""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""


import time
import logging
import faulthandler
import math

from curt.modules.vision.utils import decode_image_byte


class BaseRender:
    def __init__(self):
        self.drawing_modes = []
        self.window_ids = []
        self.window_properties = {}
        self.video_frame = {}
        self.container_size = [0, 0]
        self.friendly_name = ""

    def config_module(self, data):
        render_windows = data["windows"]
        for window in render_windows:
            window_id = window
            window_top_left = render_windows[window]["top_left"]
            window_size = render_windows[window]["size"]
            self.window_properties[window_id] = {}
            self.window_properties[window_id]["top_left"] = window_top_left
            self.window_properties[window_id]["size"] = window_size
            self.video_frame[window_id] = False
            new_width = window_top_left[0] + window_size[0]
            if new_width > self.container_size[0]:
                self.container_size[0] = new_width
            new_height = window_top_left[1] + window_size[1]
            if new_height > self.container_size[1]:
                self.container_size[1] = new_height

        drawing_modes = data["modes"]
        for mode in drawing_modes:
            self.drawing_modes.append(mode)
            self.window_ids.append(drawing_modes[mode])
        return True

    def render(self, data):
        faulthandler.enable()
        success = True
        for k in self.video_frame.keys():
            self.video_frame[k] = False

        # for window_name in data:
        #     for i in range(len(self.window_ids)):
        #         if window_name in self.window_ids[i]:
        #             mode = self.drawing_modes[i]
        #             drawing_func = getattr(self, mode)
        #             print("Drawing", mode, " on", window_name)
        #             success = drawing_func(data[window_name], window_name)
        #logging.warning(str(data))
        for i in range(len(self.drawing_modes)):
            mode = self.drawing_modes[i]
            drawing_func = getattr(self, mode)
            for window in self.window_ids[i]:
                drawing_data = data[window]
                if "camera_input" in drawing_data:
                    if isinstance(drawing_data["camera_input"], str):
                        drawing_data["camera_input"] = decode_image_byte(
                            drawing_data["camera_input"]
                        )
                if "oakd_rgb_camera_input" in drawing_data:
                    if isinstance(drawing_data["oakd_rgb_camera_input"], str):
                        drawing_data["oakd_rgb_camera_input"] = decode_image_byte(
                            drawing_data["oakd_rgb_camera_input"]
                        )

                # num = 2.0
                # for i in range(10000):
                #     num = num + math.log(math.exp(3))
                # logging.warning("Number is " + str(num))
                # success = True
                success = drawing_func(drawing_data, window)

        return success
