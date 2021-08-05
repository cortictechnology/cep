import time
import numpy as np
from curt.command import CURTCommands

CURTCommands.initialize()

oakd_pipeline_config = [
    ["add_rgb_cam_node", 640, 360, False],
    ["add_rgb_cam_preview_node"]
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
    "charlie/vision/vision_processor_service/face_detection"
)

while True:
    rgb_frame_handler = CURTCommands.request(
        rgb_camera_worker, params=["get_rgb_frame"]
    )

    face_detection_handler = CURTCommands.request(
        face_detection_worker, params=[rgb_frame_handler]
    )

    detected_face = CURTCommands.get_result(face_detection_handler)

    print(detected_face)