""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, June 2021

"""

from curt.modules.vision_module import VisionModule
from curt.modules.module_main import ModuleMain


class VisionMain(ModuleMain):
    def __init__(self):
        super().__init__(VisionModule(), port=9436)


if __name__ == "__main__":
    vision_main = VisionMain()
    vision_main.run_forever()
