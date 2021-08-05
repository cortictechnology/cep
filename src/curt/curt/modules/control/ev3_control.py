""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, October 2020

"""

import rpyc
import logging
import time
from curt.modules.control.base_control import BaseControl
from curt.utils import PID

class EV3Control(BaseControl):

    def __init__(self):
        super().__init__("ev3")
        self.controller = PID(0.5, 0, 0)

    
    def config_control_handler(self, params):
        self.hub_address = params['hub_address']
        if self.connection is not None:
            self.connection.close()
        try:
            self.connection = rpyc.classic.connect(self.hub_address)
            self.ev3_motor = self.connection.modules['ev3dev2.motor']
            self.ev3d_sensor = self.connection.modules['ev3dev2.sensor']
            self.ev3_sensor_lego = self.connection.modules['ev3dev2.sensor.lego']
            self.ev3_sound = self.connection.modules['ev3dev2.sound']
            print("EV3 control config finished")
            return True
        except:
            return False
            

    def get_motor_from_letter(self, motor_letter):
        if motor_letter == "A":
            return self.ev3_motor.OUTPUT_A
        elif motor_letter == "B":
            return self.ev3_motor.OUTPUT_B
        elif motor_letter == "C":
            return self.ev3_motor.OUTPUT_C
        elif motor_letter == "D":
            return self.ev3_motor.OUTPUT_D
        else:
            return None


    def control_motor(self, data):
        if data['motor_arrangement'] == "pair":
            motor_1 = self.get_motor_from_letter(data['motor_1'])
            motor_2 = self.get_motor_from_letter(data['motor_2'])
            if not hasattr(self, 'motor_tank'):
                if motor_1 is not None and motor_2 is not None:
                    self.motor_tank = self.ev3_motor.MoveTank(motor_1, motor_2)
            if data['motion'] == "rotate_on_degrees":
                degrees = data['degrees']
                speed = data['speed']
                self.motor_tank.on_for_degrees(-speed, speed, degrees)

            elif data['motion'] == "power_on":
                speed = data['speed']
                self.motor_tank.on(speed, speed)
            
            elif data['motion'] == "power_off":
                self.motor_tank.off()

        return True


    def capture_sensor_data(self, data):
        pass


    def sound(self, sentence):
        if not hasattr(self, 'play_sound'):
            self.play_sound = self.ev3_sound.Sound()
        print("Sentence:", sentence)
        self.play_sound.speak(str(sentence))