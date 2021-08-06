""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, October 2020

"""

from abc import abstractmethod

class BaseProvider:
    def __init__(self):
        self.token = ""

    @abstractmethod
    def config_control_handler(self, params):
        pass

    def command(self, params):
        data = params["ready_data"][0]
        if data["control_type"] == "get_devices":
            return self.get_devices(data["operation"])
        elif data["control_type"] == "light":
            return self.control_light(data["operation"])
        elif data["control_type"] == "media_player":
            return self.control_media_player(data["operation"])

    @abstractmethod
    def get_devices(self, data):
        pass

    @abstractmethod
    def control_light(self, data):
        pass

    @abstractmethod
    def control_media_player(self, data):
        pass