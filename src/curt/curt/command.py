""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, August 2020

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
    def get_vision_input_services():
        all_modules = CURTCommands.get_modules()
        vision_input_workers = []
        if "vision" in all_modules:
            for module in all_modules["vision"]:
                for worker in module.worker_list:
                    if worker.name.find("input") != -1:
                        vision_input_workers.append(worker)
        return vision_input_workers

    @staticmethod
    def get_vision_render_services():
        all_modules = CURTCommands.get_modules()
        vision_render_workers = []
        if "vision" in all_modules:
            for module in all_modules["vision"]:
                for worker in module.worker_list:
                    if worker.name.find("render") != -1:
                        vision_render_workers.append(worker)
        return vision_render_workers

    @staticmethod
    def get_voice_input_services():
        all_modules = CURTCommands.get_modules()
        voice_input_workers = []
        if "voice" in all_modules:
            for module in all_modules["voice"]:
                for worker in module.worker_list:
                    if worker.name.find("input") != -1:
                        voice_input_workers.append(worker)
        return voice_input_workers

    @staticmethod
    def get_voice_processing_services():
        all_modules = CURTCommands.get_modules()
        voice_processing_workers = []
        if "voice" in all_modules:
            for module in all_modules["voice"]:
                for worker in module.worker_list:
                    if worker.name.find("processing") != -1:
                        voice_processing_workers.append(worker)
        return voice_processing_workers

    @staticmethod
    def get_voice_generation_services():
        all_modules = CURTCommands.get_modules()
        voice_generation_workers = []
        if "voice" in all_modules:
            for module in all_modules["voice"]:
                for worker in module.worker_list:
                    if worker.name.find("generation") != -1:
                        voice_generation_workers.append(worker)
        return voice_generation_workers

    @staticmethod
    def get_nlp_intent_services():
        all_modules = CURTCommands.get_modules()
        nlp_intent_workers = []
        if "nlp" in all_modules:
            for module in all_modules["nlp"]:
                for worker in module.worker_list:
                    if worker.name.find("intent") != -1:
                        nlp_intent_workers.append(worker)
        return nlp_intent_workers

    @staticmethod
    def get_control_services():
        all_modules = CURTCommands.get_modules()
        control_workers = []
        if "control" in all_modules:
            for module in all_modules["control"]:
                for worker in module.worker_list:
                    if worker.name.find("control") != -1:
                        control_workers.append(worker)
        return control_workers

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
    def capture_frame(worker):
        return CURTCommands.base_command.execute(worker, data=False)

    @staticmethod
    def oakd_get_sysinfo(worker):
        return CURTCommands.base_command.execute(worker, data=["get_sysinfo"])

    @staticmethod
    def oakd_get_still_frame(worker):
        return CURTCommands.base_command.execute(worker, data=["get_still_frame"])

    @staticmethod
    def oakd_face_detection(
        worker, threshold, largest_face, image_handler=None, img=None
    ):
        if image_handler is not None:
            return CURTCommands.base_command.execute(
                worker,
                source_channel=[image_handler[0]],
                source_guid=[image_handler[1]],
                data=[
                    "detect_face",
                    threshold,
                    largest_face,
                    None,
                ],
            )
        else:
            if img is None:
                return CURTCommands.base_command.execute(
                    worker,
                    data=[
                        "detect_face_pipeline",
                        threshold,
                        largest_face,
                    ],
                )
            else:
                return CURTCommands.base_command.execute(
                    worker,
                    data=[
                        "detect_face",
                        threshold,
                        largest_face,
                        img,
                    ],
                )

    @staticmethod
    def oakd_object_detection(worker, image_handler):
        source_channel = []
        source_guid = []
        data = ["detect_object"]
        if isinstance(image_handler, list):
            for handler in image_handler:
                source_channel.append(handler[0])
                source_guid.append(handler[1])
                data.append(None)
        else:
            source_channel.append(image_handler[0])
            source_guid.append(image_handler[1])
            data.append(None)
        return CURTCommands.base_command.execute(
            worker, source_channel=source_channel, source_guid=source_guid, data=data
        )

    @staticmethod
    def oakd_movenet_estimation(worker, nn_node_name, image_handler):
        return CURTCommands.base_command.execute(
            worker,
            source_channel=[image_handler[0]],
            source_guid=[image_handler[1]],
            data=[
                "get_movenet_estimation",
                nn_node_name,
                None,
            ],
        )

    @staticmethod
    def measure_heartrate(
        worker, face_detection_handler, face_landmark_handler, image_handler
    ):
        return CURTCommands.base_command.execute(
            worker,
            source_channel=[
                face_detection_handler[0],
                face_landmark_handler[0],
                image_handler[0],
            ],
            source_guid=[
                face_detection_handler[1],
                face_landmark_handler[1],
                image_handler[1],
            ],
            data=None,
        )

    @staticmethod
    def generate_database(
        worker,
        face_detect_nn_node_name,
        face_landmark_nn_node_name,
        face_feature_node_name,
        image_location,
    ):
        return CURTCommands.base_command.execute(
            worker,
            data=[
                "generate_database",
                face_detect_nn_node_name,
                face_landmark_nn_node_name,
                face_feature_node_name,
                image_location,
            ],
        )

    @staticmethod
    def load_database(worker, database_location):
        return CURTCommands.base_command.execute(
            worker, data=["load_database", database_location]
        )

    @staticmethod
    def load_database(worker, database_location):
        return CURTCommands.base_command.execute(
            worker, data=["load_database", database_location]
        )

    @staticmethod
    def face_detection(image_handler, data=None):
        worker = CURTCommands.base_command.select_worker("face_detection")
        return CURTCommands.base_command.execute(
            worker,
            source_channel=image_handler.output_channel,
            source_guid=image_handler.guid,
            data=data,
        )

    @staticmethod
    def facemesh_estimation(image_handler, face_detection_handler, data=None):
        worker = CURTCommands.base_command.select_worker("face_mesh")
        return CURTCommands.base_command.execute(
            worker,
            source_channel=[image_handler[0], face_detection_handler[0]],
            source_guid=[image_handler[1], face_detection_handler[1]],
            data=data,
        )

    @staticmethod
    def face_recognition():
        CURTCommands.base_command.execute("face_recognition")

    @staticmethod
    def draw_face_bbox(
        worker, window_name, image_handler, face_detection_handler, data=None
    ):
        return CURTCommands.base_command.execute(
            worker,
            source_channel=[image_handler[0], face_detection_handler[0]],
            source_guid={window_name: [image_handler[1], face_detection_handler[1]]},
            data=data,
        )

    @staticmethod
    def draw_facemesh(worker, window_name, image_handler, facemesh_handler, data=None):
        return CURTCommands.base_command.execute(
            worker,
            source_channel=[image_handler[0], facemesh_handler[0]],
            source_guid={window_name: [image_handler[1], facemesh_handler[1]]},
            data=data,
        )

    @staticmethod
    def start_voice_recording(worker):
        return CURTCommands.base_command.execute(worker, data="start")

    @staticmethod
    def get_recorded_voice(worker):
        return CURTCommands.base_command.execute(worker, data="get")

    @staticmethod
    def pause_recording(worker):
        return CURTCommands.base_command.execute(worker, data="pause")

    @staticmethod
    def resume_recording(worker):
        return CURTCommands.base_command.execute(worker, data="resume")

    @staticmethod
    def get_speech_direction(worker):
        return CURTCommands.base_command.execute(worker, data="direction")

    @staticmethod
    def online_speech_to_text(worker, voice_input_handler, data=None):
        # worker = CURTCommands.base_command.select_worker("online_voice_processing")
        return CURTCommands.base_command.execute(
            worker,
            source_channel=voice_input_handler[0],
            source_guid=voice_input_handler[1],
            data=data,
        )

    @staticmethod
    def online_text_to_speech(worker, speech_processing_handler, data=None):
        # worker = CURTCommands.base_command.select_worker("online_voice_generation")
        return CURTCommands.base_command.execute(
            worker,
            source_channel=speech_processing_handler[0],
            source_guid=speech_processing_handler[1],
            data=data,
        )

    @staticmethod
    def rotate_motor_pair_for_degrees(worker, motor_1, motor_2, degrees, speed):
        return CURTCommands.send_task(
            worker,
            data={
                "control_type": "motor",
                "operation": {
                    "motor_arrangement": "pair",
                    "motor_1": motor_1,
                    "motor_2": motor_2,
                    "motion": "rotate_on_degrees",
                    "degrees": degrees,
                    "speed": speed,
                },
            },
        )

    @staticmethod
    def set_motor_pair_speed(worker, motor_1, motor_2, speed_1, speed_2):
        return CURTCommands.send_task(
            worker,
            data={
                "control_type": "motor",
                "operation": {
                    "motor_arrangement": "pair",
                    "motor_1": motor_1,
                    "motor_2": motor_2,
                    "motion": "speed",
                    "speed_1": speed_1,
                    "speed_2": speed_2,
                },
            },
        )

    @staticmethod
    def brake_motor_pair(worker, motor_1, motor_2):
        return CURTCommands.send_task(
            worker,
            data={
                "control_type": "motor",
                "operation": {
                    "motor_arrangement": "pair",
                    "motor_1": motor_1,
                    "motor_2": motor_2,
                    "motion": "brake",
                },
            },
        )

    @staticmethod
    def robot_speak(worker, sentence):
        return CURTCommands.send_task(
            worker, data={"control_type": "sound", "sentence": sentence}
        )

    @staticmethod
    def display_image(worker, image):
        return CURTCommands.send_task(
            worker,
            data={
                "control_type": "display",
                "data": {"display_type": "image", "image": image},
            },
        )

    @staticmethod
    def display_text(worker, text):
        return CURTCommands.send_task(
            worker,
            data={
                "control_type": "display",
                "data": {"display_type": "text", "text": text},
            },
        )

    @staticmethod
    def render(worker, config, data=None):
        source_channel = []
        for window in config:
            guids = []
            for handler in config[window]:
                if handler[0] not in source_channel:
                    source_channel.append(handler[0])
                guids.append(handler[1])
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
