""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

import logging
import sys
import time
import json
import uuid
from curt.handler import Handler
from curt.base_command import BaseCommand


class CURTCommands:

    base_command = BaseCommand()

    @staticmethod
    def initialize():
        success, broker_address = CURTCommands.base_command.connect_to_curt()
        if not success:
            print(
                "Failed connecting to any MQTT brokers, please check your broker or network settings."
            )
            sys.exit()
        return broker_address

    @staticmethod
    def get_modules():
        return CURTCommands.base_command.module_list

    @staticmethod
    def get_worker(worker):
        retrieved_worker = None
        worker_identifiers = worker.split("/")
        all_modules = CURTCommands.get_modules()
        selected_modules = all_modules[worker_identifiers[1]]
        for module in selected_modules:
            if worker_identifiers[0] in module.config_channel:
                for worker in module.worker_list:
                    if worker.name == worker_identifiers[-1]:
                        retrieved_worker = worker
        return retrieved_worker

    @staticmethod
    def request(worker, params=None, listen_to_handler=False):
        selected_worker = worker
        if isinstance(worker, str):
            selected_worker = CURTCommands.base_command.select_worker(worker)
        if isinstance(params, dict):
            sync_handler = params['sync_handler']
            return_handler = None
            for window in params:
                if window != "sync_handler":
                    for handler in params[window]:
                        config = {window: [handler]}
                        rendering_handler = CURTCommands.render(selected_worker, config=config)
                        if handler.guid == sync_handler.guid:
                            return_handler = rendering_handler
            return return_handler
        source_channel = []
        source_guid = []
        data = []
        if params is None:
            return CURTCommands.base_command.execute(selected_worker)
        for param in params:
            if isinstance(param, Handler):
                source_channel.append(param.output_channel)
                source_guid.append(param.guid)
            else:
                data.append(param)
        for i in range(len(source_channel)):
            data.append(None)
        handler = CURTCommands.base_command.execute(
            selected_worker, source_channel, source_guid, data
        )
        if listen_to_handler:
            CURTCommands.base_command.sync_client.subscribe(handler.output_channel)
            CURTCommands.base_command.current_listening_topics.append(
                handler.output_channel
            )
        return handler


    @staticmethod
    def config_worker(worker, config_params):
        self_guid = uuid.uuid4().hex
        params = {
            "dataType": "Config",
            "dataValue": {
                "worker": worker.name,
                "self_guid": self_guid,
                "data": config_params,
            },
        }
        params = json.dumps(params)
        CURTCommands.base_command.command_client.publish(worker.config_channel, params)
        time.sleep(2.5)
        return Handler(
            worker.output_channel + "/" + worker.name, self_guid, worker.name
        )

    @staticmethod
    def render(worker, config, data=None):
        source_channel = []
        for window in config:
            guids = []
            for handler in config[window]:
                if handler.output_channel not in source_channel:
                    source_channel.append(handler.output_channel)
                guids.append(handler.guid)
            config[window] = guids
        return CURTCommands.base_command.execute(
            worker, source_channel=source_channel, source_guid=config, data=data
        )

    @staticmethod
    def get_result(handler, for_streaming=False, callback=None):
        return CURTCommands.base_command.sync_for_result(
            handler, for_streaming, callback
        )

    @staticmethod
    def send_task(worker, data):
        return CURTCommands.base_command.execute(worker, data=data)

    @staticmethod
    def do_not_wait():
        self_guid = uuid.uuid4().hex
        output_channel = "cait/nowait"
        name = "no_wait_placeholder"
        msg = {
            "dataType": "Data",
            "dataValue": {"worker": name, "self_guid": self_guid, "data": "no_wait"},
        }
        msg = json.dumps(msg)
        CURTCommands.base_command.command_client.publish(
            output_channel, msg, retain=True
        )
        return (output_channel, self_guid, name)
