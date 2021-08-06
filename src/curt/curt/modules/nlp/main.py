""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

from curt.modules.nlp_module import NLPModule
from curt.modules.module_main import ModuleMain


class NLPMain(ModuleMain):
    def __init__(self):
        super().__init__(NLPModule(), port=9439)


if __name__ == "__main__":
    nlp_main = NLPMain()
    nlp_main.run_forever()
