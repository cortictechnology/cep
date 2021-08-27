""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

import json
import os
import importlib


class BaseFactory:
    def __init__(self, module_type):
        # Read configuration file
        # instantiate workers
        # store service names and class names
        # map service names to workers
        self.module_type = module_type
        self.workers = {}  # "advertising_name": class instance
        self.service_worker_map = {}
        self.service_info = {}

        self.load_configuration_file()

    def load_configuration_file(self):
        # load all workers
        # pass corresponding worker to different typed factory
        with open(
            os.path.dirname(os.path.realpath(__file__)) + "/module_configs.json"
        ) as jsonfile:
            config_data = json.load(jsonfile)
            module_config = config_data[self.module_type]

        for module in module_config:
            if module.find("service") == -1:
                has_friendly_name = False
                if isinstance(module_config[module], list):
                    mod = importlib.import_module(
                        "curt.modules."
                        + self.module_type
                        + "."
                        + module_config[module][1]
                    )
                    has_friendly_name = True
                else:
                    mod = importlib.import_module(
                        "curt.modules." + self.module_type + "." + module
                    )

                if isinstance(module_config[module], list):
                    mod_class = getattr(mod, module_config[module][0])()
                    mod_class.friendly_name = module
                else:
                    mod_class = getattr(mod, module_config[module])()
                if module.find("oakd") != -1 and module != "oakd_pipeline":
                    if "oakd_pipeline" in self.workers:
                        mod_class.oakd_pipeline = self.workers["oakd_pipeline"]
                        print("Associating oakd pipeline to:", module)
                if has_friendly_name:
                    self.workers[mod_class.friendly_name] = mod_class
                else:
                    self.workers[module] = mod_class
            else:
                self.service_worker_map[module] = module_config[module]["worker_list"]
                self.service_info[module] = module_config[module]["class"]
