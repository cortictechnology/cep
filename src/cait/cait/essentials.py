""" 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, December 2019

"""

import cait.core as core
import time
import logging

logging.getLogger().setLevel(logging.WARNING)

"""
Assumptions:
    1. Single USB webcam (supported ones)
    2. 3.5mm audio jack speaker
    3. Microphone integrated with webcam
    4. Default one database for people. person name is folder name.
    5. Faces and objects are tracked implicitly
    6. Need to teach list and dictionary knowledge
    7. return None if error occurred, otherwise empty return is normal if nothing detected
"""


def get_cloud_accounts():
    """Get a list of google cloud servie account

    Returns:
        account_list (list): List of google cloud servie account
    """
    account_list = core.get_cloud_accounts()
    return {"accounts": account_list}


def get_nlp_models():
    model_list = core.get_nlp_models()
    return {"models": model_list}


def get_video_devices():
    """Get a list of connected camera device

    Returns:
        video_device_list (list): List of camera device
    """
    return core.get_video_devices()


def get_video_services():
    """Get a list of connected camera device

    Returns:
        video_device_list (list): List of camera device
    """
    return core.get_video_devices()


def get_oakd_devices():
    """Get a list of connected oakd device

    Returns:
        video_device_list (list): List of camera device
    """
    return core.get_oakd_devices()


def get_oakd_services():
    """Get a list of connected oakd device

    Returns:
        video_device_list (list): List of camera device
    """
    return core.get_oakd_devices()


def get_audio_devices():
    """Get a list of connected audio device

    Returns:
        (list): List of audio device
    """
    return core.get_audio_devices()


def get_respeaker_services():
    return core.get_respeaker_services()


def get_voice_processing_services():
    """Get a list of voice processing services

    Returns:
        (list): List of audio device
    """
    return core.get_voice_processing_services()


def get_voice_generation_services(online=True):
    """Get a list of voice generation services

    Returns:
        (list): List of audio device
    """
    return core.get_voice_generation_services(online)


def get_control_devices():
    """Get a list of connected control device

    Returns:
        (list): List of control device
    """
    return core.get_control_devices()


def get_control_services():
    """Get a list of control services

    Returns:
        (list): List of control service
    """
    return core.get_control_services()


def test_camera(index):
    """Open the camera device with specific index, test for its connetion

    Parameters:
        index (int): index of the camera device

    Returns:
        (bool): True if success, False otherwise
    """
    return core.test_camera(index)


def initialize_component(
    component_name,
    mode,
    account="default",
    processor="local",
    language="english",
    from_web=False,
):
    """Initalization function for different components

    Parameters:
        component_name (string): name of the component to be initialized

    Keyword Parameters:
        useOnline {bool}: use online service or not (default: {True})

    Returns:
        (bool): True if initialization is success, False otherwise
    """
    if component_name == "vision":
        success, msg = core.initialize_vision(processor, mode, from_web=from_web)
    elif component_name == "voice":
        success, msg = core.initialize_voice(mode, account, language)
    elif component_name == "nlp":
        success, msg = core.initialize_nlp(mode)
    elif component_name == "control":
        success, msg = core.initialize_control(mode)
    elif component_name == "smart_home":
        success = True
        msg = "OK"
    return success, msg


def initialize_pid(kp, ki, kd):
    success, msg = core.initialize_pid(float(kp), float(ki), float(kd))
    return success, msg


def deactivate_vision():
    """Deactivate the vision component

    Returns:
        (Bool): True if deactivate successfullt, False otherwise
    """
    return core.deactivate_vision()


def deactivate_voice():
    """Deactivate the voice component

    Returns:
        (Bool): True if deactivate successfullt, False otherwise
    """
    return core.deactivate_voice()


def reset_modules():
    """Reset all module states

    Returns:
        (Bool): True if reset successfullt, False otherwise
    """
    return core.reset_modules()


def change_module_parameters(parameter_name, value):
    """Generic function for setting ai module parameters
    Parameters:
        parameter_name (string): name of prarmeter
        value {float}: value of parameter

    """
    core.change_module_parameters(parameter_name, value)


def sleep(time_value):
    """Wrapper function for the time.sleep() function
    Parameters:
        time_value {int}: sleep time in second

    """
    time.sleep(time_value)
    return True


