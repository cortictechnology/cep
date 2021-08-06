""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

import logging
import time
import requests
import json
from curt.modules.smarthome.base_provider import BaseProvider


class HAProvider(BaseProvider):
    def __init__(self):
        super().__init__()

    def config_control_handler(self, params):
        self.token = params['token']
        self.authorization = "Bearer " + self.token
        self.headers = {
            "Authorization": self.authorization,
            "content-type": "application/json",
        }
        return True
    
    def get_devices(self, data):
        device_type = data['parameter']
        url = "http://0.0.0.0:8123/api/states"
        response = requests.request("GET", url, headers=self.headers)
        response_data = response.json()

        device_names = []

        for state in response_data:
            if state["entity_id"].find(device_type + ".") != -1:
                detail_url = "http://0.0.0.0:8123/api/states/" + state["entity_id"]
                detail_response = requests.request(
                    "GET", detail_url, headers=self.headers
                ).json()
                if detail_response["state"] != "unavailable":
                    name = state["entity_id"][state["entity_id"].find(".") + 1 :]
                    device_names.append(name)
        return device_names

    def control_light(self, data):
        device_name = data['device_name']
        operation = data['operation']
        parameter = data['parameter']
        if operation == "turn_on" or operation == "turn_off" or operation == "toggle":
            url = "http://0.0.0.0:8123/api/services/light/" + operation
            data = {"entity_id": device_name}
        else:
            if operation == "color_name":
                url = "http://0.0.0.0:8123/api/services/light/turn_on"
                data = {"entity_id": device_name, "color_name": parameter}
            elif operation == "brightness_pct":
                url = "http://0.0.0.0:8123/api/services/light/turn_on"
                data = {"entity_id": device_name, "brightness_pct": int(parameter)}
        response = requests.request("POST", url, headers=self.headers, data=json.dumps(data))
        return response.json()

    def control_media_player(self, data):
        device_name = data['device_name']
        operation = data['operation']
        url = "http://0.0.0.0:8123/api/services/media_player/" + operation
        data = {"entity_id": device_name}
        response = requests.request("POST", url, headers=self.headers, data=json.dumps(data))
        return response.json()
