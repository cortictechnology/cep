""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

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
            return self.get_devices(data)
        elif data["control_type"] == "light":
            return self.control_light(data)
        elif data["control_type"] == "media_player":
            return self.control_media_player(data)

    @abstractmethod
    def get_devices(self, data):
        pass

    @abstractmethod
    def control_light(self, data):
        pass

    @abstractmethod
    def control_media_player(self, data):
        pass