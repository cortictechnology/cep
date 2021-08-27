""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

import depthai as dai
from curt.modules.vision.utils import *
from curt.modules.vision.oakd_node_types import OAKDNodeTypes
import numpy as np
import logging
from pathlib import Path
import threading


class OAKDPipeline:
    def __init__(self):
        self.xlink_nodes = {}
        self.device_nodes = {}
        self.nn_node_input_sizes = {}
        self.pipeline = dai.Pipeline()
        self.pipeline.setOpenVINOVersion(version=dai.OpenVINO.Version.VERSION_2021_3)
        self.face_detect_length = 256
        self.face_recognize_length = 112

        self.pipeline_started = False

        self.stream_nodes = {}
        self.node_to_display = []

        self.photo_count = 0
        self.reset = False
        self.friendly_name = ""

    def consume_func(self):
        try:
            while True:
                if self.reset:
                    break
                for node in self.stream_nodes:
                    if self.reset:
                        break
                    self.stream_nodes[node] = self.get_output(node)
        except Exception as e:
            logging.warning("***************OAKD STREAMING THREAD EXCEPTION:*************************")
            logging.warning(str(e))
            logging.warning("************************************************************************")

    def config_pipeline(self, config_data):
        if self.pipeline_started and self.device is not None:
            logging.warning("*********************RESET PIPELINE**********************")
            self.reset = True
            self.device.close()
            self.pipeline = dai.Pipeline()
            self.pipeline.setOpenVINOVersion(
                version=dai.OpenVINO.Version.VERSION_2021_3
            )
            self.xlink_nodes = {}
            self.consume_thread.join()
            self.stream_nodes = {}
            self.node_to_display = []
            self.photo_count = 0
            logging.warning("PIPELINE RESET DONE")
        for data in config_data:
            logging.warning(data)
            if data[0] == "version":
                self.config_pipeline_version(data[1])
            elif data[0] == "add_rgb_cam_node":
                self.add_rgb_cam_node(data[1], data[2])
            elif data[0] == "add_rgb_cam_preview_node":
                self.add_rgb_cam_preview_node()
            elif data[0] == "add_stereo_cam_node":
                self.add_stereo_cam_node(data[1])
            elif data[0] == "add_stereo_frame_node":
                self.add_stereo_frame_node()
            elif data[0] == "add_spatial_mobilenetSSD_node":
                self.add_spatial_mobilenetSSD_node(
                    data[1], data[2], data[3], data[4], data[5]
                )
            elif data[0] == "add_spatial_calculator_node":
                self.add_spatial_calculator_node()
            # elif data[0] == "add_spatial_detection_output_node":
            #     self.add_spatial_detection_output_node(data[1])
            # elif data[0] == "add_spatial_detection_depthmap_node":
            #     self.add_spatial_detection_depthmap_node(data[1])
            # elif data[0] == "add_spatial_detection_preview_node":
            #     self.add_spatial_detection_preview_node(data[1])
            # elif data[0] == "add_spatial_detection_depth_out":
            #     self.add_spatial_detection_depth_out(data[1])
            elif data[0] == "add_mobilenetssd_node":
                self.add_mobilenetssd_node(data[1], data[2], data[3], data[4], data[5])
            elif data[0] == "add_mobilenetssd_node_pipeline":
                self.add_mobilenetssd_node_pipeline(
                    data[1], data[2], data[3], data[4], data[5]
                )
            elif data[0] == "add_nn_node":
                self.add_nn_node(data[1], data[2], data[3], data[4])
            elif data[0] == "add_nn_node_pipeline":
                self.add_nn_node_pipeline(data[1], data[2], data[3], data[4])
        # logging.info("finished adding nodes")
        #sysLog = self.pipeline.createSystemLogger()
        #linkOut = self.pipeline.createXLinkOut()
        #linkOut.setStreamName("sysinfo")
        #sysLog.setRate(1)  # 1 Hz
        #sysLog.out.link(linkOut.input)
        # self.stream_nodes["sysinfo"] = None
        success = False
        retry_count = 0
        while not success:
            logging.warning("Retry count: " + str(retry_count))
            logging.warning("Trying to start oakd pipeline")
            success = self.start_pipeline()
            logging.warning("Pipeline success: " + str(success))
            retry_count += 1
            if retry_count > 3:
                logging.warning("Failed to start oakd pipeline")
                break
        if not success:
            return False
        self.pipeline_started = True
        self.reset = False
        logging.warning("Starting thread")
        self.consume_thread = threading.Thread(target=self.consume_func, daemon=True)
        self.consume_thread.start()
        logging.warning("Thread started")
        return True

    def config_pipeline_version(self, version):
        if version == "2021.1":
            self.pipeline.setOpenVINOVersion(version=dai.OpenVINO.Version.VERSION_2021_1)
        elif version == "2021.2":
            self.pipeline.setOpenVINOVersion(version=dai.OpenVINO.Version.VERSION_2021_2)
        elif version == "2021.3":
            self.pipeline.setOpenVINOVersion(version=dai.OpenVINO.Version.VERSION_2021_3)

    def run_inference(self, request_data):
        if request_data[-1]:
            self.node_to_display.append(request_data[1])

    def frame_norm(self, frame, bbox):
        return (
            np.clip(np.array(bbox), 0, 1)
            * np.array(frame.shape[:2] * (len(bbox) // 2))[::-1]
        ).astype(int)

    def add_rgb_cam_node(self, preview_width, preview_height):
        node_type = "rgb_camera"
        if node_type in self.xlink_nodes:
            logging.warning(node_type + " already exists in pipeline.")
            return
        rgb_cam = self.pipeline.createColorCamera()
        # rgb_cam.setStillSize(1280, 720)
        rgb_cam.setPreviewSize(preview_width, preview_height)
        rgb_cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
        rgb_cam.setIspScale(2, 3)
        # rgb_cam.setPreviewKeepAspectRatio(False)
        rgb_cam.setInterleaved(False)
        # if rgb_order:
        #     rgb_cam.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)
        # else:
        #     rgb_cam.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)

        self.device_nodes[node_type] = rgb_cam

        controlIn = self.pipeline.createXLinkIn()
        controlIn.setStreamName("control")
        controlIn.out.link(rgb_cam.inputControl)
        rgb_cam_still_out = self.pipeline.createXLinkOut()
        rgb_cam_still_out.setStreamName("still")
        rgb_cam.still.link(rgb_cam_still_out.input)

    def add_rgb_cam_preview_node(self):
        node_type = "rgb_camera"
        if node_type not in self.device_nodes:
            logging.warning(
                "No existing rgb node found in pipeline, cannot add rgb frame node."
            )
            return
        rgb_cam_out = self.pipeline.createXLinkOut()
        rgb_cam_out.setStreamName(node_type)
        self.device_nodes[node_type].preview.link(rgb_cam_out.input)
        self.xlink_nodes[node_type] = ["", node_type]
        self.stream_nodes[node_type] = None

    def add_stereo_cam_node(self, align_rgb):
        node_type = "stereo_camera"
        if node_type in self.xlink_nodes:
            logging.warning(node_type + " already exists in pipeline.")
            return
        monoLeft = self.pipeline.createMonoCamera()
        monoRight = self.pipeline.createMonoCamera()
        monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        monoLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
        monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        monoRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)
        stereo = self.pipeline.createStereoDepth()
        stereo.setConfidenceThreshold(240)
        if align_rgb:
            self.device_nodes["rgb_camera"].setBoardSocket(dai.CameraBoardSocket.RGB)
            self.device_nodes["rgb_camera"].initialControl.setManualFocus(130)
            stereo.setLeftRightCheck(True)
            stereo.setSubpixel(False)
            stereo.setDepthAlign(dai.CameraBoardSocket.RGB)
        monoLeft.out.link(stereo.left)
        monoRight.out.link(stereo.right)
        self.device_nodes[node_type] = stereo

    def add_stereo_frame_node(self):
        node_type = "stereo_camera"
        if node_type not in self.device_nodes:
            logging.warning(
                "No existing stereo node found in pipeline, cannot add stereo frame node."
            )
            return
        stereo_out = self.pipeline.createXLinkOut()
        stereo_out.setStreamName(node_type)
        self.device_nodes[node_type].disparity.link(stereo_out.input)
        self.xlink_nodes[node_type] = ["", node_type]
        # self.xlink_nodes.append(stereo_node_name)
        self.stream_nodes[node_type] = None

    def add_spatial_mobilenetSSD_node(
        self, node_type, nn_name, input_width, input_height, threshold
    ):
        if node_type not in OAKDNodeTypes:
            logging.warning(node_type + " does not supported.")
            return
        if node_type in self.xlink_nodes:
            logging.warning(node_type + " already exists in pipeline.")
            return
        if "rgb_camera" not in self.device_nodes:
            logging.warning(
                "No existing rgb node found in pipeline, cannot add spatial mobilenetSSD node."
            )
            return
        if "stereo_camera" not in self.device_nodes:
            logging.warning(
                "No existing stereo node found in pipeline, cannot add spatial mobilenetSSD node."
            )
            return

        manip = self.pipeline.createImageManip()
        manip.initialConfig.setResize(input_width, input_height)
        manip.setKeepAspectRatio(False)
        self.device_nodes["rgb_camera"].preview.link(manip.inputImage)

        spatialDetectionNetwork = self.pipeline.createMobileNetSpatialDetectionNetwork()
        spatialDetectionNetwork.setBlobPath(
            str(Path("/models/oakd/" + nn_name).resolve().absolute())
        )
        spatialDetectionNetwork.setConfidenceThreshold(threshold)
        spatialDetectionNetwork.input.setBlocking(False)
        spatialDetectionNetwork.setBoundingBoxScaleFactor(0.5)
        spatialDetectionNetwork.setDepthLowerThreshold(100)
        spatialDetectionNetwork.setDepthUpperThreshold(5000)
        manip.out.link(spatialDetectionNetwork.input)
        self.device_nodes["stereo_camera"].depth.link(
            spatialDetectionNetwork.inputDepth
        )
        self.device_nodes[node_type] = spatialDetectionNetwork

        detection_out = self.pipeline.createXLinkOut()
        detection_out.setStreamName(node_type + "_detections")
        self.device_nodes[node_type].out.link(detection_out.input)
        self.xlink_nodes[node_type] = ["", node_type + "_detections"]
        # self.xlink_nodes.append(node_name + "_detections")
        self.stream_nodes[node_type + "_detections"] = None

    # def add_spatial_detection_output_node(self, spatial_detection_node_name):
    #     detection_out = self.pipeline.createXLinkOut()
    #     detection_out.setStreamName(spatial_detection_node_name + "_detections")
    #     self.device_nodes[spatial_detection_node_name].out.link(detection_out.input)
    #     self.xlink_nodes.append(spatial_detection_node_name + "_detections")
    #     self.stream_nodes[spatial_detection_node_name + "_detections"] = None

    # def add_spatial_detection_depthmap_node(self, spatial_detection_node_name):
    #     detection_depth_mapping = self.pipeline.createXLinkOut()
    #     detection_depth_mapping.setStreamName(
    #         spatial_detection_node_name + "_depth_mapping"
    #     )
    #     self.device_nodes[spatial_detection_node_name].boundingBoxMapping.link(
    #         detection_depth_mapping.input
    #     )
    #     self.xlink_nodes.append(spatial_detection_node_name + "_depth_mapping")
    #     self.stream_nodes[spatial_detection_node_name + "_depth_mapping"] = None

    # def add_spatial_detection_preview_node(self, spatial_detection_node_name):
    #     cam_out = self.pipeline.createXLinkOut()
    #     cam_out.setStreamName(spatial_detection_node_name + "_preview")
    #     self.device_nodes[spatial_detection_node_name].passthrough.link(cam_out.input)
    #     self.xlink_nodes.append(spatial_detection_node_name + "_preview")
    #     self.stream_nodes[spatial_detection_node_name + "_preview"] = None

    # def add_spatial_detection_depth_out(self, spatial_detection_node_name):
    #     depth_out = self.pipeline.createXLinkOut()
    #     depth_out.setStreamName(spatial_detection_node_name + "_depth")
    #     self.device_nodes[spatial_detection_node_name].passthroughDepth.link(
    #         depth_out.input
    #     )
    #     self.xlink_nodes.append(spatial_detection_node_name + "_depth")
    #     self.stream_nodes[spatial_detection_node_name + "_depth"] = None

    def add_mobilenetssd_node(
        self, node_type, nn_name, input_width, input_height, threshold
    ):
        if node_type not in OAKDNodeTypes:
            logging.warning(node_type + " does not supported.")
            return
        if node_type in self.xlink_nodes:
            logging.warning(node_type + " already exists in pipeline.")
            return
        nn = self.pipeline.createMobileNetDetectionNetwork()
        nn.setConfidenceThreshold(threshold)
        nn.setBlobPath(str(Path("/models/oakd/" + nn_name).resolve().absolute()))
        nn.setNumInferenceThreads(2)
        nn_in = self.pipeline.createXLinkIn()
        nn_in.setStreamName(node_type + "_in")
        nn_in.out.link(nn.input)
        nn_out = self.pipeline.createXLinkOut()
        nn_out.setStreamName(node_type + "_out")
        nn.out.link(nn_out.input)
        self.xlink_nodes[node_type] = [node_type + "_in", node_type + "_out"]
        # self.xlink_nodes.append(node_name + "_in")
        # self.xlink_nodes.append(node_name + "_out")
        self.nn_node_input_sizes[node_type] = [input_width, input_height]

    def add_mobilenetssd_node_pipeline(
        self, node_type, nn_name, input_width, input_height, threshold
    ):
        if node_type not in OAKDNodeTypes:
            logging.warning(node_type + " does not supported.")
            return
        if node_type in self.xlink_nodes:
            logging.warning(node_type + " already exists in pipeline.")
            return
        if "rgb_camera" not in self.xlink_nodes:
            logging.warning(
                "No existing rgb node found in pipeline, cannot add spatial mobilenetSSD node."
            )
            return
        manip = self.pipeline.createImageManip()
        manip.initialConfig.setResize(input_width, input_height)
        manip.setKeepAspectRatio(False)
        self.device_nodes["rgb_camera"].preview.link(manip.inputImage)

        nn = self.pipeline.createMobileNetDetectionNetwork()
        nn.setConfidenceThreshold(threshold)
        nn.setBlobPath(str(Path("/models/oakd/" + nn_name).resolve().absolute()))
        nn.setNumInferenceThreads(2)
        manip.out.link(nn.input)
        nn_out = self.pipeline.createXLinkOut()
        nn_out.setStreamName(node_type + "_out")
        nn.out.link(nn_out.input)
        self.xlink_nodes[node_type] = ["", node_type + "_out"]
        self.stream_nodes[node_type + "_out"] = None

    def add_nn_node(self, node_type, nn_name, input_width, input_height):
        if node_type not in OAKDNodeTypes:
            logging.warning(node_type + " does not supported.")
            return
        if node_type in self.xlink_nodes:
            logging.warning(node_type + " already exists in pipeline.")
            return
        if node_type == "body_detection" or node_type == "body_landmarks":
            self.pipeline.setOpenVINOVersion(
                version=dai.OpenVINO.Version.VERSION_2021_3
            )
        nn = self.pipeline.createNeuralNetwork()
        nn.setBlobPath(str(Path("/models/oakd/" + nn_name).resolve().absolute()))
        nn.setNumInferenceThreads(2)
        nn_in = self.pipeline.createXLinkIn()
        nn_in.setStreamName(node_type + "_in")
        nn_in.out.link(nn.input)
        nn_out = self.pipeline.createXLinkOut()
        nn_out.setStreamName(node_type + "_out")
        nn.out.link(nn_out.input)
        self.xlink_nodes[node_type] = [node_type + "_in", node_type + "_out"]
        self.nn_node_input_sizes[node_type] = [input_width, input_height]

    def add_nn_node_pipeline(self, node_type, nn_name, input_width, input_height):
        if node_type not in OAKDNodeTypes:
            logging.warning(node_type + " does not supported.")
            return
        if node_type in self.xlink_nodes:
            logging.warning(node_type + " already exists in pipeline.")
            return
        if "rgb_camera" not in self.xlink_nodes:
            logging.warning(
                "No existing rgb node found in pipeline, cannot add spatial mobilenetSSD node."
            )
            return
        manip = self.pipeline.createImageManip()
        manip.initialConfig.setResize(input_width, input_height)
        manip.setKeepAspectRatio(False)
        self.device_nodes["rgb_camera"].preview.link(manip.inputImage)

        nn = self.pipeline.createNeuralNetwork()
        nn.setBlobPath(str(Path("/models/oakd/" + nn_name).resolve().absolute()))
        nn.setNumInferenceThreads(2)
        manip.out.link(nn.input)
        nn_out = self.pipeline.createXLinkOut()
        nn_out.setStreamName(node_type + "_out")
        nn.out.link(nn_out.input)
        self.xlink_nodes[node_type] = ["", node_type + "_out"]
        self.stream_nodes[node_type + "_out"] = None

    def add_spatial_calculator_node(self):
        if "spatial_calculator" in self.xlink_nodes:
            logging.warning("spatial_calculator node already exists in pipeline.")
            return
        if "stereo_camera" not in self.device_nodes:
            logging.warning(
                "No existing stereo node found in pipeline, cannot add spatial mobilenetSSD node."
            )
            return
        spatialLocationCalculator = self.pipeline.createSpatialLocationCalculator()
        # Config
        topLeft = dai.Point2f(0, 0)
        bottomRight = dai.Point2f(0, 0)

        config = dai.SpatialLocationCalculatorConfigData()
        config.depthThresholds.lowerThreshold = 100
        config.depthThresholds.upperThreshold = 10000
        config.roi = dai.Rect(topLeft, bottomRight)

        spatialLocationCalculator.setWaitForConfigInput(False)
        spatialLocationCalculator.initialConfig.addROI(config)

        self.device_nodes["stereo_camera"].depth.link(
            spatialLocationCalculator.inputDepth
        )
        self.device_nodes["spatial_calculator"] = spatialLocationCalculator

        # Currently we use the 'disparity' output. TODO 'depth'
        xoutSpatialData = self.pipeline.createXLinkOut()
        xinSpatialCalcConfig = self.pipeline.createXLinkIn()
        xoutSpatialData.setStreamName("spatial_calculator_out")
        xinSpatialCalcConfig.setStreamName("spatial_calculator_in")

        spatialLocationCalculator.out.link(xoutSpatialData.input)
        xinSpatialCalcConfig.out.link(spatialLocationCalculator.inputConfig)

        self.xlink_nodes["spatial_calculator"] = [
            "spatial_calculator_in",
            "spatial_calculator_out",
        ]

    def set_input(self, node_name, input_data):
        node_in = self.device.getInputQueue(name=node_name, maxSize=4, blocking=False)
        node_in.send(input_data)

    def get_output(self, node_name, just_try=False):
        if self.reset:
            return
        node_out = self.device.getOutputQueue(name=node_name, maxSize=4, blocking=False)
        if not just_try:
            output_data = node_out.get()
        else:
            output_data = node_out.tryGet()
        return output_data

    def start_pipeline(self):
        success = True
        logging.info("Creating OAK-D device")
        self.device = dai.Device(self.pipeline)
        if self.device.isClosed():
            success = False
        self.device.startPipeline()
        logging.info("Started OAK-D Pipeline")
        return success
