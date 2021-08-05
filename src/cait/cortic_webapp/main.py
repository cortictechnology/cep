""" 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, November 2019

"""

from flask import Flask
from flask import render_template, request, redirect, session, jsonify, url_for
from flask_cors import CORS
from flask_login import (
    LoginManager,
    UserMixin,
    login_required,
    login_user,
    logout_user,
    current_user,
)
from urllib.parse import urlparse
from io import BytesIO
import time
import base64
import nbformat as nbf
import logging
import errno
import json
import subprocess
import os
import socket
import fcntl
import struct
import threading
import pyaudio
import wave
import ast
from wifi import Cell
from shutil import copyfile

logging.getLogger().setLevel(logging.INFO)

application = Flask(__name__)
application.secret_key = "corticCAIT"

login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = "/"
CORS(application)

new_hostname = ""
current_language = "english"

connecting_to_wifi = False

current_vision_user = ""
current_voice_user = ""
current_nlp_user = ""
current_control_hub_user = ""
current_smarthome_user = ""
wifilist = []


@application.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == "static":
        filename = values.get("filename", None)
        if filename:
            file_path = os.path.join(application.root_path, endpoint, filename)
            values["q"] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


class User(UserMixin):
    def __init__(self, id):
        self.id = id


def is_internet_connected(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(ex)
        return False


def import_cait_modules():
    global essentials
    from cait import essentials


import_thread = threading.Thread(target=import_cait_modules, daemon=True)
import_thread.start()


def get_ip(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(
        fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack("256s", bytes(ifname[:15], "utf-8")),
        )[20:24]
    )


def get_connected_wifi():
    try:
        output = subprocess.check_output(["sudo", "iwgetid"])
        return output.decode("utf-8").split('"')[1]
    except Exception:
        return ""


@login_manager.user_loader
def load_user(id):
    return User(id)


@application.route("/setup")
def setup():
    return render_template("setup.html")


@application.route("/prev_setup")
def prev_setup():
    return render_template("setup.html")


@application.route("/isconnected", methods=["GET"])
def isConnected():
    connected = is_internet_connected()
    if connected:
        wifi_name = get_connected_wifi()
        ip = get_ip("wlan0")
        result = {"connected": True, "wifi": wifi_name, "ip": ip}
    else:
        result = {"connected": False}
    return jsonify(result)


@application.route("/wifi")
def wifi():
    if is_internet_connected():
        return redirect("/setup")
    return render_template("wifi.html")


@application.route("/prev_wifi")
def prev_wifi():
    return render_template("wifi.html")


@application.route("/getwifi", methods=["GET"])
def getwifi():
    global wifilist
    global connecting_to_wifi
    current_wifilist = []
    if not connecting_to_wifi:
        cells = list(Cell.all("wlan0"))
        for cell in cells:
            if cell.ssid != "":
                current_wifilist.append(cell.ssid)
    wifilist = current_wifilist
    return jsonify(wifilist)


@application.route("/connectwifi", methods=["POST"])
def connectwifi():
    global connecting_to_wifi
    os.system("sudo rm /etc/wpa_supplicant/wpa_supplicant.conf.success")
    data = request.get_json()
    ssid = data["ssid"]
    password = data["password"]
    logging.warning("SSID: " + ssid + ", PW: " + password)
    logging.warning("*************************")
    os.system(
        "sudo cp /etc/wpa_supplicant/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf.bak"
    )
    network_str = (
        '\nnetwork={\n        ssid="' + ssid + '"\n        psk="' + password + '"\n}\n'
    )
    with open("/etc/wpa_supplicant/wpa_supplicant.conf", "w") as f:
        f.write(
            "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\nupdate_config=1\ncountry=CA"
        )
        f.write(network_str)
    os.system("sudo wpa_cli -i wlan0 reconfigure")
    init_time = time.time()
    connecting_to_wifi = True
    while not is_internet_connected():
        time.sleep(1)
        logging.info("Connecting to wifi..no internet yet...")
        if time.time() - init_time >= 60:
            success = False
            os.system(
                "sudo mv /etc/wpa_supplicant/wpa_supplicant.conf.bak /etc/wpa_supplicant/wpa_supplicant.conf"
            )
            break
    if is_internet_connected():
        logging.info("Wifi connected.Internet connected.")
        success = True
        os.system(
            "sudo mv /etc/wpa_supplicant/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf.success"
        )
        os.system(
            "sudo mv /etc/wpa_supplicant/wpa_supplicant.conf.bak /etc/wpa_supplicant/wpa_supplicant.conf"
        )
    os.system("sudo wpa_cli -i wlan0 reconfigure")
    connecting_to_wifi = False
    result = {"result": success}
    return jsonify(result)


@application.route("/customdev", methods=["POST"])
def customdev():
    global new_hostname
    device_name = request.form.get("device_name")
    new_hostname = device_name
    username = request.form.get("username")
    password = request.form.get("user_password")
    subprocess.run(["sudo", "/usr/sbin/change_hostname.sh", device_name])
    res = os.system("sudo useradd -m " + username)
    if res != 0:
        result = {"result": res}
        return jsonify(result)
    out = os.system(
        "echo " + '"' + password + "\n" + password + '" | sudo passwd ' + username
    )
    g_out = os.system("sudo usermod -a -G cait " + username)
    if out == 0:
        os.system("sudo mkdir /home/" + username + "/cait_workspace")
        os.system(
            "sudo cp -R /home/pi/cait_workspace/*.cait /home/"
            + username
            + "/cait_workspace/"
        )
    os.system("sudo touch /usr/share/done_device_info")
    result = {"result": out}
    return jsonify(result)


@application.route("/testhardware")
def testhardware():
    return render_template("testhardware.html")


@application.route("/getusbdev", methods=["GET"])
def getusbdev():
    devices = essentials.get_usb_devices()
    usb_devices = []
    for udev in devices:
        if udev["tag"] == "Intel Movidius MyriadX":
            dev = {"tag": udev["tag"], "device": udev["device"]}
            usb_devices.append(dev)
    return jsonify(usb_devices)

@application.route("/getvideodev", methods=["GET"])
def getvideodev():
    devices = essentials.get_video_devices()
    video_devices = []
    for vid_dev in devices:
        dev = {"index": vid_dev["index"], "device": vid_dev["device"]}
        video_devices.append(dev)
    return jsonify(video_devices)


@application.route("/getaudiodev", methods=["GET"])
def getaudiodev():
    devices = essentials.get_audio_devices()
    audio_devices = []
    for aud_dev in devices:
        dev = {"index": aud_dev["index"], "device": aud_dev["device"], "type": aud_dev["type"]}
        audio_devices.append(dev)
    return jsonify(audio_devices)


@application.route("/get_control_devices", methods=["POST"])
def get_control_devices():
    devices = essentials.get_control_devices()
    control_devices = []
    for control_dev in devices:
        if control_dev["device"] == "EV3":
            dev = {
                "device": control_dev["device"],
                "mac_addr": control_dev["mac_addr"],
                "ip_addr": control_dev["ip_addr"],
            }
        else:
            dev = {"device": control_dev["device"], "mac_addr": control_dev["mac_addr"]}
        control_devices.append(dev)
    return jsonify({"control_devices": control_devices})


@application.route("/releasecam", methods=["GET"])
def releasecam():
    success = essentials.deactivate_vision()
    result = {"success": success}
    return jsonify(result)


@application.route("/testcam", methods=["POST"])
def testcam():
    data = request.get_json()
    cam_index = data["index"]
    logging.warning(str(cam_index))
    result = essentials.test_camera(cam_index)
    return jsonify(result)


@application.route("/testspeaker", methods=["POST"])
def testspeaker():
    data = request.get_json()
    speaker_index = data["index"]

    out = os.system(
        "sed -i '/defaults.ctl.card/c\defaults.ctl.card "
        + str(speaker_index)
        + "' /usr/share/alsa/alsa.conf"
    )
    out = os.system(
        "sed -i '/defaults.pcm.card/c\defaults.pcm.card "
        + str(speaker_index)
        + "' /usr/share/alsa/alsa.conf"
    )

    out = os.system("sudo -u pi aplay /opt/cortic_modules/voice_module/siri.wav")

    result = {"result": out}
    return jsonify(result)


@application.route("/testmicrophone", methods=["POST"])
def testmicrophone():
    data = request.get_json()
    index = data["index"]
    RESPEAKER_RATE = 16000
    RESPEAKER_CHANNELS = 2 
    RESPEAKER_WIDTH = 2
    # run getDeviceInfo.py to get index
    RESPEAKER_INDEX = 1  # refer to input device id
    CHUNK = 1024
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = "output.wav"
    try:
        p = pyaudio.PyAudio()  # Create an interface to PortAudio

        print("Recording")
        stream = p.open(
            rate=RESPEAKER_RATE,
            format=p.get_format_from_width(RESPEAKER_WIDTH),
            channels=RESPEAKER_CHANNELS,
            input=True,
            input_device_index=RESPEAKER_INDEX
        )

        frames = []  # Initialize array to store frames

        # Store data in chunks for 3 seconds
        for i in range(0, int(RESPEAKER_RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        # Not terminating as the scan device thread will take care of that
        # p.terminate()

        print("Finished recording")

        # Save the recorded data as a WAV file
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(RESPEAKER_CHANNELS)
        wf.setsampwidth(p.get_sample_size(p.get_format_from_width(RESPEAKER_WIDTH)))
        wf.setframerate(RESPEAKER_RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        os.system("sudo -u pi aplay -f cd -Dhw:0 " + WAVE_OUTPUT_FILENAME)

        out = os.system("rm " + WAVE_OUTPUT_FILENAME)

        result = {"result": out}
        return jsonify(result)
    except:
        result = {"result": -1}
        return jsonify(result)


@application.route("/thirdsignin")
def thirdsignin():
    return render_template("third_signin.html")


@application.route("/upload_account", methods=["POST"])
def upload_account():
    account_credentials = request.form.get("account_credentials")
    account_credentials = json.loads(account_credentials)
    curt_path = os.getenv("CURT_PATH")
    with open("/opt/accounts", "w") as f:
        f.write('["google_cloud", "account.json"]')
    with open(curt_path + "models/modules/voice/account.json", "w") as outfile:
        json.dump(account_credentials, outfile)
    result = {"result": True}
    return jsonify(result)


@application.route("/newname", methods=["POST"])
def newname():
    global new_hostname
    result = {"hostname": new_hostname}
    return jsonify(result)


@application.route("/congrats")
def congrats():
    return render_template("congrats.html")


@application.route("/finish", methods=["POST"])
def finish():
    data = request.get_json()
    hostname = data["hostname"]
    wifi_name = data["wifiname"]
    speech_account = data["speech_account"]
    if os.path.exists("/etc/wpa_supplicant/wpa_supplicant.conf.success"):
        with open("/etc/wpa_supplicant/wpa_supplicant.conf.success") as f:
            if wifi_name in f.read():
                os.system(
                    "sudo mv /etc/wpa_supplicant/wpa_supplicant.conf.success /etc/wpa_supplicant/wpa_supplicant.conf"
                )
    if speech_account != "local":
        account_credentials = json.loads(speech_account)
        curt_path = os.getenv("CURT_PATH")
        with open("/opt/accounts", "w") as f:
            f.write('["google_cloud", "account.json"]')
        with open(curt_path + "models/modules/voice/account.json", "w") as outfile:
            json.dump(account_credentials, outfile)
    subprocess.run(["sudo", "/usr/sbin/change_hostname.sh", hostname])
    os.system(
        "sudo sed -i 's/ssid=[^\"]*/ssid=" + hostname + "/g' /etc/hostapd/hostapd.conf"
    )
    os.system(
        "sudo sed -i 's/ignore_broadcast_ssid=[^\"]*/ignore_broadcast_ssid=="
        + hostname
        + "/g' /etc/hostapd/hostapd.conf"
    )
    os.system("sudo touch /usr/share/done_setup")
    result = {"success": True}
    return jsonify(result)


@application.route("/reboot", methods=["GET"])
def reboot():
    os.system("sudo reboot")


@application.route("/")
@application.route("/index")
def index():
    # if not os.path.exists("/usr/share/done_setup"):
    #     return redirect('/setup')
    return render_template("index.html")


@application.route("/signup_page")
def signup_page():
    return render_template("signup.html")


@application.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    p = subprocess.Popen(
        ["sudo", "/opt/chkpass.sh", username],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    out, err = p.communicate(str.encode(password))
    if out.decode("utf-8").find("Correct") != -1:
        user = User(username)
        login_user(user)
    result = {"result": out, "error": err}
    return jsonify(result)


@application.route("/logout")
def logout():
    logout_user()
    return redirect("/", code=302)


@application.route("/signup", methods=["POST"])
def signup():
    username = request.form.get("username")
    password = request.form.get("password")
    res = os.system("sudo useradd -m " + username)
    if res != 0:
        result = {"result": res}
        return jsonify(result)
    out = os.system(
        "echo " + '"' + password + "\n" + password + '" | sudo passwd ' + username
    )
    g_out = os.system("sudo usermod -a -G cait " + username)
    result = {"result": out}
    result = jsonify(result)
    if out == 0:
        os.system("sudo mkdir /home/" + username + "/cait_workspace")
        os.system(
            "sudo cp -R /home/pi/cait_workspace/*.cait /home/"
            + username
            + "/cait_workspace/"
        )
    return result


@application.route("/switchlang", methods=["POST"])
def switchlang():
    global current_language
    language = request.form.get("language")
    current_language = language
    result = {"result": True}
    return jsonify(result)


@application.route("/getusername", methods=["POST"])
def getusername():
    result = {"username": current_user.id}
    return jsonify(result)


@application.route("/programming")
@login_required
def programming():
    session.permanent = True
    if current_language == "chinese":
        return render_template("programming_chs.html")
    elif current_language == "french":
        return render_template("programming_fr.html")
    else:
        return render_template("programming.html")


@application.route("/get_cloud_accounts", methods=["POST"])
@login_required
def get_cloud_accounts():
    account_list = essentials.get_cloud_accounts()
    return jsonify(account_list)


@application.route("/get_nlp_models", methods=["POST"])
@login_required
def get_nlp_models():
    model_list = essentials.get_nlp_models()
    return jsonify(model_list)


@application.route("/initialize_component", methods=["POST"])
@login_required
def initialize_component():
    global current_vision_user
    global current_voice_user
    global current_nlp_user
    global current_control_hub_user
    global current_smarthome_user

    component_name = request.form.get("component_name")
    mode = request.form.get("mode")

    if component_name == "vision":
        mode = ast.literal_eval(mode)
        if current_vision_user == "" or current_vision_user == current_user.id:
            current_vision_user = current_user.id
            logging.warning("Vision User: " + current_vision_user)
        else:
            result = {
                "success": False,
                "error": "Vision compoent is being used by another user, please try again later.",
            }
            return jsonify(result)
    elif component_name == "voice":
        if current_voice_user == "" or current_voice_user == current_user.id:
            current_voice_user = current_user.id
            logging.warning("Voice User: " + current_voice_user)
        else:
            result = {
                "success": False,
                "error": "Speech compoent is being used by another user, please try again later.",
            }
            return jsonify(result)
    elif component_name == "nlp":
        if current_nlp_user == "" or current_nlp_user == current_user.id:
            current_nlp_user = current_user.id
            logging.warning("NLP User: " + current_nlp_user)
        else:
            result = {
                "success": False,
                "error": "NLP compoent is being used by another user, please try again later.",
            }
            return jsonify(result)
    elif component_name == "control":
        if (
            current_control_hub_user == ""
            or current_control_hub_user == current_user.id
        ):
            current_control_hub_user = current_user.id
            logging.warning("Control Hub User: " + current_control_hub_user)
        else:
            result = {
                "success": False,
                "error": "Control compoent is being used by another user, please try again later.",
            }
            return jsonify(result)

    account = request.form.get("account")
    if account == "default":
        account = current_user.id
    processor = request.form.get("processor")
    language = request.form.get("language")

    success, msg = essentials.initialize_component(
        component_name, mode, account, processor, language, from_web=True
    )
    if success == False:
        result = {"success": success, "error": msg}
    else:
        result = {"success": success}
    return jsonify(result)


@application.route("/init_pid", methods=["POST"])
@login_required
def init_pid():
    kp = request.form.get("kp")
    ki = request.form.get("ki")
    kd = request.form.get("kd")
    success, msg = essentials.initialize_pid(kp, ki, kd)
    if success == False:
        result = {"success": success, "error": msg}
    else:
        result = {"success": success}
    return jsonify(result)


@application.route("/release_components", methods=["POST"])
@login_required
def release_components():
    global current_vision_user
    global current_voice_user
    global current_nlp_user
    global current_control_hub_user
    success = False
    logging.warning("Releasing components")
    if current_vision_user == current_user.id:
        current_vision_user = ""
        success = essentials.deactivate_vision()
    if current_voice_user == current_user.id:
        current_voice_user = ""
        success = essentials.deactivate_voice()
    if current_nlp_user == current_user.id:
        current_nlp_user = ""
        success = True
    if current_control_hub_user == current_user.id:
        current_control_hub_user = ""
        success = True
    success = essentials.reset_modules()
    result = {"success": success}
    return jsonify(result)


@application.route("/change_module_parameters", methods=["POST"])
@login_required
def change_module_parameters():
    parameter_name = request.form.get("parameter_name")
    value = float(request.form.get("value"))
    essentials.change_module_parameters(parameter_name, value)
    result = {"success": True}
    return jsonify(result)


@application.route("/sleep", methods=["POST"])
@login_required
def cait_sleep():
    time_value = int(request.form.get("time"))
    result = essentials.sleep(time_value)
    result = {"success": result}
    return jsonify(result)


@application.route("/draw_detected_face", methods=["POST"])
@login_required
def draw_detected_face():
    face = json.loads(request.form.get("face"))
    essentials.draw_detected_face(face, from_web=True)
    result = {"success": True}
    return jsonify(result)


@application.route("/draw_recognized_face", methods=["POST"])
@login_required
def draw_recognized_face():
    coordinates = json.loads(request.form.get("coordinates"))
    names = json.loads(request.form.get("names"))
    essentials.draw_recognized_face((names, coordinates), from_web=True)
    result = {"success": True}
    return jsonify(result)


@application.route("/draw_estimated_emotions", methods=["POST"])
@login_required
def draw_estimated_emotions():
    emotions = json.loads(request.form.get("emotions"))
    essentials.draw_estimated_emotions(emotions, from_web=True)
    result = {"success": True}
    return jsonify(result)


@application.route("/draw_estimated_facemesh", methods=["POST"])
@login_required
def draw_estimated_facemesh():
    facemesh = json.loads(request.form.get("facemesh"))
    essentials.draw_estimated_facemesh(facemesh, from_web=True)
    result = {"success": True}
    return jsonify(result)

@application.route("/draw_detected_objects", methods=["POST"])
@login_required
def draw_detected_objects():
    names = json.loads(request.form.get("names"))
    coordinates = json.loads(request.form.get("coordinates"))
    essentials.draw_detected_objects((names, coordinates), from_web=True)
    result = {"success": True}
    return jsonify(result)


@application.route("/draw_estimated_body_landmarks", methods=["POST"])
@login_required
def draw_estimated_body_landmarks():
    body_landmarks_coordinates = json.loads(request.form.get("body_landmarks_coordinates"))
    essentials.draw_estimated_body_landmarks(body_landmarks_coordinates, from_web=True)
    result = {"success": True}
    return jsonify(result)

@application.route("/draw_estimated_hand_landmarks", methods=["POST"])
@login_required
def draw_estimated_hand_landmarks():
    hand_landmarks_coordinates = json.loads(request.form.get("hand_landmarks_coordinates"))
    essentials.draw_estimated_hand_landmarks(hand_landmarks_coordinates, from_web=True)
    result = {"success": True}
    return jsonify(result)


@application.route("/enable_drawing_mode", methods=["POST"])
@login_required
def enable_drawing_mode():
    mode = request.form.get("mode")
    essentials.enable_drawing_mode(mode, from_web=True)
    result = {"success": True}
    return jsonify(result)


@application.route("/camerafeed", methods=["POST"])
@login_required
def camerafeed():
    img = essentials.get_camera_image()
    if img is not None:
        encodedImage = BytesIO()
        img.save(encodedImage, "JPEG")
        contents = base64.b64encode(encodedImage.getvalue()).decode()
        encodedImage.close()
        contents = contents.split("\n")[0]
        return contents


@application.route("/detectface", methods=["POST"])
@login_required
def detectface():
    if current_vision_user != current_user.id:
        result = {
            "success": False,
            "error": "Vision compoent is being used by another user, please try again later.",
        }
        return jsonify(result)
    spatial = request.form.get("spatial")
    processor = request.form.get("processor")
    if spatial == "false":
        spatial = False
    elif spatial == "true":
        spatial = True
    faces = essentials.detect_face(processor, spatial)
    return jsonify(faces)


@application.route("/recognizeface", methods=["POST"])
@login_required
def recognizeface():
    if current_vision_user != current_user.id:
        result = {
            "success": False,
            "error": "Vision compoent is being used by another user, please try again later.",
        }
        return jsonify(result)
    people = essentials.recognize_face()
    return jsonify(people)


@application.route("/addperson", methods=["POST"])
@login_required
def addperson():
    if current_vision_user != current_user.id:
        result = {
            "success": False,
            "error": "Vision compoent is being used by another user, please try again later.",
        }
        return jsonify(result)
    person_name = request.form.get("name")
    success = essentials.add_person(person_name)
    result = {"success": success}
    return jsonify(result)


@application.route("/removeperson", methods=["POST"])
@login_required
def removeperson():
    if current_vision_user != current_user.id:
        result = {
            "success": False,
            "error": "Vision compoent is being used by another user, please try again later.",
        }
        return jsonify(result)
    person_name = request.form.get("name")
    logging.info("Remove: " + person_name)
    success = essentials.remove_person(person_name)
    result = {"success": success}
    return jsonify(result)


@application.route("/detectobject", methods=["POST"])
@login_required
def detectobject():
    if current_vision_user != current_user.id:
        result = {
            "success": False,
            "error": "Vision compoent is being used by another user, please try again later.",
        }
        return jsonify(result)
    spatial = request.form.get("spatial")
    if spatial == "false":
        spatial = False
    elif spatial == "true":
        spatial = True
    objects = essentials.detect_objects(spatial)
    return jsonify(objects)


@application.route("/classifyimage", methods=["POST"])
@login_required
def classifyimage():
    if current_vision_user != current_user.id:
        result = {
            "success": False,
            "error": "Vision compoent is being used by another user, please try again later.",
        }
        return jsonify(result)
    names = essentials.classify_image()
    return jsonify(names)


@application.route("/facemesh_estimation", methods=["POST"])
@login_required
def facemesh_estimation():
    if current_vision_user != current_user.id:
        result = {
            "success": False,
            "error": "Vision compoent is being used by another user, please try again later.",
        }
        return jsonify(result)
    facemeshes = essentials.facemesh_estimation()
    return jsonify(facemeshes)


@application.route("/face_emotions_estimation", methods=["POST"])
@login_required
def face_emotions_estimation():
    if current_vision_user != current_user.id:
        result = {
            "success": False,
            "error": "Vision compoent is being used by another user, please try again later.",
        }
        return jsonify(result)
    emotions = essentials.face_emotions_estimation()
    return jsonify(emotions)


@application.route("/get_body_landmarks", methods=["POST"])
@login_required
def get_body_landmarks():
    if current_vision_user != current_user.id:
        result = {
            "success": False,
            "error": "Vision compoent is being used by another user, please try again later.",
        }
        return jsonify(result)
    body_landmarks = essentials.get_body_landmarks()
    return jsonify(body_landmarks)


@application.route("/get_hand_landmarks", methods=["POST"])
@login_required
def get_hand_landmarks():
    if current_vision_user != current_user.id:
        result = {
            "success": False,
            "error": "Vision compoent is being used by another user, please try again later.",
        }
        return jsonify(result)
    hand_landmarks = essentials.get_hand_landmarks()
    return jsonify(hand_landmarks)


@application.route("/listen", methods=["POST"])
@login_required
def listen():
    success, text = essentials.listen()
    if success == False:
        result = {"success": success, "text": text}
    else:
        result = {"success": success, "text": text}
    return jsonify(result)


@application.route("/say", methods=["POST"])
@login_required
def say():
    text = request.form.get("text")
    success = essentials.say(text)
    result = {"success": success}
    return jsonify(result)


@application.route("/analyze", methods=["POST"])
@login_required
def analyze():
    text = request.form.get("text")
    result = essentials.analyse_text(text)
    return jsonify(result)


@application.route("/saveworkspace", methods=["POST"])
@login_required
def saveworkspace():
    xml_text = request.form.get("xml_text")
    filename = request.form.get("filename")
    if filename != "":
        save_type = request.form.get("save_type")
        if save_type == "autosave":
            location = "/home/" + current_user.id + "/tmp/"
        else:
            location = "/home/" + current_user.id + "/cait_workspace/"
        savename = location + filename
        if not os.path.exists(os.path.dirname(savename)):
            try:
                # os.makedirs(os.path.dirname(savename))
                os.system("sudo mkdir " + location)
                os.system("sudo chown " + current_user.id + ":cait " + location)
                os.system("sudo chmod -R g+rwx " + location)
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        f = open(savename, "w")
        f.write(xml_text)
        f.close()
        result = {"success": 1}
    else:
        result = {"success": -1}
    return jsonify(result)


def format_python_code(code_string):
    code = code_string
    formatted_code = []
    code_split = code.splitlines()
    for line in code_split:
        if line.find("import ") == 0 or line.find("from ") == 0:
            formatted_code.append(line)
    need_indent = False
    under_main_block = False
    variable_list = []
    for i in range(len(code_split)):
        line = code_split[i]
        if line.find("import ") == 0 or line.find("from ") == 0:
            continue
        if line.find(" = None") != -1:
            variable_name = line[0 : line.find(" = None")]
            variable_list.append(variable_name)
        if line.find("def") == 0 or line.find('"""') == 0 or line.find(" = None") != -1:
            need_indent = False
            if line.find("def main():") == 0:
                under_main_block = True
            else:
                under_main_block = False
        else:
            need_indent = True
        if need_indent:
            leading_space = len(line) - len(line.lstrip(" "))
            if leading_space > 0:
                line = line.lstrip(" ")
                line = " " * leading_space * 2 + line
                if under_main_block:
                    line = "    " + line
            else:
                line = "    " + line
        formatted_code.append(line)

    line_to_remove = []
    for line in formatted_code:
        if line.find('"""') == 0 or line.find("def") == 0:
            break
        if line.find("import ") == -1 and line.find(" = None") == -1:
            line_to_remove.append(line)

    for line in line_to_remove:
        formatted_code.remove(line)

    main_line_location = -1
    for i in range(len(formatted_code) - 1):
        line = formatted_code[i]
        if line.find("import ") == 0:
            if formatted_code[i + 1].find("import ") == -1:
                formatted_code[i] = line + "\n"
        if line.find(" = None") != -1:
            if formatted_code[i + 1].find(" = None") == -1:
                formatted_code[i] = line + "\n"
        if line.find("def main():") == 0:
            main_line_location = i

    if main_line_location != -1:
        global_line = "    global "
        for var in variable_list:
            global_line = global_line + var + ", "
        global_line = global_line[0:-2]
        if global_line != "    globa":
            formatted_code.insert(main_line_location + 1, global_line)

    formatted_code.append('\nif __name__ == "__main__":')
    formatted_code.append("    setup()")
    formatted_code.append("    main()")

    code = "\n".join(formatted_code)

    return code


@application.route("/savepythoncode", methods=["POST"])
@login_required
def savepythoncode():
    code = request.form.get("code")
    code = format_python_code(code)
    filename = request.form.get("filename")
    if filename != "":
        location = "/home/" + current_user.id + "/cait_workspace/python_code/"
        savename = location + filename
        if not os.path.exists(os.path.dirname(savename)):
            try:
                # os.makedirs(os.path.dirname(savename))
                os.system("sudo mkdir " + location)
                os.system("sudo chown " + current_user.id + ":cait " + location)
                os.system("sudo chmod -R g+rwx " + location)
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        f = open(savename, "w")
        f.write(code)
        f.close()
        result = {"success": True}
    else:
        result = {"success": -1}
    return jsonify(result)


@application.route("/savenotebook", methods=["POST"])
@login_required
def savenotebook():
    nb = nbf.v4.new_notebook()
    code = request.form.get("code")
    code = format_python_code(code)
    import_code = code[0 : code.find("\n\n")]
    import_code = import_code + "\nfrom lolviz import *"
    if code.find("None\n\n") != -1:
        import_code = (
            import_code + code[code.find("\n\n") : code.find("None\n\n")] + "None"
        )

    init_code = code[
        code.find("def setup():") : code.find("\n    \n", code.find("def setup():"))
    ]
    main_code = code[
        code.find("def main()") : code.find("\n\n", code.find("def main()"))
    ]
    run_code = code[code.find("if __name__") :]
    text = "Jupyter notebook generated from Cait visual programming interface"
    func_code = ""
    if code.find('"""') != -1:
        func_code = code[code.find('"""') : code.find("\n    \n    \n")]
        nb["cells"] = [
            nbf.v4.new_markdown_cell(text),
            nbf.v4.new_code_cell(import_code),
            nbf.v4.new_code_cell(func_code),
            nbf.v4.new_code_cell(init_code),
            nbf.v4.new_code_cell(main_code),
            nbf.v4.new_code_cell(run_code),
        ]
    else:
        nb["cells"] = [
            nbf.v4.new_markdown_cell(text),
            nbf.v4.new_code_cell(import_code),
            nbf.v4.new_code_cell(init_code),
            nbf.v4.new_code_cell(main_code),
            nbf.v4.new_code_cell(run_code),
        ]
    filename = request.form.get("filename")
    if filename != "":
        location = "/home/" + current_user.id + "/cait_workspace/python_notebooks/"
        savename = location + filename
        if not os.path.exists(os.path.dirname(savename)):
            try:
                # os.makedirs(os.path.dirname(savename))
                os.system("sudo mkdir " + location)
                os.system("sudo chown " + current_user.id + ":cait " + location)
                os.system("sudo chmod -R g+rwx " + location)
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        with open(savename, "w") as f:
            nbf.write(nb, f)
        result = {"success": True}
    else:
        result = {"success": -1}
    return jsonify(result)


@application.route("/clearcache", methods=["POST"])
@login_required
def clearcache():
    location = "/home/" + current_user.id + "/tmp/"
    filename = "workspace_autosave.xml"
    savename = location + filename
    result = {"success": True}
    try:
        os.remove(savename)

    except:
        pass
    return jsonify(result)


@application.route("/loadworkspace", methods=["POST"])
@login_required
def loadworkspace():
    filename = request.form.get("filename")
    if filename != "":
        save_type = request.form.get("save_type")
        if save_type == "autosave":
            location = "/home/" + current_user.id + "/tmp/"
        else:
            location = "/home/" + current_user.id + "/cait_workspace/"
        savename = location + filename
        if os.path.exists(savename):
            f = open(savename, "r")
            xml_text = f.read()
            f.close()
            # if filename == "workspace_autosave.xml":
            #     try:
            #         os.remove(savename)
            #     except:
            #         pass
        else:
            xml_text = ""
        result = {"xml_text": xml_text}
    else:
        result = {"xml_text": ""}
    return jsonify(result)


@application.route("/control_motor", methods=["POST"])
@login_required
def move():
    hub_name = request.form.get("hub_name")
    motor_name = request.form.get("motor_name")
    speed = request.form.get("speed")
    duration = request.form.get("duration")
    success, msg = essentials.control_motor(hub_name, motor_name, speed, duration)
    if success == False:
        result = {"success": success, "error": msg}
    else:
        result = {"success": success}
    return jsonify(result)


@application.route("/control_motor_group", methods=["POST"])
@login_required
def control_motor_speed_group():
    operation_list = request.form.get("data")
    success, msg = essentials.control_motor_group(operation_list)
    result = {"success": success}
    if success == False:
        result = {"success": success, "error": msg}
    else:
        result = {"success": success}
    return jsonify(result)


@application.route("/set_motor_position", methods=["POST"])
@login_required
def set_motor_position():
    hub_name = request.form.get("hub_name")
    motor_name = request.form.get("motor_name")
    position = request.form.get("position")
    success, msg = essentials.set_motor_position(hub_name, motor_name, int(position))
    if success == False:
        result = {"success": success, "error": msg}
    else:
        result = {"success": success}
    return jsonify(result)


@application.route("/set_motor_power", methods=["POST"])
@login_required
def set_motor_power():
    hub_name = request.form.get("hub_name")
    motor_name = request.form.get("motor_name")
    power = request.form.get("power")
    success, msg = essentials.set_motor_power(hub_name, motor_name, int(power))
    if success == False:
        result = {"success": success, "error": msg}
    else:
        result = {"success": success}
    return jsonify(result)


@application.route("/rotate_motor", methods=["POST"])
@login_required
def rotate_motor():
    hub_name = request.form.get("hub_name")
    motor_name = request.form.get("motor_name")
    angle = request.form.get("angle")
    success, msg = essentials.rotate_motor(hub_name, motor_name, int(angle))
    if success == False:
        result = {"success": success, "error": msg}
    else:
        result = {"success": success}
    return jsonify(result)


@application.route("/update_pid", methods=["POST"])
@login_required
def update_pid():
    error = request.form.get("error")
    result = essentials.update_pid(error)
    return jsonify(result)


@application.route("/get_states", methods=["POST"])
@login_required
def get_states():
    device_type = request.form.get("device_type")
    devices = essentials.get_devices(device_type)
    return jsonify(devices)


@application.route("/control_light", methods=["POST"])
@login_required
def control_light():
    device_name = "light." + request.form.get("device_name")
    operation = request.form.get("operation")
    parameter = request.form.get("parameter")
    result = essentials.control_light(device_name, operation, parameter)
    result = {"result": result}
    return jsonify(result)


@application.route("/control_media_player", methods=["POST"])
@login_required
def control_media_player():
    device_name = "media_player." + request.form.get("device_name")
    operation = request.form.get("operation")
    result = essentials.control_media_player(device_name, operation)
    result = {"result": result}
    return jsonify(result)


if __name__ == "__main__":
    application.run()
    # application.run(host="0.0.0.0", port=80, threaded=True)
