""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, March 2021

"""

import curt.modules.vision.depthai as dai
from curt.modules.vision.utils import *
import numpy as np
import logging
import os
import time


class OAKDSysinfo:
    def __init__(self):
        self.oakd_pipeline = None
        self.friendly_name = ""

    def config_pipeline(self, config_data):
        pass

    def config_pipeline_version(self, version):
        pass

    def run_inference(self, request_data):
        if request_data[0] == "get_sysinfo":
            return self.get_sysinfo()

    def get_sysinfo(self):
        info = self.oakd_pipeline.get_output("sysinfo", just_try=True)
        if info is not None:
            m = 1024 * 1024
            used_ddr_memory = round(info.ddrMemoryUsage.used / m, 2)
            total_ddr_memory = round(info.ddrMemoryUsage.total / m, 2)
            used_cmx_memory = round(info.cmxMemoryUsage.used / m, 2)
            total_cmx_memory = round(info.cmxMemoryUsage.total / m, 2)
            used_leoncss_memory = round(info.leonCssMemoryUsage.used / m, 2)
            total_leoncss_memory = round(info.leonCssMemoryUsage.total / m, 2)
            used_leonmss_memory = round(info.leonMssMemoryUsage.used / m, 2)
            total_leonmss_memory = round(info.leonMssMemoryUsage.total / m, 2)
            avg_temp = round(info.chipTemperature.average, 2)
            leon_os_cpu_usage = round(info.leonCssCpuUsage.average * 100, 2)
            leon_rt_cpu_usage = round(info.leonMssCpuUsage.average * 100, 2)
            return [
                used_ddr_memory,
                total_ddr_memory,
                used_cmx_memory,
                total_cmx_memory,
                used_leoncss_memory,
                total_leoncss_memory,
                used_leonmss_memory,
                total_leonmss_memory,
                avg_temp,
                leon_os_cpu_usage,
                leon_rt_cpu_usage,
            ]
        else:
            return []
