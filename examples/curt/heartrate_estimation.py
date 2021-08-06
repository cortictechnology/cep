""" 
This example demostrate how to use OAK-D to obtain a heart rate
estimation of a person. Face detected by the oakd face detection
worker is passed to a heart rate estimation worker. The heart rate
is returned once a stead signal is identified.

"""

import time
import numpy as np
from curt.command import CURTCommands

CURTCommands.initialize()

oakd_pipeline_config = [
    ["add_rgb_cam_node", 640, 360, False],
    ["add_rgb_cam_preview_node"],
    [
        "add_nn_node_pipeline",
        "face_detection",
        "face-detection-retail-0004_openvino_2021.2_6shave.blob",
        300,
        300,
    ]
]

oakd_pipeline_worker = CURTCommands.get_worker(
    "charlie/vision/oakd_service/oakd_pipeline"
)
CURTCommands.config_worker(oakd_pipeline_worker, oakd_pipeline_config)
time.sleep(5)

rgb_camera_worker = CURTCommands.get_worker(
    "charlie/vision/oakd_service/oakd_rgb_camera_input"
)

face_detection_worker = CURTCommands.get_worker(
    "charlie/vision/oakd_service/oakd_face_detection"
)

heartrate_measure_worker = CURTCommands.get_worker(
    "charlie/vision/vision_processor_service/heartrate_measure"
)

while True:
    rgb_frame_handler = CURTCommands.request(
        rgb_camera_worker, params=["get_rgb_frame"]
    )

    face_detection_handler = CURTCommands.request(
        face_detection_worker, params=["detect_face_pipeline", 0.6, False]
    )

    heartrate_measure_handler = CURTCommands.request(
        heartrate_measure_worker, params=[rgb_frame_handler, face_detection_handler]
    )

    heartrate = CURTCommands.get_result(heartrate_measure_handler)["dataValue"]["data"]

    print(heartrate)