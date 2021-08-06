""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, October 2020

"""

from curt.base_factory import BaseFactory

class SmartHomeFactory(BaseFactory):

    def __init__(self):
        super().__init__("smarthome")