def enable_drawing_mode(mode, from_web=False):
    """Wrapper function to enable drawing modes
    Parameters:
        mode {String}: mode to enable
    """
    core.enable_drawing_mode(mode, from_web=from_web)


def draw_detected_face(face, from_web=False):
    """Wrapper function to draw detected face to current camera feed
    Parameters:
        face: location information of the face

    """
    if isinstance(face, dict):
        core.draw_detected_face(face["coordinates"], from_web=from_web)
    else:
        core.draw_detected_face(face, from_web=from_web)


def draw_recognized_face(people, from_web=False):
    """Wrapper function to draw recognized face to current camera feed
    Parameters:
        people {Dict}: names and locations of faces

    """
    if isinstance(people, dict):
        core.draw_recognized_face(
            people["names"], people["coordinates"], from_web=from_web
        )
    else:
        core.draw_recognized_face(people[0], people[1], from_web=from_web)


def draw_estimated_emotions(emotions, from_web=False):
    """Wrapper function to draw face emotions to current camera feed
    Parameters:
        emotions: emotion information of the faces

    """
    if isinstance(emotions, dict):
        core.draw_estimated_emotions(emotions["emotions"], from_web=from_web)
    else:
        core.draw_estimated_emotions(emotions, from_web=from_web)


def draw_estimated_facemesh(facemesh, from_web=False):
    """Wrapper function to draw face facemesh to current camera feed
    Parameters:
        facemesh: facemesh information of the faces

    """
    if isinstance(facemesh, dict):
        core.draw_estimated_facemesh(facemesh["facemesh"], from_web=from_web)
    else:
        core.draw_estimated_facemesh(facemesh, from_web=from_web)


def draw_detected_objects(objects, from_web=False):
    """Wrapper function to draw detected objects to current camera feed
    Parameters:
        objects: location information of the objects

    """
    if isinstance(objects, dict):
        core.draw_detected_objects(
            objects["names"], objects["coordinates"], from_web=from_web
        )
    else:
        core.draw_detected_objects(objects[0], objects[1], from_web=from_web)


def draw_estimated_body_landmarks(body_landmarks_coordinates, from_web=False):
    """Wrapper function to draw body landmarks to current camera feed
    Parameters:
        body_landmarks_coordinates: body landmarks locations

    """
    if isinstance(body_landmarks_coordinates, dict):
        core.draw_estimated_body_landmarks(
            body_landmarks_coordinates["body_landmarks_coordinates"], from_web=from_web
        )
    else:
        core.draw_estimated_body_landmarks(
            body_landmarks_coordinates, from_web=from_web
        )


def draw_estimated_hand_landmarks(hand_landmarks_coordinates, from_web=False):
    """Wrapper function to draw hand landmarks to current camera feed
    Parameters:
        hand_landmarks_coordinates: hand landmarks locations

    """
    if isinstance(hand_landmarks_coordinates, dict):
        core.draw_estimated_hand_landmarks(
            hand_landmarks_coordinates["hand_landmarks_coordinates"], from_web=from_web
        )
    else:
        core.draw_estimated_hand_landmarks(
            hand_landmarks_coordinates, from_web=from_web
        )


def get_camera_image():
    """Retrieve one rgb camera image

    Returns:
        (mat): cv2 image
    """
    img = core.get_camera_image()
    if img is not None:
        return img
    else:
        return None


def get_stereo_image():
    """Retrieve one stereo camera image

    Returns:
        (mat): cv2 image
    """
    img = core.get_stereo_image()
    if img is not None:
        return img
    else:
        return None


def detect_face(processor="oakd", spatial=False):
    """Detects all person faces from camera feed. No need to pass in camera feed explicitly at this level.

    Returns:
        (list): coordinates
    """
    faces = core.detect_face(processor=processor, spatial=spatial)

    if faces is not None:
        coordinates = faces
        faces = {"success": True, "coordinates": coordinates}
        return faces
    else:
        return {"success": False}


def recognize_face():
    """Recognize the name of person from camera feed. No need to pass in camera feed explicitly at this level.

    Returns:
        people (List): names of recognized people
        coordinates (List): coordinates of recognized faces
    """

    names, coordinates = core.recognize_face()

    if names is not None and coordinates is not None:
        result = {"success": True, "names": names, "coordinates": coordinates}
        return result
    else:
        return {"success": False}


