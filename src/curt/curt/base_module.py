""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, August 2020

"""

from abc import abstractmethod
import threading
import paho.mqtt.client as mqtt
import os
import socket
import time
import json
import logging
import importlib
import collections
import traceback
from curt.utils import circularlist

logging.getLogger().setLevel(logging.INFO)


class BaseModule:
    def __init__(self, module_type):

        self.module_type = module_type
        self.config_channel = (
            "cait/config/" + socket.getfqdn().lower() + "/" + self.module_type
        )
        self.task_channel = (
            "cait/task/" + socket.getfqdn().lower() + "/" + self.module_type
        )
        self.output_channel = (
            "cait/output/" + socket.getfqdn().lower() + "/" + self.module_type
        )
        self.streaming_channel = (
            "cait/streaming/" + socket.getfqdn().lower() + "/" + self.module_type
        )
        self.input_channels = []
        self.publish_client = mqtt.Client()

        self.listen_command_client = mqtt.Client()
        self.listen_command_client.on_connect = self.on_connect
        self.listen_command_client.on_message = self.on_message

        self.service_worker_map = {}
        self.worker_factory = None
        self.services = {}
        self.create_factory()
        self.create_services()
        for service in self.services:
            self.services[service].on_finishing_handler = self.on_finish
        self.unclaimed_data = collections.deque(maxlen=20)
        self.avg_process_remote_data_time = circularlist(20)

    def initialize(self, broker_ip):
        self.broker_ip = broker_ip
        ret = self.connect_mqtt(self.publish_client)
        while ret != True:
            time.sleep(1)
            ret = self.connect_mqtt(self.publish_client)
        self.publish_client.loop_start()
        self.publish_client.publish(self.output_channel, "", retain=True)
        self.publish_client.publish(self.config_channel, "", retain=True)
        self.publish_client.publish(self.task_channel, "", retain=True)
        ret = self.connect_mqtt(self.listen_command_client)
        while ret != True:
            time.sleep(1)
            ret = self.connect_mqtt(self.listen_command_client)
        self.listen_command_client.loop_start()
        print(self.module_type, "module initialized.")

    def connect_mqtt(self, client):
        try:
            # logging.warning("Broker ip: " + str(self.broker_ip))
            client.connect(self.broker_ip, 1883, 60)
            logging.info("Connected to broker")
            return True
        except Exception as e:
            logging.warning(e)
            logging.info("Broker not up yet, retrying...")
            return False

    @abstractmethod
    def create_factory(self):
        pass

    def create_services(self):
        for service in self.worker_factory.service_info:
            serv = importlib.import_module(
                "curt.modules." + self.module_type + "." + service
            )
            serv_class = getattr(serv, self.worker_factory.service_info[service])()
            worker_names = self.worker_factory.service_worker_map[service]
            for name in worker_names:
                serv_class.workers[name] = self.worker_factory.workers[name]
            self.services[serv_class.service_type] = serv_class

    def matach_data_to_guid_list(self, _data, source_guid):
        task_data = {}
        if _data is None:
            for i in range(len(self.unclaimed_data)):
                if self.unclaimed_data[i][0] in source_guid:
                    task_data[self.unclaimed_data[i][0]] = [
                        self.unclaimed_data[i][1],
                        self.unclaimed_data[i][2],
                    ]
        elif isinstance(_data, list):
            task_data["ready_data"] = []
            # TO-DO: Need a better way to arange the node name parameters from the other data
            for i in range(len(_data)):
                if _data[i] is not None:
                    task_data["ready_data"].append(_data[i])
            for i in range(len(self.unclaimed_data)):
                if self.unclaimed_data[i][0] in source_guid:
                    task_data[self.unclaimed_data[i][0]] = [
                        self.unclaimed_data[i][1],
                        self.unclaimed_data[i][2],
                    ]
        else:
            for i in range(len(source_guid)):
                task_data[source_guid[i]] = ["NA", _data[i]]

        return task_data

    @abstractmethod
    def process_remote_data(self, data):
        pass

    def process_local_data(self, data):
        return data

    def on_connect(self, client, userdata, flags, rc):
        logging.info(
            self.module_type + " connected to broker with result code " + str(rc)
        )
        client.subscribe(self.config_channel)
        client.subscribe(self.task_channel)
        logging.info(self.module_type + " subscribed to: " + str(self.config_channel))
        logging.info(self.module_type + " subscribed to: " + str(self.task_channel))

    def on_message(self, client, userdata, msg):
        data = msg.payload.decode()
        try:
            data = json.loads(data)
            if msg.topic == self.config_channel:
                if data["dataType"] == "SubscribeTo":
                    if data["dataValue"].find(os.uname()[1].lower()) == -1:
                        if data["dataValue"] not in self.input_channels:
                            self.input_channels.append(data["dataValue"])
                            client.subscribe(data["dataValue"])
                            time.sleep(0.001)
                            logging.info(
                                self.module_type
                                + " subscribed to: "
                                + str(data["dataValue"])
                            )
                elif data["dataType"] == "UnsubscribeFrom":
                    if data["dataValue"] in self.input_channels:
                        client.unsubscribe(data["dataValue"])
                        time.sleep(0.001)
                        logging.info(
                            self.module_type
                            + " unsubscribed from: "
                            + str(data["dataValue"])
                        )
                elif data["dataType"] == "Config":
                    worker = data["dataValue"]["worker"]
                    self_guid = data["dataValue"]["self_guid"]
                    _data = data["dataValue"]["data"]
                    _data = [_data, True]
                    for service in self.services:
                        if worker in self.services[service].workers:
                            self.services[service].add_task(
                                [worker, "None1", self_guid, msg.topic, _data]
                            )
                            self.services[service].execute_next_task()
            elif msg.topic == self.task_channel:
                if data["dataType"] == "Task":
                    worker = data["dataValue"]["worker"]
                    source_guid = data["dataValue"]["source_guid"]
                    self_guid = data["dataValue"]["self_guid"]
                    msg_topic = msg.topic
                    _data = data["dataValue"]["data"]
                    task_data = _data
                    if isinstance(source_guid, list):
                        task_data = self.matach_data_to_guid_list(_data, source_guid)
                    elif isinstance(source_guid, dict):
                        task_data = []
                        for render_window in source_guid:
                            input_guid = source_guid[render_window]
                            _task_data = self.matach_data_to_guid_list(
                                _data, input_guid
                            )
                            task_data.append({render_window: _task_data})
                    else:
                        if _data is None:
                            for i in range(len(self.unclaimed_data)):
                                if self.unclaimed_data[i][0] == source_guid:
                                    # print("Matched with:", source_guid)
                                    task_data = self.unclaimed_data[i][2]
                    task_data = [task_data, False]
                    # t1 = time.time()
                    for service in self.services:
                        if worker in self.services[service].workers:
                            self.services[service].add_task(
                                [worker, source_guid, self_guid, msg_topic, task_data]
                            )
                            if self.services[service].get_load() <= 2:
                                self.services[service].execute_next_task()
                            break
                    # print("Task execution time:", time.time() - t1)
            else:
                if data["dataType"] == "Data":
                    worker = data["dataValue"]["worker"]
                    self_guid = data["dataValue"]["self_guid"]
                    _data = data["dataValue"]["data"]
                    has_matched = False
                    task_data = _data
                    # print(task_data)
                    for service in self.services:
                        has_matched = self.services[service].task_data_has_match(
                            self_guid, worker
                        )
                        task_data = self.process_remote_data(task_data)
                        if has_matched:
                            # t1 = time.monotonic()
                            # self.avg_process_remote_data_time.append(
                            #     time.monotonic() - t1
                            # )
                            # print(
                            #     "decoding time:",
                            #     self.avg_process_remote_data_time.calc_average(),
                            # )
                            filled = self.services[service].fill_in_task_data(
                                self_guid, worker, task_data
                            )
                    if not has_matched:
                        self.unclaimed_data.append([self_guid, worker, task_data])
                    for service in self.services:
                        self.services[service].execute_next_task()
        except Exception as e:
            logging.error(traceback.format_exc())

    def on_finish(
        self, worker, source_guid, self_guid, msg_topic, result, service_type
    ):
        # Trigger by worker's finishing action
        # Publish and store result data to service queue
        # t1 = time.time()
        worker_name = worker
        if worker == "webcam_input" or worker == "picam_input":
            worker_name = "camera_input"
        if isinstance(result, tuple):
            msg = {
                "dataType": "Data",
                "dataValue": {
                    "worker": worker_name,
                    "self_guid": self_guid,
                    "data": result[1],
                },
            }
        else:
            msg = {
                "dataType": "Data",
                "dataValue": {
                    "worker": worker_name,
                    "self_guid": self_guid,
                    "data": result,
                },
            }
        # logging.warning(str(msg))
        msg = json.dumps(msg)
        self.publish_client.publish(
            self.output_channel + "/" + worker, msg, qos=1, retain=True
        )
        # if worker == "oakd_facemesh":
        #    print("***********Facemesh published***********    ", self_guid)
        # if self.enable_streaming:
        #     self.streaming_client.publish(self.streaming_channel, msg, qos=1, retain=True)
        # print("Finish handler (publish message) time:", time.time() - t1)
        # t1 = time.time()
        data_filled = False
        for service in self.services:
            if isinstance(result, tuple):
                filled = self.services[service].fill_in_task_data(
                    self_guid, worker_name, result[0]
                )
            else:
                filled = self.services[service].fill_in_task_data(
                    self_guid, worker_name, result
                )
            data_filled = data_filled or filled
        # print("Finish handler (fill data) time:", time.time() - t1)
        # t1 = time.time()
        if not data_filled:
            if isinstance(result, tuple):
                self.unclaimed_data.append([self_guid, worker_name, result[0]])
            else:
                self.unclaimed_data.append([self_guid, worker_name, result])
            # print("Appending unclaimed data from:", self_guid)
        # print("Finish handler (add unclaimed) time:", time.time() - t1)
