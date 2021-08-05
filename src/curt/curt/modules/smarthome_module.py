""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, August 2020

"""

class SmartHomeModule(BaseModule):
    # fake workers for sending command
    # Different configuration file section

    def __init__(self):

        self.session = None
        # connection section for HA communication

