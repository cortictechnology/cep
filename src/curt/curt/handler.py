""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

class Handler:
    def __init__(self, output_channel, guid, name):
        self.output_channel = output_channel
        self.guid = guid
        self.name = name
