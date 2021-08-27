""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

from curt.modules.smarthome_module import SmartHomeModule
from curt.modules.module_main import ModuleMain


class SmartHomeMain(ModuleMain):
    def __init__(self):
        super().__init__(SmartHomeModule(), port=9440)


if __name__ == "__main__":
    smart_home_main = SmartHomeMain()
    smart_home_main.run_forever()
