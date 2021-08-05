""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, August 2020

"""

class circularlist(object):
    def __init__(self, size, data = []):
        """Initialization"""
        self.index = 0
        self.size = size
        self._data = list(data)[-size:]

    def append(self, value):
        """Append an element"""
        if len(self._data) == self.size:
            self._data[self.index] = value
        else:
            self._data.append(value)
        self.index = (self.index + 1) % self.size

    def __getitem__(self, key):
        """Get element by index, relative to the current index"""
        if len(self._data) == self.size:
            return(self._data[(key + self.index) % self.size])
        else:
            return(self._data[key])

    def __repr__(self):
        """Return string representation"""
        return self._data.__repr__() + ' (' + str(len(self._data))+' items)'

    def calc_average(self):
        num_data = len(self._data)
        sum = 0
        for val in self._data:
            sum = sum + val
        return(float(sum)/num_data)


class PID:

    def __init__(self, kp, kd, ki):
        self.kp = kp
        self.kd = kd
        self.ki = ki

        self.d_control_error = 0
        self.previous_control_error = 0
        self.previous_2_control_error = 0
        self.sum_of_control_errors = 0

    
    def set_kp(self, kp):
        self.kp = kp

    
    def set_kd(self, kd):
        self.kd = kd


    def set_ki(self, ki):
        self.ki = ki


    def update_states(self, control_error):
        self.d_control_error = 1.5 * control_error - 2 * self.previous_control_error + 0.5 * self.previous_2_control_error
        self.previous_2_control_error = self.previous_control_error
        self.previous_control_error = control_error
        self.sum_of_control_errors = self.sum_of_control_errors + control_error
        if self.sum_of_control_errors > 20:
            self.sum_of_control_errors = 20
        if self.sum_of_control_errors < -20:
            self.sum_of_control_errors = -20


    def pid_control_adjustment(self, control_error):
        return self.kp * control_error + self.kd * self.d_control_error + self.ki * self.sum_of_control_errors