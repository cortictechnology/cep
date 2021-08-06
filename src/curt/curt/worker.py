""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

class Worker:

    def __init__(self, name, config_channel, task_channel, output_channel):
        self.name = name
        self.config_channel = config_channel
        self.task_channel = task_channel
        self.output_channel = output_channel
        self.input_channels = []