def add_person(name=None):
    """Add a new person into face database, associate the name with the person's face image captured from camera feed.

    Parameters:
        name (string): name of the person.

    Returns:
        (bool): return True if adding face is success, False otherwise.
    """
    if name == None:
        return -1

    success = core.add_person(name)

    return success


def remove_person(name):
    """Remove a specific person from database

    Parameters:
        name (string): name of the person to remove
    """
    if name == None:
        return -1

    success = core.remove_person(name)

    return success


def detect_objects(spatial=False):
    """detect the object appearing in camera feed

    Returns:
        (list): names of the objects
        (list): coordinates of objects
    """
    objects = core.detect_objects(spatial=spatial)

    if objects is not None:
        names, coordinates = objects
        objects = {"success": True, "names": names, "coordinates": coordinates}
        return objects
    else:
        return None


def facemesh_estimation():
    """Estimate the meshes of faces

    Returns:
        (list): meshes of faces
    """
    facemesh = core.facemesh_estimation()
    if facemesh is not None:
        result = {"success": True, "facemesh": facemesh}
        return result
    else:
        return None


def face_emotions_estimation():
    """Estimate the emotions of faces

    Returns:
        (list): enmotions of faces
    """
    emotions = core.face_emotions_estimation()
    if emotions is not None:
        result = {"success": True, "emotions": emotions}
        return result
    else:
        return None


def get_hand_landmarks():
    """Estimate the landmarks of hands

    Returns:
        (list): landmark coordinates of the hands
    """
    hand_landmarks_coordinates, hand_bboxes, handnesses = core.get_hand_landmarks()
    result = {
        "success": True,
        "hand_landmarks_coordinates": hand_landmarks_coordinates,
        "hand_bboxes": hand_bboxes,
        "handnesses": handnesses,
    }
    return result


def get_body_landmarks():
    """Estimate the landmarks of a human body

    Returns:
        (list): landmark coordinates of the body
    """
    body_landmarks_coordinates = core.get_body_landmarks()
    result = {"success": True, "body_landmarks_coordinates": body_landmarks_coordinates}
    return result


def classify_image():
    """Classify the current camera feed into an image label

    Returns:
        (list): top 5 possible image types
    """
    names = core.classify_image()

    if names is not None:
        names = {"success": True, "names": names}
        return names
    else:
        return None


def listen():
    """Listen to user speech from audio feed captured by microphone.

    Returns:
        (string): the user speech generated from speech-to-text module.
    """

    success, text = core.listen()

    return success, text


def listen_for_wakeword():
    """Continuously detecting the appeareance of wakeword from the audio stream. Higher priority than the listen() function.

    Returns:
        (bool): return True if detected wakeword, False otherwise.
    """

    gotWakeWord = core.listen_for_wakeword()

    return gotWakeWord


def say(text):
    """Speak the text through speaker at the specific volume.

    Parameters:
        text (string): text to be spoken.
        volume (int): 0-100.

    Returns:
        (bool): True if successfully spoken. False otherwise.
    """
    if text == None:
        return -1

    success = core.say(text)

    return success


def analyse_text(text):
    """Analyse the user speech generated from the listen() function.

    Parameters:
        text (string): user speech.

    Returns:
        (dict): Contains the intention and entities from the analytics of the user speech.
    """
    if text == None:
        return -1

    topic, condifence, entities = core.analyze(text)

    intention = {"topic": topic, "confidence": condifence, "entities": entities}

    return intention


def set_motor_position(hub_name, motor_name, position):
    """Set the absolute position of a motor

    Parameters:
        motor_name (string): Name of motor to control, currently, only support "motor_A", "motor_B", "motor_C", "motor_D" corresponding to BrickPi ports
        position (int): -inf to inf

    Returns:
        (bool): True if successfully moved. False otherwise.
    """

    success, msg = core.set_motor_position(hub_name, motor_name, position)

    return success, msg


def set_motor_power(hub_name, motor_name, power):
    """Set the power level of a motor

    Parameters:
        motor_name (string): Name of motor to control, currently, only support "motor_A", "motor_B", "motor_C", "motor_D" corresponding to BrickPi ports
        power (int): 0-100

    Returns:
        (bool): True if successfully moved. False otherwise.
    """

    success, msg = core.set_motor_power(hub_name, motor_name, power)

    return success, msg


