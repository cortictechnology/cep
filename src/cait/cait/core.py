""" 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""
import os
import sys

curt_path = os.getenv("CURT_PATH")
sys.path.insert(0, curt_path)
from curt.command import CURTCommands
import paho.mqtt.client as mqtt
import logging
import time
import json
import socket
import requests
import base64
import threading
import queue
import numpy as np
import cv2
from .managers.device_manager import DeviceManager
from .PID import PID
from .core_data import *
from .utils import (
    get_ip_address,
    connect_mqtt,
    decode_image_byte,
    draw_face_detection,
    draw_face_recognition,
    draw_object_detection,
    draw_image_classification,
    draw_face_emotions,
    draw_facemesh,
    draw_body_landmarks,
    draw_hand_landmarks,
)

camera_img = None

full_domain_name = socket.getfqdn()

device_manager = DeviceManager()

logging.getLogger().setLevel(logging.WARNING)

logging.warning("*********Initializing CURT Command Interface*********")
broker_address = CURTCommands.initialize()

streaming_channel = "cait/output/" + os.uname()[1].lower() + "/displayFrame"
streaming_client = mqtt.Client()
hearbeat_client = mqtt.Client()
ret = connect_mqtt(streaming_client, broker_address)
while ret != True:
    time.sleep(1)
    ret = connect_mqtt(streaming_client, broker_address)
ret = connect_mqtt(hearbeat_client, broker_address)
while ret != True:
    time.sleep(1)
    ret = connect_mqtt(hearbeat_client, broker_address)


def heartbeat_func():
    global hearbeat_client
    device_info = {"hostname": os.uname()[1].lower(), "host_ip": get_ip_address()}
    while True:
        hearbeat_client.publish(
            "cait/output/" + os.uname()[1].lower() + "/system_status", "CAIT UP", qos=1
        )
        hearbeat_client.publish(
            "cait/output/device_info", json.dumps(device_info), qos=1
        )

        time.sleep(2)


heartbeat_thread = threading.Thread(target=heartbeat_func, daemon=True)
heartbeat_thread.start()

logging.warning("*********Core heartbeat thread started*********")

vision_dispatch_queue = queue.Queue()
speech_dispatch_queue = queue.Queue()
nlp_dispatch_queue = queue.Queue()
control_dispatch_queue = queue.Queue()
smart_home_dispatch_queue = queue.Queue()


def dispatch_func(dispatch_queue):
    while True:
        task_data = dispatch_queue.get()
        task_func = task_data["function"]
        task_args = task_data["args"]
        task_func(task_args)


def get_video_devices():
    return device_manager.get_video_devices()


def get_usb_devices():
    return device_manager.get_usb_devices()


def get_audio_devices():
    return device_manager.get_audio_devices()


def get_control_devices():
    control_devices = device_manager.get_control_devices()
    connected_devices = []
    for device in control_devices:
        if device["connected"]:
            if device["device"] == "EV3":
                connected_devices.append(device["device"] + ": " + device["ip_addr"])
            else:
                connected_devices.append(device["device"] + ": " + device["mac_addr"])
    return control_devices


def initialize_vision(processor="local", mode=[], from_web=False):
    global current_camera
    global oakd_nodes
    global vision_initialized
    global stream_thread
    global drawing_modes
    global preview_width
    global preview_height
    global spatial_face_detection
    global spatial_object_detection
    global user_mode
    global reset_all
    while reset_in_progress:
        time.sleep(0.1)
    reset_all = False
    drawing_modes = {
        "Depth Mode": False,
        "Face Detection": [],
        "Face Recognition": [],
        "Face Emotions": [],
        "Face Mesh": [],
        "Object Detection": [],
        "Image Classification": [],
        "Hand Landmarks": [],
        "Pose Landmarks": [],
    }
    if vision_initialized:
        vision_initialized = False
        if stream_thread is not None:
            stream_thread.join()
    if from_web:
        user_mode = "web"
    else:
        user_mode = "code"
    current_video_device = None
    if processor == "oakd":
        current_video_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/oakd_service/oakd_pipeline"
        )
        if current_video_worker is None:
            vision_initialized = False
            return (
                False,
                "No OAK device is detected, or connected device is not supported",
            )
        for node in mode:
            if node[0] == "add_rgb_cam_node":
                preview_width = node[1]
                preview_height = node[2]
                current_camera = "oakd"
            if node[0] == "add_spatial_mobilenetSSD_node":
                if node[1] == "face_detection":
                    spatial_face_detection = True
                elif node[1] == "object_detection":
                    spatial_object_detection = True
            elif node[0] == "add_nn_node_pipeline":
                if node[1] == "face_detection":
                    spatial_face_detection = False
                elif node[1] == "object_detection":
                    spatial_object_detection = False

        config_handler = CURTCommands.config_worker(current_video_worker, mode)
        success = CURTCommands.get_result(config_handler)["dataValue"]["data"]
        if not success:
            vision_initialized = False
            return (
                False,
                "Failed to initialzie oakd pipeline, please check if the device is connected.",
            )
    elif processor == "cpu":
        success = False
        if mode["index"] != -1 and mode["index"] != 99:
            current_video_worker = CURTCommands.get_worker(
                full_domain_name + "/vision/vision_input_service/webcam_input"
            )
            if current_video_worker is None:
                vision_initialized = False
                return (
                    False,
                    "No USB webcam is detected, or connected webcam is not supported",
                )
            current_camera = "webcam"
            config_handler = CURTCommands.config_worker(
                current_video_worker,
                {
                    "camera_index": mode["index"],
                    "capture_width": 640,
                    "capture_height": 480,
                    "reset": False,
                },
            )
            success = CURTCommands.get_result(config_handler)["dataValue"]["data"]
        elif mode["index"] == 99:
            current_video_worker = CURTCommands.get_worker(
                full_domain_name + "/vision/vision_input_service/picam_input"
            )
            if current_video_worker is None:
                vision_initialized = False
                return (
                    False,
                    "No CSI-Camera is detected, or connected device is not supported",
                )
            current_camera = "picam"
            config_handler = CURTCommands.config_worker(
                current_video_worker,
                {"capture_width": 640, "capture_height": 480, "reset": False},
            )
            success = CURTCommands.get_result(config_handler)["dataValue"]["data"]
        if not success:
            vision_initialized = False
            return (
                False,
                "Failed to initialize local camera, please check if the webcam or csi-camera is connected.",
            )
    vision_initialized = True
    stream_thread = threading.Thread(target=streaming_func, daemon=True)
    stream_thread.start()
    return True, "OK"


def test_camera(index):
    processor = "local"
    mode = []
    if index == "myriad":
        processor = "oakd"
        mode = [["add_rgb_cam_node", 640, 360], ["add_rgb_cam_preview_node"]]
    else:
        processor = "cpu"
        mode = {"index": index}
    return initialize_vision(processor, mode, True)


def deactivate_vision():
    global vision_initialized
    global vision_mode
    global stream_thread
    global current_camera
    global drawing_modes
    global spatial_face_detection
    global spatial_object_detection
    vision_initialized = False
    spatial_face_detection = False
    spatial_object_detection = False
    vision_mode = []
    if stream_thread is not None:
        stream_thread.join()
    drawing_modes = {
        "Depth Mode": False,
        "Face Detection": [],
        "Face Recognition": [],
        "Face Emotions": [],
        "Face Mesh": [],
        "Object Detection": [],
        "Image Classification": [],
        "Hand Landmarks": [],
        "Pose Landmarks": [],
    }
    video_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_pipeline"
    )
    if video_worker is not None:
        config_handler = CURTCommands.config_worker(
            video_worker,
            [["reset"]],
        )
    video_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/vision_input_service/webcam_input"
    )
    if video_worker is not None:
        config_handler = CURTCommands.config_worker(
            video_worker,
            {"reset": True},
        )
    video_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/vision_input_service/picam_input"
    )
    if video_worker is not None:
        config_handler = CURTCommands.config_worker(
            video_worker,
            {"reset": True},
        )
    current_camera = ""
    return True


def get_cloud_accounts():
    return account_names


def get_nlp_models():
    model_list = []
    curt_path = os.getenv("CURT_PATH")
    for model in os.listdir(curt_path + "models/modules/nlp"):
        if os.path.isdir(curt_path + "models/modules/nlp/" + model):
            model_list.append(model)
    return model_list


def initialize_voice(
    mode="online", account="default", language="english", input_device=""
):
    global voice_initialized
    global voice_mode
    global use_respeaker
    global reset_all
    reset_all = False
    speaker_attached = False
    while reset_in_progress:
        time.sleep(0.1)
    audio_devices = get_audio_devices()
    for device in audio_devices:
        if device["type"] == "Output":
            speaker_attached = True
    if not speaker_attached:
        voice_initialized = False
        return (
            False,
            "No audio output deveice is detected, or connected device is not supported",
        )
    logging.warning(str(input_device) + "*******************")
    if input_device == "":
        voice_initialized = False
        return (
            False,
            "No audio input deveice is detected, or connected device is not supported",
        )
    if language == "english":
        processing_language = "en-UK"
        generation_language = "en"
        generation_accents = "ca"
    elif language == "french":
        processing_language = "fr-FR"
        generation_language = "fr"
        generation_accents = ""
    elif language == "chinese":
        processing_language = "zh-CN"
        generation_language = "zh"
        generation_accents = ""
    voice_generation_worker = None
    voice_processing_worker = None
    index = int(input_device[0 : input_device.find(":")])
    channel_count = 1
    voice_input_worker = None
    if input_device.find("seeed") != -1:
        voice_input_worker = CURTCommands.get_worker(
            full_domain_name + "/voice/voice_input_service/respeaker_input"
        )
        use_respeaker = True
        channel_count = 4
    else:
        voice_input_worker = CURTCommands.get_worker(
            full_domain_name + "/voice/voice_input_service/live_input"
        )
        use_respeaker = False
    voice_processing_worker = None
    if mode == "online":
        voice_mode = "online"
        voice_processing_worker = CURTCommands.get_worker(
            full_domain_name + "/voice/speech_to_text_service/online_voice_processing"
        )
        voice_generation_worker = CURTCommands.get_worker(
            full_domain_name + "/voice/text_to_speech_service/online_voice_generation"
        )
    else:
        voice_mode = "offline"
        voice_processing_worker = CURTCommands.get_worker(
            full_domain_name + "/voice/speech_to_text_service/offline_voice_processing"
        )
        voice_generation_worker = CURTCommands.get_worker(
            full_domain_name + "/voice/text_to_speech_service/offline_voice_generation"
        )
    if voice_input_worker is None:
        return (
            False,
            "No audio deveice is detected, or connected device is not supported",
        )
    if voice_processing_worker is None:
        return (
            False,
            "No voice processing service is detected, or connected device is not supported",
        )
    if voice_generation_worker is None:
        return (
            False,
            "No voice generation is detected, or connected device is not supported",
        )
    logging.warning("Audio input index:" + str(index))
    config_handler = CURTCommands.config_worker(
        voice_input_worker, {"audio_in_index": index}
    )
    success = CURTCommands.get_result(config_handler)["dataValue"]["data"]
    if not success:
        return (
            False,
            "No voice input device connected. Please connect the Respeaker 4 mic array HAT and try again.",
        )
    # CURTCommands.request(voice_input_worker, params=["start"])
    # CURTCommands.start_voice_recording(voice_input_worker)
    if mode == "online":
        curt_path = os.getenv("CURT_PATH")
        account_file = cloud_accounts[account]
        with open(curt_path + "models/modules/voice/" + account_file) as f:
            account_info = json.load(f)
        config_handler = CURTCommands.config_worker(
            voice_processing_worker,
            {
                "account_crediential": account_info,
                "language": processing_language,
                "sample_rate": 16000,
                "channel_count": channel_count,
            },
        )
        success = CURTCommands.get_result(config_handler)["dataValue"]["data"]
        if not success:
            return False, "Cannot initialize voice processing worker."
        config_handler = CURTCommands.config_worker(
            voice_generation_worker,
            {"language": generation_language, "accents": generation_accents},
        )
        success = CURTCommands.get_result(config_handler)["dataValue"]["data"]
        if not success:
            return False, "Cannot initialize voice generation worker."
    time.sleep(1)
    voice_initialized = True
    return True, "OK"


def deactivate_voice():
    global voice_initialized
    voice_initialized = False
    return True


def initialize_nlp(mode="english_default"):
    global nlp_initialized
    global current_nlp_model
    global reset_all
    while reset_in_progress:
        time.sleep(0.1)
    reset_all = False
    rasa_intent_worker = CURTCommands.get_worker(
        full_domain_name + "/nlp/nlp_intent_classify_service/rasa_intent_classifier"
    )
    config_handler = CURTCommands.config_worker(rasa_intent_worker, {"model": mode})
    success = CURTCommands.get_result(config_handler)["dataValue"]["data"]
    if not success:
        nlp_initialized = False
        return False, "Failed to initialized NLP module."
    nlp_initialized = True
    return True, "OK"


def deactivate_nlp():
    return True


def initialize_control(hub_address):
    global control_initialized
    global reset_all
    while reset_in_progress:
        time.sleep(0.1)
    reset_all = False
    robot_inventor_control_worker = CURTCommands.get_worker(
        full_domain_name + "/control/control_service/robot_inventor_control"
    )
    if robot_inventor_control_worker is None:
        return False, "No control worker available"
    if isinstance(hub_address, list):
        hub_address = hub_address[0]
        address = hub_address[hub_address.find(": ") + 2 :]
    else:
        address = hub_address[hub_address.find(": ") + 2 : -2]
    config_handler = CURTCommands.config_worker(
        robot_inventor_control_worker, {"hub_address": address}
    )
    success = CURTCommands.get_result(config_handler)["dataValue"]["data"]
    if not success:
        control_initialized = False
        return (
            False,
            "Failed connecting to robot inventor, try restarting the robot inventor hub and run initialize again.",
        )
    control_initialized = True
    return True, "OK"


def deactivate_control():
    global control_initialized
    global pid_controller
    # result = caitCore.send_component_commond("control", "Control Down")
    # if result == False:
    #     logging.info("Deactivate Control: Error occurred")
    #     return result
    control_initialized = False
    pid_controller = None
    return True


def initialize_smarthome():
    global smarthome_initialized
    global reset_all
    while reset_in_progress:
        time.sleep(0.1)
    reset_all = False
    ha_worker = CURTCommands.get_worker(
        full_domain_name + "/smarthome/smarthome_service/ha_provider"
    )
    config_handler = CURTCommands.config_worker(ha_worker, {"token": token})
    success = CURTCommands.get_result(config_handler)["dataValue"]["data"]
    if not success:
        smarthome_initialized = False
        return (
            False,
            "Failed to initialize smart home woker, check the connection with home assistant",
        )
    smarthome_initialized = True
    return True, "OK"


def initialize_pid(kp, ki, kd):
    global pid_controller
    global reset_all
    reset_all = False
    if pid_controller is None:
        pid_controller = PID(kP=kp, kI=ki, kD=kd)
        pid_controller.initialize()
    return True, "OK"


def change_module_parameters(parameter_name, value):
    pass


def get_camera_worker():
    global current_camera
    worker = None
    if current_camera == "oakd":
        worker = CURTCommands.get_worker(
            full_domain_name + "/vision/oakd_service/oakd_rgb_camera_input"
        )
    elif current_camera == "webcam":
        worker = CURTCommands.get_worker(
            full_domain_name + "/vision/vision_input_service/webcam_input"
        )
    elif current_camera == "picam":
        worker = CURTCommands.get_worker(
            full_domain_name + "/vision/vision_input_service/picam_input"
        )
    else:
        logging.warning("Current worker does not fit into any supported category")
    return worker


def get_camera_image(for_streaming=False):
    global current_camera
    global oakd_nodes
    global vision_initialized
    if not vision_initialized:
        logging.info(
            "Please call initialize_vision() function before using the vision module"
        )
        return False, "Vision module is not initialized"
    retry_count = 0
    worker = get_camera_worker()
    while worker is None:
        worker = get_camera_worker()
        retry_count += 1
        if retry_count > 3:
            break

    if worker is None:
        logging.warning("No rgb camera worker found.")
        return False, "No rgb camera worker found."
    rgb_frame_handler = None
    frame = None
    rgb_frame_handler = CURTCommands.request(worker, params=["get_rgb_frame"])
    if rgb_frame_handler is not None:
        frame = CURTCommands.get_result(rgb_frame_handler, for_streaming)["dataValue"][
            "data"
        ]
        if not isinstance(frame, str):
            frame = None
    return frame


def get_stereo_image(for_streaming=False):
    global oakd_nodes
    global vision_initialized
    if not vision_initialized:
        logging.info(
            "Please call initialize_vision() function before using the vision module"
        )
        return None
    worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_stereo_camera_input"
    )
    stereo_frame_handler = None
    frame = None
    if worker is not None:
        stereo_frame_handler = CURTCommands.request(worker, params=["get_stereo_frame"])
    else:
        logging.warning("No stereo camera worker fonund.")
    if stereo_frame_handler is not None:
        frame = CURTCommands.get_result(stereo_frame_handler, for_streaming)[
            "dataValue"
        ]["data"]
        if not isinstance(frame, str):
            frame = None
    return frame


def change_vision_mode(mode):
    global vision_mode
    vision_mode.append(mode)


def enable_drawing_mode(mode, from_web=False):
    global drawing_modes
    drawing_modes[mode] = True


def draw_detected_face(face, from_web=False):
    global drawing_modes
    global user_mode
    if from_web:
        user_mode = "web"
    else:
        user_mode = "code"
    drawing_modes["Face Detection"] = face


def draw_recognized_face(names, coordinates, from_web=False):
    global drawing_modes
    global user_mode
    if from_web:
        user_mode = "web"
    else:
        user_mode = "code"
    drawing_modes["Face Recognition"] = [names, coordinates]


def draw_estimated_emotions(emotions, from_web=False):
    global drawing_modes
    global user_mode
    if from_web:
        user_mode = "web"
    else:
        user_mode = "code"
    drawing_modes["Face Emotions"] = emotions


def draw_estimated_facemesh(facemesh, from_web=False):
    global drawing_modes
    global user_mode
    if from_web:
        user_mode = "web"
    else:
        user_mode = "code"
    drawing_modes["Face Mesh"] = facemesh


def draw_detected_objects(names, coordinates, from_web=False):
    global drawing_modes
    global user_mode
    if from_web:
        user_mode = "web"
    else:
        user_mode = "code"
    drawing_modes["Object Detection"] = [names, coordinates]


def draw_classified_image(names, from_web=False):
    global drawing_modes
    global user_mode
    if from_web:
        user_mode = "web"
    else:
        user_mode = "code"
    drawing_modes["Image Classification"] = names


def draw_estimated_body_landmarks(body_landmarks, from_web=False):
    global drawing_modes
    global user_mode
    if from_web:
        user_mode = "web"
    else:
        user_mode = "code"
    drawing_modes["Pose Landmarks"] = body_landmarks


def draw_estimated_hand_landmarks(hand_landmarks, from_web=False):
    global drawing_modes
    global user_mode
    if from_web:
        user_mode = "web"
    else:
        user_mode = "code"
    drawing_modes["Hand Landmarks"] = hand_landmarks


def detect_face(processor, spatial=False, for_streaming=False):
    global current_camera
    global oakd_nodes
    global vision_initialized
    if not vision_initialized:
        logging.info(
            "Please call initialize_vision() function before using the vision module"
        )
        return None
    change_vision_mode("face_detection")
    camera_worker = None
    worker = None
    logging.warning("Processor:" + str(processor))
    if current_camera == "oakd":
        camera_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/oakd_service/oakd_rgb_camera_input"
        )
    elif current_camera == "webcam":
        camera_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/vision_input_service/webcam_input"
        )
    elif current_camera == "picam":
        camera_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/vision_input_service/picam_input"
        )
    if processor == "oakd":
        worker = CURTCommands.get_worker(
            full_domain_name + "/vision/oakd_service/oakd_face_detection"
        )
    else:
        worker = CURTCommands.get_worker(
            full_domain_name + "/vision/vision_processor_service/face_detection"
        )
    faces = []
    if camera_worker is not None and worker is not None:
        rgb_frame_handler = CURTCommands.request(
            camera_worker, params=["get_rgb_frame"]
        )
        if processor == "oakd":
            if spatial:
                face_detection_handler = CURTCommands.request(
                    worker, params=["get_spatial_face_detections"]
                )
            else:
                if current_camera != "oakd":
                    face_detection_handler = CURTCommands.request(
                        worker, params=["detect_face", 0.6, False, rgb_frame_handler]
                    )
                else:
                    face_detection_handler = CURTCommands.request(
                        worker, params=["detect_face_pipeline", 0.6, False]
                    )
        else:
            face_detection_handler = CURTCommands.request(
                worker, params=[rgb_frame_handler]
            )
        faces = CURTCommands.get_result(face_detection_handler, for_streaming)[
            "dataValue"
        ]["data"]
        width = 640
        height = 360
        if current_camera != "oakd":
            width = 640
            height = 480
        if isinstance(faces, list):
            for face in faces:
                if isinstance(face, list):
                    face[0] = int(face[0] * width)
                    face[1] = int(face[1] * height)
                    face[2] = int(face[2] * width)
                    face[3] = int(face[3] * height)
                elif isinstance(face, dict):
                    bbox = face["face_coordinates"]
                    bbox[0] = int(bbox[0] * width)
                    bbox[1] = int(bbox[1] * height)
                    bbox[2] = int(bbox[2] * width)
                    bbox[3] = int(bbox[3] * height)
        else:
            faces = []
    return faces


def recognize_face(processor, for_streaming=False):
    global oakd_nodes
    global vision_initialized
    if not vision_initialized:
        logging.info(
            "Please call initialize_vision() function before using the vision module"
        )
        return None, []
    names = []
    coordinates = []
    change_vision_mode("face_recognition")
    if current_camera == "oakd":
        camera_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/oakd_service/oakd_rgb_camera_input"
        )
    elif current_camera == "webcam":
        camera_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/vision_input_service/webcam_input"
        )
    elif current_camera == "picam":
        camera_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/vision_input_service/picam_input"
        )
    if processor == "oakd":
        face_detection_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/oakd_service/oakd_face_detection"
        )
        face_recognition_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/oakd_service/oakd_face_recognition"
        )
    else:
        face_detection_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/vision_processor_service/face_detection"
        )
        face_recognition_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/vision_processor_service/face_recognition"
        )

    rgb_frame_handler = None
    if camera_worker is not None:
        rgb_frame_handler = CURTCommands.request(
            camera_worker, params=["get_rgb_frame"]
        )
    else:
        logging.warning("No camera worker available")
        return names, coordinates

    if processor == "oakd":
        if spatial_face_detection:
            face_detection_handler = CURTCommands.request(
                face_detection_worker, params=["get_spatial_face_detections"]
            )
        else:
            if current_camera != "oakd":
                face_detection_handler = CURTCommands.request(
                    face_detection_worker,
                    params=["detect_face", 0.6, False, rgb_frame_handler],
                )
            else:
                face_detection_handler = CURTCommands.request(
                    face_detection_worker, params=["detect_face_pipeline", 0.6, False]
                )
    else:
        face_detection_handler = CURTCommands.request(
            face_detection_worker, params=[rgb_frame_handler]
        )
    if rgb_frame_handler is not None and face_detection_handler is not None:
        face_recognition_handler = CURTCommands.request(
            face_recognition_worker,
            params=[
                "recognize_face",
                rgb_frame_handler,
                face_detection_handler,
            ],
        )
        identities = CURTCommands.get_result(face_recognition_handler, for_streaming)[
            "dataValue"
        ]["data"]
        width = 640
        height = 360
        if current_camera != "oakd":
            width = 640
            height = 480
        if identities is not None:
            # rgb_frame = identities["frame"]
            for name in identities:
                if name != "frame":
                    detection = identities[name]
                    names.append(name)
                    x1 = int(detection[0] * width)
                    y1 = int(detection[1] * height)
                    x2 = int(detection[2] * width)
                    y2 = int(detection[3] * height)
                    coordinates.append([x1, y1, x2, y2])

    return names, coordinates


def add_person(processor, name):
    global oakd_nodes
    global vision_initialized
    if not vision_initialized:
        logging.info(
            "Please call initialize_vision() function before using the vision module"
        )
        return None, []
    change_vision_mode("face_recognition")
    if current_camera == "oakd":
        camera_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/oakd_service/oakd_rgb_camera_input"
        )
    elif current_camera == "webcam":
        camera_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/vision_input_service/webcam_input"
        )
    elif current_camera == "picam":
        camera_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/vision_input_service/picam_input"
        )
    if processor == "oakd":
        face_detection_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/oakd_service/oakd_face_detection"
        )
        face_recognition_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/oakd_service/oakd_face_recognition"
        )
    else:
        face_detection_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/vision_processor_service/face_detection"
        )
        face_recognition_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/vision_processor_service/face_recognition"
        )
    success = False
    while not success:
        rgb_frame_handler = None
        if camera_worker is not None:
            rgb_frame_handler = CURTCommands.request(
                camera_worker, params=["get_rgb_frame"]
            )
        else:
            logging.warning("No camera worker available")
            break
        if processor == "oakd":
            if spatial_face_detection:
                face_detection_handler = CURTCommands.request(
                    face_detection_worker, params=["get_spatial_face_detections"]
                )
            else:
                if current_camera != "oakd":
                    face_detection_handler = CURTCommands.request(
                        face_detection_worker,
                        params=["detect_face", 0.6, False, rgb_frame_handler],
                    )
                else:
                    face_detection_handler = CURTCommands.request(
                        face_detection_worker,
                        params=["detect_face_pipeline", 0.6, False],
                    )
        else:
            face_detection_handler = CURTCommands.request(
                face_detection_worker, params=[rgb_frame_handler]
            )
        if rgb_frame_handler is not None and face_detection_handler is not None:
            face_recognition_handler = CURTCommands.request(
                face_recognition_worker,
                params=["add_person", name, rgb_frame_handler, face_detection_handler],
            )
            success = CURTCommands.get_result(face_recognition_handler)["dataValue"][
                "data"
            ]
    return success


def remove_person(processor, name):
    global oakd_nodes
    global vision_initialized
    if not vision_initialized:
        logging.info(
            "Please call initialize_vision() function before using the vision module"
        )
        return None, []
    change_vision_mode("face_recognition")
    if processor == "oakd":
        face_recognition_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/oakd_service/oakd_face_recognition"
        )
    else:
        face_recognition_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/vision_processor_service/face_recognition"
        )
    success = False
    while not success:
        face_recognition_handler = CURTCommands.request(
            face_recognition_worker,
            params=["remove_person", name],
        )
        success = CURTCommands.get_result(face_recognition_handler)["dataValue"]["data"]
    return success


def detect_objects(processor, spatial=False, for_streaming=False):
    global oakd_nodes
    global vision_initialized
    if not vision_initialized:
        logging.info(
            "Please call initialize_vision() function before using the vision module"
        )
        return None
    change_vision_mode("object_detection")
    if current_camera == "oakd":
        camera_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/oakd_service/oakd_rgb_camera_input"
        )
    elif current_camera == "webcam":
        camera_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/vision_input_service/webcam_input"
        )
    elif current_camera == "picam":
        camera_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/vision_input_service/picam_input"
        )
    if processor == "oakd":
        worker = CURTCommands.get_worker(
            full_domain_name + "/vision/oakd_service/oakd_object_detection"
        )
    else:
        worker = CURTCommands.get_worker(
            full_domain_name + "/vision/vision_processor_service/object_detection"
        )
    coordinates = []
    names = []
    objects = []
    if camera_worker is not None and worker is not None:
        if processor == "oakd":
            if spatial:
                object_detection_handler = CURTCommands.request(
                    worker, params=["get_spatial_object_detections"]
                )
            else:
                if current_camera != "oakd":
                    rgb_frame_handler = CURTCommands.request(
                        camera_worker, params=["get_rgb_frame"]
                    )
                    object_detection_handler = CURTCommands.request(
                        worker, params=["detect_object", rgb_frame_handler]
                    )
                else:
                    object_detection_handler = CURTCommands.request(
                        worker, params=["detect_object_pipeline"]
                    )
        else:
            rgb_frame_handler = CURTCommands.request(
                camera_worker, params=["get_rgb_frame"]
            )
            object_detection_handler = CURTCommands.request(
                worker, params=[rgb_frame_handler]
            )

        objects = CURTCommands.get_result(object_detection_handler, for_streaming)[
            "dataValue"
        ]["data"]
        # logging.warning("Objects: " + str(objects))
        if not isinstance(objects, list):
            objects = []
    width = 640
    height = 360
    if current_camera != "oakd":
        width = 640
        height = 480
    for obj in objects:
        if len(obj) > 5:
            coordinates.append(
                [
                    obj[0] * width,
                    obj[1] * height,
                    obj[2] * width,
                    obj[3] * height,
                    obj[4],
                    obj[5],
                    obj[6],
                ]
            )
        else:
            coordinates.append(
                [obj[0] * width, obj[1] * height, obj[2] * width, obj[3] * height]
            )
        names.append(object_labels[int(obj[-1])])
    return names, coordinates


def classify_image(for_streaming=False):
    global oakd_nodes
    global vision_initialized
    if not vision_initialized:
        logging.info(
            "Please call initialize_vision() function before using the vision module"
        )
        return None
    change_vision_mode("image_classification")
    if current_camera == "oakd":
        camera_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/oakd_service/oakd_rgb_camera_input"
        )
    elif current_camera == "webcam":
        camera_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/vision_input_service/webcam_input"
        )
    elif current_camera == "picam":
        camera_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/vision_input_service/picam_input"
        )
    worker = CURTCommands.get_worker(
        full_domain_name + "/vision/vision_processor_service/image_classification"
    )
    image_classes = []
    if camera_worker is not None and worker is not None:
        rgb_frame_handler = CURTCommands.request(
            camera_worker, params=["get_rgb_frame"]
        )
        image_classification_handler = CURTCommands.request(
            worker, params=[rgb_frame_handler]
        )
        image_classes = CURTCommands.get_result(
            image_classification_handler, for_streaming
        )["dataValue"]["data"]
        if image_classes is None:
            image_classes = []
    return image_classes


def face_emotions_estimation(for_streaming=False):
    global oakd_nodes
    global vision_initialized
    if not vision_initialized:
        logging.info(
            "Please call initialize_vision() function before using the vision module"
        )
        return None
    change_vision_mode("face_emotions")
    if current_camera == "oakd":
        camera_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/oakd_service/oakd_rgb_camera_input"
        )
    elif current_camera == "webcam":
        camera_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/vision_input_service/webcam_input"
        )
    elif current_camera == "picam":
        camera_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/vision_input_service/picam_input"
        )
    face_detection_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_face_detection"
    )
    face_emotions_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_face_emotions"
    )
    if camera_worker is not None:
        rgb_frame_handler = CURTCommands.request(
            camera_worker, params=["get_rgb_frame"]
        )
    else:
        logging.warning("No rgb camera preview node in the pipeline")
    if spatial_face_detection:
        face_detection_handler = CURTCommands.request(
            face_detection_worker, params=["get_spatial_face_detections"]
        )
    else:
        if current_camera != "oakd":
            face_detection_handler = CURTCommands.request(
                face_detection_worker,
                params=["detect_face", 0.6, False, rgb_frame_handler],
            )
        else:
            face_detection_handler = CURTCommands.request(
                face_detection_worker, params=["detect_face_pipeline", 0.6, False]
            )
    emotions = []
    width = 640
    height = 360
    if current_camera != "oakd":
        width = 640
        height = 480
    if rgb_frame_handler is not None and face_detection_handler is not None:
        face_emotions_handler = CURTCommands.request(
            face_emotions_worker,
            params=[rgb_frame_handler, face_detection_handler],
        )
        emotions = CURTCommands.get_result(face_emotions_handler, for_streaming)[
            "dataValue"
        ]["data"]
        if emotions is None:
            return []

        for emotion in emotions:
            raw_emtotions = emotion[0]
            emo = {}
            emo["neutral"] = raw_emtotions[0]
            emo["happy"] = raw_emtotions[1]
            emo["sad"] = raw_emtotions[2]
            emo["surprise"] = raw_emtotions[3]
            emo["anger"] = raw_emtotions[4]
            emotion[0] = emo
            bbox = emotion[1]
            bbox[0] = bbox[0] * width
            bbox[1] = bbox[1] * height
            bbox[2] = bbox[2] * width
            bbox[3] = bbox[3] * height
    return emotions


def facemesh_estimation(for_streaming=False):
    global oakd_nodes
    global vision_initialized
    if not vision_initialized:
        logging.info(
            "Please call initialize_vision() function before using the vision module"
        )
        return None
    change_vision_mode("facemesh")
    if current_camera == "oakd":
        camera_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/oakd_service/oakd_rgb_camera_input"
        )
    elif current_camera == "webcam":
        camera_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/vision_input_service/webcam_input"
        )
    elif current_camera == "picam":
        camera_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/vision_input_service/picam_input"
        )
    face_detection_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_face_detection"
    )
    facemesh_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_facemesh"
    )
    if camera_worker is not None:
        rgb_frame_handler = CURTCommands.request(
            camera_worker, params=["get_rgb_frame"]
        )
    else:
        logging.warning("No rgb camera preview node in the pipeline")
    if spatial_face_detection:
        face_detection_handler = CURTCommands.request(
            face_detection_worker, params=["get_spatial_face_detections"]
        )
    else:
        if current_camera != "oakd":
            face_detection_handler = CURTCommands.request(
                face_detection_worker,
                params=["detect_face", 0.6, False, rgb_frame_handler],
            )
        else:
            face_detection_handler = CURTCommands.request(
                face_detection_worker, params=["detect_face_pipeline", 0.6, False]
            )
    facemeshes = []
    width = 640
    height = 360
    if current_camera != "oakd":
        width = 640
        height = 480
    if rgb_frame_handler is not None and face_detection_handler is not None:
        facemesh_handler = CURTCommands.request(
            facemesh_worker, params=[rgb_frame_handler, face_detection_handler]
        )
        facemeshes = CURTCommands.get_result(facemesh_handler, for_streaming)[
            "dataValue"
        ]["data"]
        if facemeshes is None:
            return []
        for facemesh in facemeshes:
            for pt in facemesh:
                pt[0] = pt[0] * width
                pt[1] = pt[1] * height
    return facemeshes


def get_hand_landmarks(for_streaming=False):
    global oakd_nodes
    global vision_initialized
    if not vision_initialized:
        logging.info(
            "Please call initialize_vision() function before using the vision module"
        )
        return None
    change_vision_mode("hand_landmarks")
    if current_camera == "oakd":
        camera_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/oakd_service/oakd_rgb_camera_input"
        )
    elif current_camera == "webcam":
        camera_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/vision_input_service/webcam_input"
        )
    elif current_camera == "picam":
        camera_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/vision_input_service/picam_input"
        )
    hand_landmarks_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_hand_landmarks"
    )
    if camera_worker is not None:
        rgb_frame_handler = CURTCommands.request(
            camera_worker, params=["get_rgb_frame"]
        )
    else:
        logging.warning("No rgb camera worker found.")
    hand_landmarks_coordinates = []
    hand_bboxes = []
    handnesses = []
    width = 640
    height = 360
    if current_camera != "oakd":
        width = 640
        height = 480
    if rgb_frame_handler is not None:
        hand_landmarks_handler = CURTCommands.request(
            hand_landmarks_worker,
            params=[rgb_frame_handler],
        )
        hand_landmarks = CURTCommands.get_result(hand_landmarks_handler, for_streaming)[
            "dataValue"
        ]["data"]
        if hand_landmarks is None:
            return [], [], []
        for landmarks in hand_landmarks:
            for lm_xy in landmarks[0]:
                lm_xy[0] = lm_xy[0] * width
                lm_xy[1] = lm_xy[1] * height
            hand_landmarks_coordinates.append(landmarks[0])
            landmarks[1][0] = landmarks[1][0] * width
            landmarks[1][1] = landmarks[1][1] * height
            landmarks[1][2] = landmarks[1][2] * width
            landmarks[1][3] = landmarks[1][3] * height
            hand_bboxes.append(landmarks[1])
            handnesses.append(landmarks[2])
    return hand_landmarks_coordinates, hand_bboxes, handnesses


def get_body_landmarks(for_streaming=False):
    global oakd_nodes
    global vision_initialized
    if not vision_initialized:
        logging.info(
            "Please call initialize_vision() function before using the vision module"
        )
        return None
    change_vision_mode("body_landmarks")
    if current_camera == "oakd":
        camera_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/oakd_service/oakd_rgb_camera_input"
        )
    elif current_camera == "webcam":
        camera_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/vision_input_service/webcam_input"
        )
    elif current_camera == "picam":
        camera_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/vision_input_service/picam_input"
        )
    body_landmarks_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_pose_estimation"
    )
    if camera_worker is not None:
        rgb_frame_handler = CURTCommands.request(
            camera_worker, params=["get_rgb_frame"]
        )
    else:
        logging.warning("No rgb camera worker found.")
    body_ladmarks = []
    width = 640
    height = 360
    if current_camera != "oakd":
        width = 640
        height = 480
    if rgb_frame_handler is not None:
        body_landmarks_handler = CURTCommands.request(
            body_landmarks_worker,
            params=[rgb_frame_handler],
        )
        body_ladmarks = CURTCommands.get_result(body_landmarks_handler, for_streaming)[
            "dataValue"
        ]["data"]
        if body_ladmarks is None:
            return []
        for landmarks in body_ladmarks:
            landmarks[0] = landmarks[0] * width
            landmarks[1] = landmarks[1] * height

    return body_ladmarks


def say(message_topic, entities=[]):
    global voice_mode
    message = message_topic
    if not voice_initialized:
        logging.info(
            "Please call initialize_voice() function before using the vision module"
        )
        return False
    voice_input_worker = CURTCommands.get_worker(
        full_domain_name + "/voice/voice_input_service/respeaker_input"
    )
    if voice_mode == "online":
        voice_generation_worker = CURTCommands.get_worker(
            full_domain_name + "/voice/text_to_speech_service/online_voice_generation"
        )
    else:
        voice_generation_worker = CURTCommands.get_worker(
            full_domain_name + "/voice/text_to_speech_service/offline_voice_generation"
        )
    logging.info("say: " + message)
    CURTCommands.request(voice_input_worker, params=["pause"])
    voice_generation_handler = CURTCommands.request(
        voice_generation_worker, params=[message]
    )
    generation_status = CURTCommands.get_result(voice_generation_handler)
    CURTCommands.request(voice_input_worker, params=["resume"])
    return True


def create_file_list(directory_path):
    file_list = [
        f
        for f in os.listdir(directory_path)
        if os.path.isfile(os.path.join(directory_path, f))
    ]
    return file_list


audio_playing = False
current_audio_file = ""


def play_audio_func():
    global audio_playing
    global current_audio_file
    previous_audio_file = ""
    while True:
        if previous_audio_file != current_audio_file:
            if not audio_playing:
                audio_playing = True
                previous_audio_file = current_audio_file
                out = os.system("aplay " + current_audio_file)
                audio_playing = False
        else:
            time.sleep(0.001)


# play_audio_thread = threading.Thread(target=play_audio_func, daemon=True)
# play_audio_thread.start()


def play_audio(file_path):
    global audio_playing
    global current_audio_file
    if not audio_playing:
        audio_playing = True
        out = os.system("aplay " + file_path)
        audio_playing = False
        # current_audio_file = file_path
    return True


def listen():
    global voice_mode
    global use_respeaker
    voice_input_worker = None
    if use_respeaker:
        voice_input_worker = CURTCommands.get_worker(
            full_domain_name + "/voice/voice_input_service/respeaker_input"
        )
    else:
        voice_input_worker = CURTCommands.get_worker(
            full_domain_name + "/voice/voice_input_service/live_input"
        )
    if voice_mode == "online":
        voice_generation_worker = CURTCommands.get_worker(
            full_domain_name + "/voice/text_to_speech_service/online_voice_generation"
        )
    else:
        voice_generation_worker = CURTCommands.get_worker(
            full_domain_name + "/voice/text_to_speech_service/offline_voice_generation"
        )
    # CURTCommands.request(voice_input_worker, params=["pause"])
    voice_generation_handler = CURTCommands.request(
        voice_generation_worker, params=["notification_tone"]
    )
    generation_status = CURTCommands.get_result(voice_generation_handler)
    time.sleep(0.1)
    # CURTCommands.request(voice_input_worker, params=["resume"])
    time.sleep(0.05)
    speech = ""
    while speech == "":
        if reset_all:
            return
        voice_handler = CURTCommands.request(voice_input_worker, params=["get"])
        voice_processing_worker = None
        if voice_mode == "online":
            voice_processing_worker = CURTCommands.get_worker(
                full_domain_name
                + "/voice/speech_to_text_service/online_voice_processing"
            )
        else:
            voice_processing_worker = CURTCommands.get_worker(
                full_domain_name
                + "/voice/speech_to_text_service/offline_voice_processing"
            )
        voice_processing_handler = CURTCommands.request(
            voice_processing_worker, params=[voice_handler]
        )
        speech_result = CURTCommands.get_result(voice_processing_handler)
        if speech_result is not None:
            speech = speech_result["dataValue"]["data"]
            if speech is None:
                speech = ""
        time.sleep(0.1)
    return True, speech


def analyze(user_message):
    if not nlp_initialized:
        logging.info(
            "Please call initialize_nlp() function before using the vision module"
        )
        return "", "", ""
    rasa_intent_worker = CURTCommands.get_worker(
        full_domain_name + "/nlp/nlp_intent_classify_service/rasa_intent_classifier"
    )
    # get_rasa_intent_services()[0]

    nlp_intent_handler = CURTCommands.request(rasa_intent_worker, params=[user_message])
    nlp_intent = CURTCommands.get_result(nlp_intent_handler)["dataValue"]["data"]
    nlp_response = json.loads(nlp_intent)
    topic = nlp_response["topic"]
    condifence = nlp_response["confidence"]
    extracted_entities = nlp_response["entities"]
    entities = []
    for entity in extracted_entities:
        entity_entry = {
            "entity_name": entity["entity"],
            "entity_value": entity["value"],
        }
        entry_is_uniqued = True
        for e in entities:
            if (
                entity_entry["entity_name"] == e["entity_name"]
                and entity_entry["entity_value"] == e["entity_value"]
            ):
                entry_is_uniqued = False
        if entry_is_uniqued:
            entities.append(entity_entry)
    return topic, condifence, entities


def control_motor(hub_name, motor_name, speed, duration):
    global oakd_nodes
    global control_initialized
    if not control_initialized:
        logging.info(
            "Please call initialize_control() function before using the vision module"
        )
        return False, "Not initialized"
    control_worker = CURTCommands.get_worker(
        full_domain_name + "/control/control_service/robot_inventor_control"
    )
    motor = motor_name[-1]
    control_params = {
        "control_type": "motor",
        "operation": {
            "motor_arrangement": "individual",
            "motor": motor,
            "motion": "speed",
            "speed": speed,
        },
    }
    control_handler = CURTCommands.request(control_worker, params=[control_params])
    start_time = time.monotonic()
    while (time.monotonic() - start_time) < float(duration):
        time.sleep(0.01)
    control_params = {
        "control_type": "motor",
        "operation": {
            "motor_arrangement": "individual",
            "motor": motor,
            "motion": "brake",
        },
    }
    control_handler = CURTCommands.request(control_worker, params=[control_params])
    return True, "OK"


def set_motor_position(hub_name, motor_name, position):
    global oakd_nodes
    global control_initialized
    if not control_initialized:
        logging.info(
            "Please call initialize_control() function before using the vision module"
        )
        return False, "Not initialized"
    control_worker = CURTCommands.get_worker(
        full_domain_name + "/control/control_service/robot_inventor_control"
    )
    motor = motor_name[-1]
    control_params = {
        "control_type": "motor",
        "operation": {
            "motor_arrangement": "individual",
            "motor": motor,
            "motion": "rotate_to_position",
            "position": int(position),
            "speed": 70,
        },
    }
    control_handler = CURTCommands.request(control_worker, params=[control_params])
    time.sleep(1)
    return True, "OK"


def set_motor_power(hub_name, motor_name, power):
    global oakd_nodes
    global control_initialized
    if not control_initialized:
        logging.info(
            "Please call initialize_control() function before using the vision module"
        )
        return False, "Not initialized"
    control_worker = CURTCommands.get_worker(
        full_domain_name + "/control/control_service/robot_inventor_control"
    )
    motor = motor_name[-1]
    control_params = {
        "control_type": "motor",
        "operation": {
            "motor_arrangement": "individual",
            "motor": motor,
            "motion": "speed",
            "speed": int(power),
        },
    }
    control_handler = CURTCommands.request(control_worker, params=[control_params])
    time.sleep(0.05)
    return True, "OK"


def rotate_motor(hub_name, motor_name, angle):
    global oakd_nodes
    global control_initialized
    if not control_initialized:
        logging.info(
            "Please call initialize_control() function before using the vision module"
        )
        return False, "Not initialized"
    control_worker = CURTCommands.get_worker(
        full_domain_name + "/control/control_service/robot_inventor_control"
    )
    motor = motor_name[-1]
    speed = 70
    if int(angle) < 0:
        speed = -70
    control_params = {
        "control_type": "motor",
        "operation": {
            "motor_arrangement": "individual",
            "motor": motor,
            "motion": "rotate_on_degrees",
            "degrees": int(angle),
            "speed": speed,
        },
    }
    control_handler = CURTCommands.request(control_worker, params=[control_params])
    time.sleep(0.1)
    return True, "OK"


def control_motor_group(operation_list):
    global oakd_nodes
    global control_initialized
    if not control_initialized:
        logging.info(
            "Please call initialize_control() function before using the vision module"
        )
        return False, "Not initialized"
    control_worker = CURTCommands.get_worker(
        full_domain_name + "/control/control_service/robot_inventor_control"
    )
    motor_list = []
    duration_list = []
    largest_duration = 0
    largest_angle = 0
    op_list = json.loads(operation_list)["operation_list"]
    for operation in op_list:
        motor_name = operation["motor_name"]
        motor = motor_name[-1]
        if "speed" in operation:
            motor_list.append(motor)
            speed = int(operation["speed"])
            duration = float(operation["duration"])
            if duration > largest_duration:
                largest_duration = duration
            duration_list.append(duration)
            control_params = {
                "control_type": "motor",
                "operation": {
                    "motor_arrangement": "individual",
                    "motor": motor,
                    "motion": "speed",
                    "speed": int(speed),
                },
            }
            control_handler = CURTCommands.request(
                control_worker, params=[control_params]
            )
        elif "angle" in operation:
            motor_list.append(motor)
            angle = int(operation["angle"])
            if abs(angle) > largest_angle:
                largest_angle = abs(angle)
            speed = 70
            if int(angle) < 0:
                speed = -70
            control_params = {
                "control_type": "motor",
                "operation": {
                    "motor_arrangement": "individual",
                    "motor": motor,
                    "motion": "rotate_on_degrees",
                    "degrees": int(angle),
                    "speed": speed,
                },
            }
            control_handler = CURTCommands.request(
                control_worker, params=[control_params]
            )
        elif "position" in operation:
            position = int(operation["position"])
            if abs(position) > largest_angle:
                largest_angle = abs(position)
            control_params = {
                "control_type": "motor",
                "operation": {
                    "motor_arrangement": "individual",
                    "motor": motor,
                    "motion": "rotate_to_position",
                    "position": int(position),
                    "speed": 70,
                },
            }
            control_handler = CURTCommands.request(
                control_worker, params=[control_params]
            )
        elif "power" in operation:
            power = int(operation["power"])
            if power != 0:
                control_params = {
                    "control_type": "motor",
                    "operation": {
                        "motor_arrangement": "individual",
                        "motor": motor,
                        "motion": "speed",
                        "speed": int(power),
                    },
                }
                CURTCommands.request(control_worker, params=[control_params])
            else:
                control_params = {
                    "control_type": "motor",
                    "operation": {
                        "motor_arrangement": "individual",
                        "motor": motor,
                        "motion": "brake",
                    },
                }
                CURTCommands.request(control_worker, params=[control_params])
    if largest_angle > 800:
        if largest_duration < 2:
            largest_duration = 2
    else:
        largest_duration = 1.2
    start_time = time.monotonic()
    while time.monotonic() - start_time < largest_duration:
        remaining_duration_list = []
        for i in range(0, len(duration_list)):
            if time.monotonic() - start_time >= duration_list[i]:
                control_params = {
                    "control_type": "motor",
                    "operation": {
                        "motor_arrangement": "individual",
                        "motor": motor_list[i],
                        "motion": "brake",
                    },
                }
                CURTCommands.request(control_worker, params=[control_params])
            else:
                remaining_duration_list.append(duration_list[i])
        duration_list = remaining_duration_list
        time.sleep(0.1)
    for m in range(0, len(motor_list)):
        control_params = {
            "control_type": "motor",
            "operation": {
                "motor_arrangement": "individual",
                "motor": motor_list[m],
                "motion": "brake",
            },
        }
        CURTCommands.request(control_worker, params=[control_params])
    time.sleep(0.003)
    return True, "OK"


def stop_all_motors():
    global oakd_nodes
    global control_initialized
    if not control_initialized:
        logging.info(
            "Please call initialize_control() function before using the vision module"
        )
        return False
    control_worker = CURTCommands.get_worker(
        full_domain_name + "/control/control_service/robot_inventor_control"
    )
    motors = ["A", "B", "C", "D", "E", "F"]
    for motor in motors:
        control_params = {
            "control_type": "motor",
            "operation": {
                "motor_arrangement": "individual",
                "motor": motor,
                "motion": "brake",
            },
        }
        CURTCommands.request(control_worker, params=[control_params])
    return True


def update_pid(error):
    global pid_controller
    if pid_controller is not None:
        value = int(pid_controller.update(error))
        return value
    else:
        return 0


def get_devices(device_type):
    ha_worker = CURTCommands.get_worker(
        full_domain_name + "/smarthome/smarthome_service/ha_provider"
    )
    if ha_worker is None:
        return []
    config_handler = CURTCommands.config_worker(ha_worker, {"token": token})
    success = CURTCommands.get_result(config_handler)["dataValue"]["data"]
    if not success:
        return []
    smarthome_params = {"control_type": "get_devices", "parameter": device_type}
    smarthome_handler = CURTCommands.request(ha_worker, params=[smarthome_params])
    devices = CURTCommands.get_result(smarthome_handler)["dataValue"]["data"]
    return devices


def control_light(device_name, operation, parameter=None):
    global smarthome_initialized
    if not smarthome_initialized:
        logging.info(
            "Please call initialize_smarthome() function before using the smarthome module"
        )
        return False
    ha_worker = CURTCommands.get_worker(
        full_domain_name + "/smarthome/smarthome_service/ha_provider"
    )
    smarthome_params = {
        "control_type": "light",
        "device_name": device_name,
        "operation": operation,
        "parameter": parameter,
    }
    smarthome_handler = CURTCommands.request(ha_worker, params=[smarthome_params])
    result = CURTCommands.get_result(smarthome_handler)["dataValue"]["data"]
    return result


def control_media_player(device_name, operation):
    global smarthome_initialized
    if not smarthome_initialized:
        logging.info(
            "Please call initialize_smarthome() function before using the smarthome module"
        )
        return False
    ha_worker = CURTCommands.get_worker(
        full_domain_name + "/smarthome/smarthome_service/ha_provider"
    )
    smarthome_params = {
        "control_type": "media_player",
        "device_name": device_name,
        "operation": operation,
    }
    smarthome_handler = CURTCommands.request(ha_worker, params=[smarthome_params])
    result = CURTCommands.get_result(smarthome_handler)["dataValue"]["data"]
    return result


def streaming_func():
    global streaming_client
    global streaming_channel
    global vision_initialized
    global vision_mode
    global drawing_modes
    global camera_img
    global user_mode
    try:
        while True:
            if vision_initialized:
                img = None
                if drawing_modes["Depth Mode"]:
                    img = get_stereo_image(for_streaming=True)
                else:
                    img = get_camera_image(for_streaming=True)
                if img is not None:
                    camera_img = decode_image_byte(img)
                    if drawing_modes["Face Detection"] != []:
                        camera_img = draw_face_detection(
                            camera_img, drawing_modes["Face Detection"]
                        )
                    if drawing_modes["Face Recognition"] != []:
                        camera_img = draw_face_recognition(
                            camera_img,
                            drawing_modes["Face Recognition"][0],
                            drawing_modes["Face Recognition"][1],
                        )
                    if drawing_modes["Face Emotions"] != []:
                        camera_img = draw_face_emotions(
                            camera_img, drawing_modes["Face Emotions"]
                        )
                    if drawing_modes["Face Mesh"] != []:
                        camera_img = draw_facemesh(
                            camera_img, drawing_modes["Face Mesh"]
                        )
                    if drawing_modes["Object Detection"] != []:
                        camera_img = draw_object_detection(
                            camera_img,
                            drawing_modes["Object Detection"][0],
                            drawing_modes["Object Detection"][1],
                        )
                    if drawing_modes["Image Classification"] != []:
                        camera_img = draw_image_classification(
                            camera_img, drawing_modes["Image Classification"]
                        )
                    if drawing_modes["Pose Landmarks"] != []:
                        camera_img = draw_body_landmarks(
                            camera_img, drawing_modes["Pose Landmarks"]
                        )
                    if drawing_modes["Hand Landmarks"] != []:
                        camera_img = draw_hand_landmarks(
                            camera_img, drawing_modes["Hand Landmarks"]
                        )
                    if user_mode == "web":
                        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
                        _, buffer = cv2.imencode(".jpg", camera_img, encode_param)
                        imgByteArr = base64.b64encode(buffer)
                        streaming_client.publish(streaming_channel, imgByteArr)
                    else:
                        cv2.imshow("Camera feed", camera_img)
                        cv2.waitKey(1)
            else:
                print("Stream thread exiting")
                break
    except Exception as e:
        logging.warning(
            "***************STREAMING THREAD EXCEPTION:*************************"
        )
        logging.warning(str(e))
        logging.warning(
            "*******************************************************************"
        )


def reset_modules():
    global reset_all
    global reset_in_progress
    global vision_initialized
    global voice_initialized
    global nlp_initialized
    global control_initialized
    global smarthome_initialized
    global vision_mode
    global current_camera
    global stream_thread
    global pid_controller
    global drawing_modes
    global spatial_face_detection
    global spatial_object_detection
    # logging.warning("------------RESETTING MODULES-------------")
    reset_in_progress = True
    reset_all = True
    vision_initialized = False
    spatial_face_detection = False
    spatial_object_detection = False
    voice_initialized = False
    nlp_initialized = False
    if control_initialized:
        stop_all_motors()
    control_initialized = False
    smarthome_initialized = False
    vision_mode = []
    pid_controller = None
    if stream_thread is not None:
        stream_thread.join()
    drawing_modes = {
        "Depth Mode": False,
        "Face Detection": [],
        "Face Recognition": [],
        "Face Emotions": [],
        "Face Mesh": [],
        "Object Detection": [],
        "Image Classification": [],
        "Hand Landmarks": [],
        "Pose Landmarks": [],
    }
    video_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_pipeline"
    )
    if video_worker is not None:
        config_handler = CURTCommands.config_worker(
            video_worker,
            [["reset"]],
        )
        success = CURTCommands.get_result(config_handler)["dataValue"]["data"]
    video_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/vision_input_service/webcam_input"
    )
    if video_worker is not None:
        config_handler = CURTCommands.config_worker(
            video_worker,
            {"reset": True},
        )
        success = CURTCommands.get_result(config_handler)["dataValue"]["data"]
    video_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/vision_input_service/picam_input"
    )
    if video_worker is not None:
        config_handler = CURTCommands.config_worker(
            video_worker,
            {"reset": True},
        )
        success = CURTCommands.get_result(config_handler)["dataValue"]["data"]
    current_camera = ""

    webcam_microphone_worker = CURTCommands.get_worker(
        full_domain_name + "/voice/voice_input_service/live_input"
    )
    if webcam_microphone_worker is not None:
        voice_handler = CURTCommands.request(
            webcam_microphone_worker, params=["release"]
        )
        success = CURTCommands.get_result(voice_handler)["dataValue"]["data"]

    respeaker_worker = CURTCommands.get_worker(
        full_domain_name + "/voice/voice_input_service/respeaker_input"
    )
    if respeaker_worker is not None:
        voice_handler = CURTCommands.request(respeaker_worker, params=["release"])
        success = CURTCommands.get_result(voice_handler)["dataValue"]["data"]
    reset_in_progress = False
    return True


logging.warning("*********Core imported*********")

if __name__ == "__main__":
    pass
