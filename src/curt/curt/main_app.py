""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, August 2020

"""

import paho.mqtt.client as mqtt
from abc import abstractmethod
import logging
import time
import json

# import psutil
import signal
from curt.utils import circularlist


class MainApp:
    def __init__(self, broker_address):
        self.curt_address = broker_address
        self.current_finishing_handlers = {}
        self.finishing_handlers = []
        self.step_client = mqtt.Client()
        self.step_client.on_connect = self.on_connect
        self.step_client.on_message = self.on_message
        ret = self.connect_mqtt(self.step_client, broker_address)
        while ret != True:
            time.sleep(1)
            ret = self.connect_mqtt(self.step_client, broker_address)
        # self.counter = 0
        self.init_time = time.time()
        self.framerates = circularlist(10)
        self.subscribed_topic = []
        signal.signal(signal.SIGINT, self.cleanup)

    def connect_mqtt(self, client, address):
        try:
            client.connect(address, 1883, 60)
            logging.info("Connected to broker")
            self.connected_to_cait = True
            return True
        except:
            logging.info("Broker: (" + address + ") not up yet, retrying...")
            return False

    def on_connect(self, client, userdata, flags, rc):
        logging.info("App connected to broker with result code " + str(rc))

    def on_message(self, client, userdata, msg):
        data = msg.payload.decode()
        # logging.warning(str(data))
        data = json.loads(data)
        task_id = data["dataValue"]["self_guid"]
        if task_id in self.current_finishing_handlers:
            if (
                data["dataValue"]["worker"]
                == self.current_finishing_handlers[task_id][0]
            ):
                self.current_finishing_handlers[task_id][1] = True
        all_handles_sync = True
        for handler in self.current_finishing_handlers:
            all_handles_sync = (
                all_handles_sync and self.current_finishing_handlers[handler][1]
            )
        if all_handles_sync and len(self.current_finishing_handlers) > 0:
            # self.counter = self.counter + 1
            # elapsed_time = time.time() - self.init_time
            # if elapsed_time > 1:
            #    self.framerates.append(float(self.counter) / elapsed_time)
            #    print("Average FPS:", self.framerates.calc_average())
            #    self.counter = 0
            #    self.init_time = time.time()
            self.current_finishing_handlers = {}
            self.on_step()
            self.end_step()

    @abstractmethod
    def setup(self):
        # setup module paramerts
        pass

    @abstractmethod
    def on_step(self):
        pass

    def end_step(self):
        # hearbeat client subscribe to the finishing_handles, return upon received messages
        # if finishing_handles are changed, unsubscribe and subscribe again
        if len(self.finishing_handlers) == 0:
            logging.warning(
                "No handlers in the finishing_handler list, please make sure you add the proper ones in the on_step function"
            )
        updated_subscribed_topic = []

        for topic in self.subscribed_topic:
            worker_needed = False
            for handler_ in self.finishing_handlers:
                if topic == handler_.output_channel:
                    worker_needed = True
                    updated_subscribed_topic.append(topic)

            if not worker_needed:
                logging.warning("unsubscribe from: " + topic)
                self.step_client.unsubscribe(topic)
                time.sleep(0.001)

        self.subscribed_topic = updated_subscribed_topic

        for handler in self.finishing_handlers:
            self.current_finishing_handlers[handler.guid] = [handler.name, False]
            if handler.output_channel not in self.subscribed_topic:
                self.step_client.subscribe(handler.output_channel)
                time.sleep(0.001)
                logging.info("App subscribed to: " + str(handler.output_channel))
                self.subscribed_topic.append(handler.output_channel)

        self.finishing_handlers = []

    def cleanup(self, sig, frame):
        pass

    def execute(self):
        self.setup()
        logging.info("Performing Setup config")
        self.on_step()
        self.end_step()
        self.step_client.loop_forever()
