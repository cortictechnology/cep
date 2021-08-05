""" 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, December 2019

"""

from curt.command import CURTCommands
import paho.mqtt.client as mqtt
import logging
import time
import json
import os
import socket
import requests
import base64
import threading
import numpy as np
import cv2
from .managers.device_manager import DeviceManager
from .PID import PID
from .core_data import *
from .utils import (
    connect_mqtt,
    decode_image_byte,
    draw_face_detection,
    draw_face_recognition,
    draw_object_detection,
    draw_face_emotions,
    draw_facemesh,
    draw_body_landmarks,
    draw_hand_landmarks,
)

camera_img = None

full_domain_name = socket.getfqdn()

device_manager = DeviceManager()

logging.getLogger().setLevel(logging.WARNING)

broker_address = CURTCommands.initialize()

streaming_channel = "cait/output/" + os.uname()[1].lower() + "/displayFrame"
streaming_client = mqtt.Client()
ret = connect_mqtt(streaming_client, broker_address)
while ret != True:
    time.sleep(1)
    ret = connect_mqtt(streaming_client, broker_address)


def get_video_devices():
    all_vision_input = CURTCommands.get_vision_input_services()
    camera_workers = []
    for vision_input in all_vision_input:
        if vision_input.name == "webcam" or vision_input.name == "picam_input":
            camera_workers.append(vision_input)
    return camera_workers


def get_audio_devices():
    voice_inputs = []
    all_voice_input_services = CURTCommands.get_voice_input_services()
    for voice_input in all_voice_input_services:
        if voice_input.name == "live_input":
            voice_inputs.append(voice_input)
    return voice_inputs


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


def test_camera(index):
    pass


def initialize_vision(processor="local", mode=[], from_web=False):
    global oakd_nodes
    global vision_initialized
    global stream_thread
    global drawing_modes
    global preview_width
    global preview_height
    global spatial_face_detection
    global spatial_object_detection
    global user_mode
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
        # available_video_devices = CURTCommands.get_oakd_services("oakd_pipeline")
        current_video_device = CURTCommands.get_worker(
            full_domain_name + "/vision/oakd_service/oakd_pipeline"
        )
    else:
        available_video_devices = get_video_devices()
        if len(available_video_devices) != 0:
            current_video_device = available_video_devices[0]
    if current_video_device is None:
        return (
            False,
            "No video device is detected, or connected device is not supported",
        )

    if processor == "oakd":
        for node in mode:
            if node[0] == "add_rgb_cam_node":
                preview_width = node[1]
                preview_height = node[2]
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

        CURTCommands.config_worker(current_video_device, mode)
    else:
        # Selecting a VGA resolution, future work should provide a list of selected resolution
        CURTCommands.config_worker(
            current_video_device,
            {"camera_index": 0, "capture_width": 640, "capture_height": 480},
        )
    drawing_modes = {
        "Depth Mode": False,
        "Face Detection": [],
        "Face Recognition": [],
        "Face Emotions": [],
        "Face Mesh": [],
        "Object Detection": [],
        "Hand Landmarks": [],
        "Pose Landmarks": [],
    }
    time.sleep(10)
    vision_initialized = True
    stream_thread = threading.Thread(target=streaming_func, daemon=True)
    stream_thread.start()
    logging.info("***********Streaming preview thread started***********")
    return True, "OK"


def deactivate_vision():
    global vision_initialized
    global vision_mode
    vision_initialized = False
    vision_mode = []
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


def initialize_voice(mode="online", account="default", language="english"):
    global voice_initialized
    global voice_mode
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
    voice_input_worker = CURTCommands.get_worker(
        full_domain_name + "/voice/voice_input_service/respeaker_input"
    )
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
    CURTCommands.config_worker(voice_input_worker, {"audio_in_index": 0})
    time.sleep(0.5)
    CURTCommands.request(voice_input_worker, params=["start"])
    # CURTCommands.start_voice_recording(voice_input_worker)
    if mode == "online":
        curt_path = os.getenv("CURT_PATH")
        account_file = cloud_accounts[account]
        with open(curt_path + "models/modules/voice/" + account_file) as f:
            account_info = json.load(f)
        CURTCommands.config_worker(
            voice_processing_worker,
            {
                "account_crediential": account_info,
                "language": processing_language,
                "sample_rate": 16000,
                "channel_count": 4,
            },
        )
        CURTCommands.config_worker(
            voice_generation_worker,
            {"language": generation_language, "accents": generation_accents},
        )
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
    robot_inventor_control_worker = CURTCommands.get_worker(
        full_domain_name + "/control/control_service/robot_inventor_control"
    )
    if robot_inventor_control_worker is None:
        return False, "No control worker available"
    address = hub_address[hub_address.find(": ") + 2 : -2]
    config_handler = CURTCommands.config_worker(
        robot_inventor_control_worker, {"hub_address": address}
    )
    print({"hub_address": address})
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


