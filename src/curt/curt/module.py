""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, August 2020

"""

class Module:

    def __init__(self, module_type, config_channel, task_channel, output_channel, worker_list, load):
        self.module_type = module_type
        self.config_channel = config_channel
        self.task_channel = task_channel
        self.output_channel = output_channel
        self.worker_list = worker_list
        self.load = load