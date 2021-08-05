""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, August 2020

"""

import paho.mqtt.client as mqtt
import logging
import time
import json
import uuid
import socket
import collections

# import psutil

from curt.module import Module
from curt.worker import Worker
from curt.handler import Handler

logging.getLogger().setLevel(logging.INFO)

# Use one mqtt client for publishing command
class BaseCommand:
    def __init__(self):
        self.command_client = mqtt.Client()
        self.sync_client = mqtt.Client()
        self.sync_client.on_connect = self.on_connect_sync
        self.sync_client.on_message = self.on_message_sync
        self.sync_client_stream = mqtt.Client()
        self.sync_client_stream.on_connect = self.on_connect_sync_stream
        self.sync_client_stream.on_message = self.on_message_sync_stream
        self.selected_service = None
        self.module_list = {}
        self.hearbeat_client = mqtt.Client()
        self.hearbeat_client.on_connect = self.on_connect_hearbeat
        self.hearbeat_client.on_message = self.on_message_heartbeat
        self.connected_to_cait = False
        self.remote_worker_to_sync = None
        self.remote_guid_to_sync = None
        self.remote_result = None
        self.remote_worker_to_sync_stream = None
        self.remote_guid_to_sync_stream = None
        self.remote_result_stream = None
        self.current_sync_channel = ""
        self.current_sync_channel_stream = ""
        self.result_channels = {}
        self.unclaimed_data = collections.deque(maxlen=50)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = ("", 9435)
        self.sock.bind(server_address)
        self.current_listening_topics = []

    def connect_mqtt(self, client, address):
        try:
            client.connect(address, 1883, 60)
            logging.info("Connected to broker")
            self.connected_to_cait = True
            client.loop_start()
            return True
        except:
            logging.info("Broker: (" + address + ") not up yet, retrying...")
            return False

    def connect_to_curt(self):
        curt_broker_address = ""
        start_time = time.perf_counter()
        while time.perf_counter() - start_time < 60:
            data, address = self.sock.recvfrom(4096)
            data = str(data.decode("UTF-8"))
            if "curt_broker_available" in data:
                curt_broker_address = address[0]
                break
        if curt_broker_address == "":
            return False, ""
        print("Found a curt broker at:", curt_broker_address)
        ret = self.connect_mqtt(self.command_client, curt_broker_address)
        while ret != True:
            time.sleep(1)
            ret = self.connect_mqtt(self.command_client, curt_broker_address)
        ret = self.connect_mqtt(self.sync_client, curt_broker_address)
        while ret != True:
            time.sleep(1)
            ret = self.connect_mqtt(self.sync_client, curt_broker_address)
        ret = self.connect_mqtt(self.sync_client_stream, curt_broker_address)
        while ret != True:
            time.sleep(1)
            ret = self.connect_mqtt(self.sync_client_stream, curt_broker_address)
        ret = self.connect_mqtt(self.hearbeat_client, curt_broker_address)
        while ret != True:
            time.sleep(1)
            ret = self.connect_mqtt(self.hearbeat_client, curt_broker_address)
        self.broker_address = curt_broker_address
        time.sleep(2)
        return ret, curt_broker_address

    def on_connect_sync(self, client, userdata, flags, rc):
        logging.info("Sync client connected to broker with result code " + str(rc))

    def on_message_sync(self, client, userdata, msg):
        data = msg.payload.decode()
        data = json.loads(data)
        self.unclaimed_data.append(data)

    def on_connect_sync_stream(self, client, userdata, flags, rc):
        logging.info("Sync client connected to broker with result code " + str(rc))

    def on_message_sync_stream(self, client, userdata, msg):
        data = msg.payload.decode()
        data = json.loads(data)
        # if self.remote_guid_to_sync is not None:
        if data["dataValue"]["worker"] == self.remote_worker_to_sync_stream:
            if data["dataValue"]["self_guid"] == self.remote_guid_to_sync_stream:
                self.remote_result_stream = data

    def on_connect_hearbeat(self, client, userdata, flags, rc):
        # heartbeat client should subscribe to heartbeat
        logging.info(
            "Command interface connected to broker with result code " + str(rc)
        )
        client.subscribe("cait/heartbeats")
        logging.info("Command interface subscribed to hearbeat channel")

    def on_message_heartbeat(self, client, userdata, msg):
        data = msg.payload.decode()
        data = json.loads(data)
        if data["module_type"] not in self.module_list:
            worker_list = []
            for worker_name in data["worker_list"]:
                worker_list.append(
                    Worker(
                        worker_name,
                        data["config_channel"],
                        data["task_channel"],
                        data["output_channel"],
                    )
                )
            module = Module(
                data["module_type"],
                data["config_channel"],
                data["task_channel"],
                data["output_channel"],
                worker_list,
                data["load"],
            )
            self.module_list[data["module_type"]] = [module]
        else:
            service_exist = False
            for service in self.module_list[data["module_type"]]:
                if (
                    service.config_channel == data["config_channel"]
                    and service.output_channel == data["output_channel"]
                ):
                    service.load = data["load"]
                    service_exist = True
            if not service_exist:
                worker_list = []
                for worker_name in data["worker_list"]:
                    worker_list.append(
                        Worker(
                            worker_name,
                            data["config_channel"],
                            data["task_channel"],
                            data["output_channel"],
                        )
                    )
                module = Module(
                    data["module_type"],
                    data["config_channel"],
                    data["task_channel"],
                    data["output_channel"],
                    worker_list,
                    data["load"],
                )
                self.module_list[data["module_type"]].append(module)

    def select_worker(self, worker_name):
        available_worker_list = []
        for module_type in self.module_list:
            for module in self.module_list[module_type]:
                for worker in module.worker_list:
                    if worker.name == worker_name:
                        broker_hostname = self.broker_address[
                            0 : self.broker_address.find(".")
                        ]
                        if broker_hostname in worker.config_channel:
                            available_worker_list.append((module.load, worker, True))
                        else:
                            available_worker_list.append((module.load, worker, False))
        if len(available_worker_list) > 0:
            available_worker_list = sorted(available_worker_list, key=lambda x: x[0])
            for worker in available_worker_list:
                if worker[2]:
                    return worker[1]
            return available_worker_list[0][1]
        else:
            return None

    def subscribe_to(self, worker, channel):
        msg = {"dataType": "SubscribeTo", "dataValue": channel}
        msg = json.dumps(msg)
        self.command_client.publish(worker.config_channel, msg, retain=True)

    def execute(self, worker, source_channel=[], source_guid=[], data=[]):
        # for every command, need a guid to attach
        self_guid = uuid.uuid4().hex

        task = {
            "dataType": "Task",
            "dataValue": {
                "worker": worker.name,
                "source_guid": source_guid,
                "self_guid": self_guid,
                "data": data,
            },
        }
        task = json.dumps(task)
        for channel in source_channel:
            if channel != "":
                if channel not in worker.input_channels:
                    self.subscribe_to(worker, channel)
                    worker.input_channels.append(channel)
        self.command_client.publish(worker.task_channel, task, retain=True)
        return Handler(
            worker.output_channel + "/" + worker.name, self_guid, worker.name
        )

    def sync_for_result(self, handler, for_streaming=False, callback=None):
        # if callback is None:
        if not for_streaming:
            remote_result = None
            if handler.output_channel not in self.current_listening_topics:
                self.sync_client.subscribe(handler.output_channel)
                self.current_listening_topics.append(handler.output_channel)
            while remote_result == None:
                for data in list(self.unclaimed_data):
                    if data["dataValue"]["worker"] == handler.name:
                        if data["dataValue"]["self_guid"] == handler.guid:
                            remote_result = data
                            self.unclaimed_data.remove(data)
            return remote_result
        else:
            self.remote_result_stream = None
            self.remote_worker_to_sync_stream = handler.name
            self.remote_guid_to_sync_stream = handler.guid
            if self.current_sync_channel_stream != handler.output_channel:
                if self.current_sync_channel_stream != "":
                    self.sync_client_stream.unsubscribe(
                        self.current_sync_channel_stream
                    )
            self.sync_client_stream.subscribe(handler.output_channel)
            self.current_sync_channel_stream = handler.output_channel
            while self.remote_result_stream == None:
                time.sleep(0.001)
            self.remote_worker_to_sync_stream = None
            self.remote_guid_to_sync_stream = None
            return self.remote_result_stream