def initialize_pid(kp, ki, kd):
    global pid_controller
    if pid_controller is None:
        pid_controller = PID(kP=kp, kI=ki, kD=kd)
        pid_controller.initialize()
    return True, "OK"


def change_module_parameters(parameter_name, value):
    pass


def get_camera_image(for_streaming=False):
    global oakd_nodes
    global vision_initialized
    if not vision_initialized:
        logging.info(
            "Please call initialize_vision() function before using the vision module"
        )
        return None
    worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_rgb_camera_input"
    )
    rgb_frame_handler = None
    frame = None
    if worker is not None:
        rgb_frame_handler = CURTCommands.request(worker, params=["get_rgb_frame"])
    else:
        logging.warning("No rgb camera worker found.")
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
    global user_mode
    if from_web:
        user_mode = "web"
    else:
        user_mode = "code"
    drawing_modes["Face Detection"] = face


def draw_recognized_face(names, coordinates, from_web=False):
    global user_mode
    if from_web:
        user_mode = "web"
    else:
        user_mode = "code"
    drawing_modes["Face Recognition"] = [names, coordinates]


def draw_estimated_emotions(emotions, from_web=False):
    global user_mode
    if from_web:
        user_mode = "web"
    else:
        user_mode = "code"
    drawing_modes["Face Emotions"] = emotions


def draw_estimated_facemesh(facemesh, from_web=False):
    global user_mode
    if from_web:
        user_mode = "web"
    else:
        user_mode = "code"
    drawing_modes["Face Mesh"] = facemesh


def draw_detected_objects(names, coordinates, from_web=False):
    global user_mode
    if from_web:
        user_mode = "web"
    else:
        user_mode = "code"
    drawing_modes["Object Detection"] = [names, coordinates]


def draw_estimated_body_landmarks(body_landmarks, from_web=False):
    global user_mode
    if from_web:
        user_mode = "web"
    else:
        user_mode = "code"
    drawing_modes["Pose Landmarks"] = body_landmarks


def draw_estimated_hand_landmarks(hand_landmarks, from_web=False):
    global user_mode
    if from_web:
        user_mode = "web"
    else:
        user_mode = "code"
    drawing_modes["Hand Landmarks"] = hand_landmarks


def detect_face(processor="oakd", spatial=False, for_streaming=False):
    global oakd_nodes
    global vision_initialized
    if not vision_initialized:
        logging.info(
            "Please call initialize_vision() function before using the vision module"
        )
        return None
    change_vision_mode("face_detection")
    if processor == "oakd":
        worker = CURTCommands.get_worker(
            full_domain_name + "/vision/oakd_service/oakd_face_detection"
        )
    else:
        camera_worker = CURTCommands.get_worker(
            full_domain_name + "/vision/oakd_service/oakd_rgb_camera_input"
        )
        worker = CURTCommands.get_worker(
            full_domain_name + "/vision/vision_processor_service/face_detection"
        )
    faces = []
    if worker is not None:
        if processor == "oakd":
            if spatial:
                face_detection_handler = CURTCommands.request(
                    worker, params=["get_spatial_face_detections"]
                )
            else:
                face_detection_handler = CURTCommands.request(
                    worker, params=["detect_face_pipeline", 0.6, False]
                )
        else:
            rgb_frame_handler = CURTCommands.request(
                camera_worker, params=["get_rgb_frame"]
            )
            face_detection_handler = CURTCommands.request(
                worker, params=[rgb_frame_handler]
            )
        faces = CURTCommands.get_result(face_detection_handler, for_streaming)[
            "dataValue"
        ]["data"]
        if isinstance(faces, list):
            for face in faces:
                if isinstance(face, list):
                    face[0] = int(face[0] * 640)
                    face[1] = int(face[1] * 360)
                    face[2] = int(face[2] * 640)
                    face[3] = int(face[3] * 360)
                elif isinstance(face, dict):
                    bbox = face["face_coordinates"]
                    bbox[0] = int(bbox[0] * 640)
                    bbox[1] = int(bbox[1] * 360)
                    bbox[2] = int(bbox[2] * 640)
                    bbox[3] = int(bbox[3] * 360)
        else:
            faces = []
    return faces


