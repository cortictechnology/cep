""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

from curt.modules.voice_module import VoiceModule
from curt.modules.module_main import ModuleMain


class VoiceMain(ModuleMain):
    def __init__(self):
        super().__init__(VoiceModule(), port=9438)


if __name__ == "__main__":
    voice_main = VoiceMain()
    voice_main.run_forever()
