""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

import depthai as dai
from curt.modules.vision.utils import *
import numpy as np
import logging
import os
import time


class OAKDSpatialCalculator:
    def __init__(self):
        self.oakd_pipeline = None
        self.friendly_name = ""

    def run_inference(self, request_data):
        if request_data[0] == "set_spatial_config":
            return self.set_spatial_config(request_data[1])

        elif request_data[0] == "get_spatial_locations":
            return self.get_spatial_locations()

    def set_spatial_config(self, pts):
        if "spatial_calculator" not in self.oakd_pipeline.xlink_nodes:
            logging.warning("No such node: spatial_calculator in the pipeline")
            return None
        spatial_data_node_names = self.oakd_pipeline.xlink_nodes["spatial_calculator"]
        config = dai.SpatialLocationCalculatorConfigData()
        config.depthThresholds.lowerThreshold = 100
        config.depthThresholds.upperThreshold = 10000
        cfg = dai.SpatialLocationCalculatorConfig()
        for pt in pts:
            x = pt[0]
            y = pt[1]
            x1 = x - 0.01
            y1 = y - 0.01
            x2 = x + 0.01
            y2 = y + 0.01
            if x1 < 0:
                x1 = 0
            if y1 < 0:
                y1 = 0
            if x2 >= 1:
                x2 = 0.99
            if y2 >= 1:
                y2 = 0.99
            topLeft = dai.Point2f(x1, y1)
            bottomRight = dai.Point2f(x2, y2)
            config.roi = dai.Rect(topLeft, bottomRight)
            cfg.addROI(config)

        self.oakd_pipeline.set_input(spatial_data_node_names[0], cfg)
        return True

    def get_spatial_locations(self):
        if "spatial_calculator" not in self.oakd_pipeline.xlink_nodes:
            logging.warning("No such node: spatial_calculator in the pipeline")
            return None
        spatial_locations = []
        spatial_data_node_names = self.oakd_pipeline.xlink_nodes["spatial_calculator"]
        spatialData = self.oakd_pipeline.get_output(
            spatial_data_node_names[1]
        ).getSpatialLocations()
        for depthData in spatialData:
            location = [
                depthData.spatialCoordinates.x,
                depthData.spatialCoordinates.y,
                depthData.spatialCoordinates.z,
            ]
            spatial_locations.append(location)
        return spatial_locations