def recognize_face(for_streaming=False):
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
    camera_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_rgb_camera_input"
    )
    face_detection_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_face_detection"
    )
    face_recognition_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_face_recognition"
    )
    rgb_frame_handler = None
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
        face_detection_handler = CURTCommands.request(
            face_detection_worker, params=["detect_face_pipeline", 0.6, False]
        )
    if rgb_frame_handler is not None and face_detection_handler is not None:
        face_recognition_handler = CURTCommands.request(
            face_recognition_worker,
            params=[
                rgb_frame_handler,
                face_detection_handler,
                "recognize_face",
            ],
        )
        identities = CURTCommands.get_result(face_recognition_handler, for_streaming)[
            "dataValue"
        ]["data"]
        if identities is not None:
            # rgb_frame = identities["frame"]
            for name in identities:
                if name != "frame":
                    detection = identities[name]
                    names.append(name)
                    x1 = int(detection[0] * 640)
                    y1 = int(detection[1] * 360)
                    x2 = int(detection[2] * 640)
                    y2 = int(detection[3] * 360)
                    coordinates.append([x1, y1, x2, y2])

    return names, coordinates


def add_person(name):
    global oakd_nodes
    global vision_initialized
    if not vision_initialized:
        logging.info(
            "Please call initialize_vision() function before using the vision module"
        )
        return None, []
    change_vision_mode("face_recognition")
    camera_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_rgb_camera_input"
    )
    face_detection_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_face_detection"
    )
    face_recognition_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_face_recognition"
    )
    success = False
    while not success:
        rgb_frame_handler = None
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
            face_detection_handler = CURTCommands.request(
                face_detection_worker, params=["detect_face_pipeline", 0.6, False]
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


def remove_person(name):
    global oakd_nodes
    global vision_initialized
    if not vision_initialized:
        logging.info(
            "Please call initialize_vision() function before using the vision module"
        )
        return None, []
    change_vision_mode("face_recognition")
    face_recognition_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_face_recognition"
    )
    success = False
    while not success:
        face_recognition_handler = CURTCommands.request(
            face_recognition_worker,
            params=["remove_person", name],
        )
        success = CURTCommands.get_result(face_recognition_handler)["dataValue"]["data"]
    return success


def detect_objects(spatial=False, for_streaming=False):
    global oakd_nodes
    global vision_initialized
    if not vision_initialized:
        logging.info(
            "Please call initialize_vision() function before using the vision module"
        )
        return None
    change_vision_mode("object_detection")
    worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_object_detection"
    )
    coordinates = []
    names = []
    objects = []
    if worker is not None:
        if spatial:
            object_detection_handler = CURTCommands.request(
                worker, params=["get_spatial_object_detections"]
            )
        else:
            object_detection_handler = CURTCommands.request(
                worker, params=["detect_object_pipeline"]
            )
        objects = CURTCommands.get_result(object_detection_handler, for_streaming)[
            "dataValue"
        ]["data"]
        if not isinstance(objects, list):
            objects = []
    for object in objects:
        if len(object) > 4:
            coordinates.append(
                [
                    object[0] * 640,
                    object[1] * 360,
                    object[2] * 640,
                    object[3] * 360,
                    object[4],
                    object[5],
                    object[6],
                ]
            )
        else:
            coordinates.append(
                [object[0] * 640, object[1] * 360, object[2] * 640, object[3] * 360]
            )
        names.append(object_labels[object[-1]])
    return names, coordinates


