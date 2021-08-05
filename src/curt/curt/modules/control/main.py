""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, October 2020

"""

from curt.modules.control_module import ControlModule
from curt.modules.module_main import ModuleMain


class ControlMain(ModuleMain):
    def __init__(self):
        super().__init__(ControlModule(), port=9437)


if __name__ == "__main__":
    control_main = ControlMain()
    control_main.run_forever()