def set_motor_power_group(operation_list):
    """Set the power level of a motor group

    Parameters:
        operation_list (list): A list of operation in string, refer to code generated from the visual programming interface

    Returns:
        (bool): True if successfully moved. False otherwise.
    """

    success, msg = core.set_motor_power_group(operation_list)

    return success, msg


def control_motor(hub_name, motor_name, speed, duration):
    """Move robot forward or backward, with specific speed and for specific duration

    Parameters:
        motor_name (string): Name of motor to control, currently, only support "motor_A", "motor_B", "motor_C", "motor_D" corresponding to BrickPi ports
        speed (int): 0-100
        duration (int): 0 - inf

    Returns:
        (bool): True if successfully moved. False otherwise.
    """

    success, msg = core.control_motor(hub_name, motor_name, speed, duration)

    return success, msg


def control_motor_group(operation_list):
    """Move a group of motors together

    Parameters:
        operation_list (list): A list of operation in string, refer to code generated from the visual programming interface

    Returns:
        (bool): True if successfully moved. False otherwise.
    """

    success, msg = core.control_motor_group(operation_list)

    return success, msg


def rotate_motor(hub_name, motor_name, angle):
    """Rotate robot to a certain angle

    Parameters:
        motor_name (string): Name of motor to control, currently, only support "motor_A", "motor_B", "motor_C", "motor_D" corresponding to BrickPi ports
        angle (int): Roatational angle

    Returns:
        (bool): True if successfully moved. False otherwise.
    """

    success, msg = core.rotate_motor(hub_name, motor_name, angle)

    return success, msg


def update_pid(error):
    value = core.update_pid(float(error))
    return {"value": value}


def get_devices(device_type):
    """Get a list of smart devices in the local network

    Returns:
        (list): List of smart devices in the local network
    """
    devices = core.get_devices(device_type)
    result = {"devices": devices}

    return result


def control_light(device_name, operation, parameter=None):
    """Control the operation of a smart light device.

    Parameters:
        device_name (string): name of smart light device.
        operation (string): operation, currently supporting "turn_on",  "turn_off", "toggle", "color_name", "brightness_pct".
        parameter {}: any parameter for the operation.

    Returns:
        (bool): True if successfully sent command to homeassistant. False otherwise.
    """
    result = core.control_light(device_name, operation, parameter)
    return result


def control_media_player(device_name, operation):
    """Control the operation of a smart media player.

    Parameters:
        device_name (string): name of smart media player.
        operation (string): operation, currently supporting "media_play",  "media_pause", "volume_up", "volume_down".

    Returns:
        (bool): True if successfully sent command to homeassistant. False otherwise.
    """
    result = core.control_media_player(device_name, operation)
    return result


def turn_to_person(name):
    """Rotate the robot to face a person, this is a combined usage of recognizeFace() and move() function. Not implemented.

    Parameters:
        name (string): name of the person that the robot should center to.

    Returns:
        (bool): True if successfully turned. False otherwise.
    """
    success = True
    return success


def follow_person(name):
    """Move the robot so that it constantly follows a person, this is a combined usage of recognizeFace() and move() function. Not implemented.

    Parameters:
        name (string): name of the person that the robot should be following.

    Returns:
        (bool): True if successfully moved. False otherwise.
    """
    success = True
    return success


def greet_person(name, speech):
    """Greet a specific person in a specific way, this is combined usage of recognizeFace() and say() function. Not implemented.

    Parameters:
        name (sring): name of the person to greet, it can be an actual name, or simply Unknown.
        speech (string): words to say to the person.

    Returns:
        (bool): True if successfully greeted. False otherwise.
    """
    success = True
    return success


def ask_for_person_name():
    """Ask for the name of a person appearing in the camera feed, this is a combined usage of say(), listen() and analyseSpeech() function. Not implemented.

    Returns:
        (string): name of the person.
    """
    name = ""
    return name


def get_response(text):
    """Generate robot response based on user speech input. Not implemented.

    Parameters:
        text (string): Result from listen() function

    Returns:
        (string): robot response
    """
    respone = ""
    return respone


def control_smart_device(device_name, action):
    """Control the smart devices's state through action. Not implemented.

    Parameters:
        device_name (string): Name of the device recorded in Home assistant
        action (string): valid action state for the device, as recorded in home assistant.

    Returns:
        (bool): True if device is successfully controlled. False otherwise.
    """
    success = True
    return success