def face_emotions_estimation(for_streaming=False):
    global oakd_nodes
    global vision_initialized
    if not vision_initialized:
        logging.info(
            "Please call initialize_vision() function before using the vision module"
        )
        return None
    change_vision_mode("face_emotions")
    camera_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_rgb_camera_input"
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
        face_detection_handler = CURTCommands.request(
            face_detection_worker, params=["detect_face_pipeline", 0.6, False]
        )
    emotions = []
    if rgb_frame_handler is not None and face_detection_handler is not None:
        face_emotions_handler = CURTCommands.request(
            face_emotions_worker,
            params=[rgb_frame_handler, face_detection_handler],
        )
        emotions = CURTCommands.get_result(face_emotions_handler, for_streaming)[
            "dataValue"
        ]["data"]
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
            bbox[0] = bbox[0] * 640
            bbox[1] = bbox[1] * 360
            bbox[2] = bbox[2] * 640
            bbox[3] = bbox[3] * 360
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
    camera_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_rgb_camera_input"
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
        face_detection_handler = CURTCommands.request(
            face_detection_worker, params=["detect_face_pipeline", 0.6, False]
        )
    facemeshes = []
    if rgb_frame_handler is not None and face_detection_handler is not None:
        facemesh_handler = CURTCommands.request(
            facemesh_worker, params=[rgb_frame_handler, face_detection_handler]
        )
        facemeshes = CURTCommands.get_result(facemesh_handler, for_streaming)[
            "dataValue"
        ]["data"]
        for facemesh in facemeshes:
            for pt in facemesh:
                pt[0] = pt[0] * 640
                pt[1] = pt[1] * 360
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
    camera_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_rgb_camera_input"
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
    if rgb_frame_handler is not None:
        hand_landmarks_handler = CURTCommands.request(
            hand_landmarks_worker,
            params=[rgb_frame_handler],
        )
        hand_ladmarks = CURTCommands.get_result(hand_landmarks_handler, for_streaming)[
            "dataValue"
        ]["data"]
        for landmarks in hand_ladmarks:
            for lm_xy in landmarks[0]:
                lm_xy[0] = lm_xy[0] * 640
                lm_xy[1] = lm_xy[1] * 360
            hand_landmarks_coordinates.append(landmarks[0])
            landmarks[1][0] = landmarks[1][0] * 640
            landmarks[1][1] = landmarks[1][1] * 360
            landmarks[1][2] = landmarks[1][2] * 640
            landmarks[1][3] = landmarks[1][3] * 360
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
    camera_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_rgb_camera_input"
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
    if rgb_frame_handler is not None:
        body_landmarks_handler = CURTCommands.request(
            body_landmarks_worker,
            params=[rgb_frame_handler],
        )
        body_ladmarks = CURTCommands.get_result(body_landmarks_handler, for_streaming)[
            "dataValue"
        ]["data"]
        for landmarks in body_ladmarks:
            landmarks[0] = landmarks[0] * 640
            landmarks[1] = landmarks[1] * 360

    return body_ladmarks


def classify_image():
    return []


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


def listen():
    global voice_mode
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
    CURTCommands.request(voice_input_worker, params=["pause"])
    voice_generation_handler = CURTCommands.request(
        voice_generation_worker, params=["notification_tone"]
    )
    generation_status = CURTCommands.get_result(voice_generation_handler)
    time.sleep(0.1)
    CURTCommands.request(voice_input_worker, params=["resume"])
    time.sleep(0.05)
    speech = ""
    while speech == "":
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
    time.sleep(0.1)
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
        return False, "Not initialized"
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


def update_pid(error):
    global pid_controller
    if pid_controller is not None:
        return int(pid_controller.update(error))
    else:
        return 0


def get_devices(device_type):
    url = "http://0.0.0.0:8123/api/states"
    response = requests.request("GET", url, headers=headers)
    response_data = response.json()

    device_names = []

    for state in response_data:
        if state["entity_id"].find(device_type + ".") != -1:
            detail_url = "http://0.0.0.0:8123/api/states/" + state["entity_id"]
            detail_response = requests.request(
                "GET", detail_url, headers=headers
            ).json()
            if detail_response["state"] != "unavailable":
                name = state["entity_id"][state["entity_id"].find(".") + 1 :]
                device_names.append(name)
    return device_names


def control_light(device_name, operation, parameter=None):
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
    response = requests.request("POST", url, headers=headers, data=json.dumps(data))
    return response.json()


def control_media_player(device_name, operation):
    url = "http://0.0.0.0:8123/api/services/media_player/" + operation
    data = {"entity_id": device_name}
    response = requests.request("POST", url, headers=headers, data=json.dumps(data))
    return response.json()


def streaming_func():
    global streaming_client
    global streaming_channel
    global vision_initialized
    global vision_mode
    global drawing_modes
    global camera_img
    global user_mode
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
                    camera_img = draw_facemesh(camera_img, drawing_modes["Face Mesh"])
                if drawing_modes["Object Detection"] != []:
                    camera_img = draw_object_detection(
                        camera_img,
                        drawing_modes["Object Detection"][0],
                        drawing_modes["Object Detection"][1],
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


def reset_modules():
    global vision_initialized
    global voice_initialized
    global nlp_initialized
    global control_initialized
    global smarthome_initialized
    global vision_mode
    global stream_thread
    global pid_controller
    global drawing_modes
    global spatial_face_detection
    global spatial_object_detection
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
        "Hand Landmarks": [],
        "Pose Landmarks": [],
    }
    return True


if __name__ == "__main__":
    pass
