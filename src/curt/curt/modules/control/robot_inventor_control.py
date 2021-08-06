""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, October 2020

"""

import logging
import time
import bluetooth
from curt.modules.control.base_control import BaseControl
from curt.utils import PID

logging.getLogger().setLevel(logging.INFO)


class RobotInventorControl(BaseControl):
    def __init__(self):
        super().__init__("robot_inventor")
        self.current_emotion = ""
        self.current_hub_address = ""

    def connect_to_robot_inventor(self, hub_address):
        try:
            print(hub_address)
            self.connection = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            robot_inventor_hub = bluetooth.find_service(address=hub_address)
            port = robot_inventor_hub[2]["port"]
            host = robot_inventor_hub[2]["host"]
            logging.warning("Connecting to: " + str(port) + ", " + str(host))
            self.connection.connect((host, port))
            time.sleep(1)
            self.connection.settimeout(5)
            self.connection.send(b"\x03")
            self.connection.send(b"import hub\x0D")
            time.sleep(0.5)
            dump = self.connection.recv(102400)
            time.sleep(0.5)
            self.current_hub_address = hub_address
            return True
        except:
            logging.warning("No robot inventor hub connected")
            return False

    def config_control_handler(self, params):
        hub_address = params["hub_address"]
        if self.current_hub_address != hub_address:
            if self.current_hub_address != "":
                self.connection.close()

        success = self.connect_to_robot_inventor(hub_address)
        retry_count = 0
        while not success:
            success = self.connect_to_robot_inventor(hub_address)
            retry_count += 1
            if retry_count > 3:
                logging.warning("Exceed retry time")
                break
        if not success:
            logging.warning("Failed connecting to robot inventor hub")
            self.current_hub_address = ""
            self.connection = None
            return False
        return True

    def control_motor(self, data):
        if self.connection is not None:
            if data["motor_arrangement"] == "pair":
                motor_1 = data["motor_1"]
                motor_2 = data["motor_2"]
                msg = (
                    b"pair = hub.port."
                    + motor_1.encode("utf-8")
                    + b".motor.pair(hub.port."
                    + motor_2.encode("utf-8")
                    + b".motor)\x0D"
                )
                self.connection.send(msg)
                if data["motion"] == "rotate_on_degrees":
                    degrees = data["degrees"]
                    speed_1 = int(data["speed_1"])
                    speed_2 = int(data["speed_2"])
                    msg_pair = (
                        b"pair.run_for_degrees("
                        + str(degrees).encode("utf-8")
                        + b", "
                        + str(speed_1).encode("utf-8")
                        + b", "
                        + str(speed_2).encode("utf-8")
                        + b")\x0D"
                    )
                    self.connection.send(msg_pair)
                    time.sleep(0.5)
                elif data["motion"] == "speed":
                    speed_1 = int(data["speed_1"])
                    speed_2 = int(data["speed_2"])
                    msg_pair = (
                        b"pair.run_at_speed("
                        + str(speed_1).encode("utf-8")
                        + b", "
                        + str(speed_2).encode("utf-8")
                        + b")\x0D"
                    )
                    self.connection.send(msg_pair)
                    time.sleep(0.005)
                elif data["motion"] == "brake":
                    msg_pair = b"pair.brake()\x0D"
                    self.connection.send(msg_pair)
                    time.sleep(0.005)
                elif data["motion"] == "rotate_to_position":
                    position = data["position"]
                    speed_1 = int(data["speed_1"])
                    speed_2 = int(data["speed_2"])
                    time.sleep(0.005)
            elif data["motor_arrangement"] == "individual":
                motor = data["motor"]
                if data["motion"] == "rotate_on_degrees":
                    degrees = data["degrees"]
                    speed = data["speed"]
                    msg_individual = (
                        b"hub.port."
                        + motor.encode("utf-8")
                        + b".motor.run_for_degrees("
                        + str(degrees).encode("utf-8")
                        + b", "
                        + str(speed).encode("utf-8")
                        + b")\x0D"
                    )
                    self.connection.send(msg_individual)
                    time.sleep(0.005)
                elif data["motion"] == "rotate_to_position":
                    position = data["position"]
                    speed = data["speed"]
                    msg_0 = b"motor = hub.port." + motor.encode("utf-8") + b".motor\x0D"
                    msg_1 = b"abs_pos = motor.get()[2]\x0D"
                    msg_2 = b"if abs_pos > 180: abs_pos = abs_pos - 360\x0D\x0D"
                    msg_3 = b"motor.preset(abs_pos)\x0D"
                    msg_4 = (
                        b"motor.run_to_position("
                        + str(position).encode("utf-8")
                        + b", 100)\x0D"
                    )
                    self.connection.send(msg_0)
                    print(msg_0)
                    time.sleep(0.003)
                    self.connection.send(msg_1)
                    print(msg_2)
                    time.sleep(0.003)
                    self.connection.send(msg_2)
                    print(msg_2)
                    time.sleep(0.003)
                    self.connection.send(msg_3)
                    print(msg_3)
                    time.sleep(0.003)
                    self.connection.send(msg_4)
                    print(msg_4)
                    time.sleep(0.003)
                elif data["motion"] == "speed":
                    speed = int(data["speed"])
                    msg_individual = (
                        b"hub.port."
                        + motor.encode("utf-8")
                        + b".motor.run_at_speed("
                        + str(speed).encode("utf-8")
                        + b", 100)\x0D"
                    )
                    self.connection.send(msg_individual)
                    time.sleep(0.005)
                elif data["motion"] == "brake":
                    msg_individual = (
                        b"hub.port." + motor.encode("utf-8") + b".motor.brake()\x0D"
                    )
                    self.connection.send(msg_individual)
                    time.sleep(0.005)
            return True
        else:
            return False

    def display(self, data):
        if data["display_type"] == "image":
            if data["image"] == "Happy":
                if self.current_emotion == "Sad":
                    msg = b"hub.display.show([hub.Image.SAD, hub.Image.HAPPY], fade=2, loop=False, delay=1000)\x0D"
                    self.connection.send(msg)
                    time.sleep(0.1)
                    self.current_emotion = "Happy"
                elif self.current_emotion == "":
                    print("Displaying happy")
                    msg = b"hub.display.show(hub.Image.HAPPY)\x0D"
                    self.connection.send(msg)
                    time.sleep(0.1)
            elif data["image"] == "Sad":
                if self.current_emotion == "Happy":
                    msg = b"hub.display.show([hub.Image.HAPPY, hub.Image.SAD], fade=2, loop=False, delay=1000)\x0D"
                    self.connection.send(msg)
                    time.sleep(0.1)
                    self.current_emotion = "Sad"
                elif self.current_emotion == "":
                    msg = b"hub.display.show(hub.Image.SAD)\x0D"
                    self.connection.send(msg)
                    time.sleep(0.1)
                    self.current_emotion = "Sad"
            elif data["image"] == "clock":
                msg = (
                    b"hub.display.show(hub.Image.ALL_CLOCKS, loop=True, delay=100)\x0D"
                )
                self.connection.send(msg)
                time.sleep(0.1)
        elif data["display_type"] == "text":
            msg = (
                b'hub.display.show("' + data["text"].encode("utf-8") + b'", fade=2)\x0D'
            )
            self.connection.send(msg)
            time.sleep(0.1)

    def capture_sensor_data(self, data):
        pass

    def sound(self, sentence):
        if sentence == "Hi, I am Sam":
            msg = b'hub.sound.play("sam.spike.bin")\x0D'
            self.connection.send(msg)
            time.sleep(0.1)
        elif sentence == "I can see you now":
            msg = b'hub.sound.play("see_you_now.spike.bin")\x0D'
            self.connection.send(msg)
            time.sleep(0.1)
        elif sentence == "Where are you going":
            msg = b'hub.sound.play("where.spike.bin")\x0D'
            self.connection.send(msg)
            time.sleep(0.1)
