""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

import threading
import json
import time
import socket
import logging
import sys


class ModuleMain:
    def __init__(self, module, port):
        self.module = module
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = ("", self.port)
        self.sock.bind(server_address)
        curt_broker_address = ""
        while True:
            data, address = self.sock.recvfrom(4096)
            data = str(data.decode("UTF-8"))
            if "curt_broker_available" in data:
                curt_broker_address = address[0]
                break
            print("Scanning for MQTT broker...")
            time.sleep(4)
        logging.warning("Found a curt broker at: " + str(curt_broker_address))
        self.module.initialize(curt_broker_address)
        self.heartbeat_thread = threading.Thread(
            target=self.heartbeat_func, daemon=True
        )
        self.heartbeat_thread.start()

    def heartbeat_func(self):
        while True:
            try:
                if (
                    self.module.worker_factory is not None
                    and len(self.module.services) > 0
                ):
                    msg = {
                        "module_type": self.module.module_type,
                        "config_channel": self.module.config_channel,
                        "task_channel": self.module.task_channel,
                        "output_channel": self.module.output_channel,
                    }
                    worker_list = []
                    load = 0
                    for service in self.module.services:
                        worker_list = worker_list + list(
                            self.module.services[service].workers.keys()
                        )
                        load = load + self.module.services[service].get_load()
                    msg["worker_list"] = worker_list
                    msg["load"] = load
                    msg = json.dumps(msg)
                    self.module.publish_client.publish("cait/heartbeats", msg)
            except:
                continue
            time.sleep(2)

    def run_forever(self):
        self.heartbeat_thread.join()
