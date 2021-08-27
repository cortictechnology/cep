""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

from abc import abstractmethod


class BaseControl:
    def __init__(self, hub_type):
        self.hub_address = ""
        self.hub_type = hub_type
        self.connection = None

    @abstractmethod
    def config_control_handler(self, params):
        pass

    def command(self, params):
        data = params["ready_data"][0]
        if data["control_type"] == "motor":
            return self.control_motor(data["operation"])
        elif data["control_type"] == "sensor":
            return self.capture_sensor_data(data["operation"])
        elif data["control_type"] == "sound":
            return self.sound(data["sentence"])
        elif data["control_type"] == "display":
            return self.display(data["data"])

    @abstractmethod
    def control_motor(self, data):
        pass

    @abstractmethod
    def capture_sensor_data(self, data):
        pass

    @abstractmethod
    def sound(self, data):
        pass

    @abstractmethod
    def display(self, data):
        pass
