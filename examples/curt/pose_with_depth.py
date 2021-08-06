""" 
This example demostrate the use of rgb and stereo camera to obtain the 
sparial location of a human pose.
The rgb frame is passed to a pose estimation worker, the otained body 
landmarks are then passed to a spatial calcultor worker to obtain the 
spatial locations.

""" 

import numpy as np
from curt.command import CURTCommands

# Modify these to your own workers
# Format is "<host_name>/<module_type>/<service_name>/<worker_name>"
OAKD_PIPELINE_WORKER = "charlie/vision/oakd_service/oakd_pipeline"
RGB_CAMERA_WORKER = "charlie/vision/oakd_service/oakd_rgb_camera_input"
BODY_LANDMARKS_WORKER =  "charlie/vision/oakd_service/oakd_pose_estimation"
SPATIAL_CALCULATOR_WORKER = "charlie/vision/oakd_service/oakd_spatial_calculator"

preview_width = 640
preview_heigth = 360

body_detection_nn_input_size = 224
body_landmarks_nn_input_size = 256

CURTCommands.initialize()

oakd_pipeline_config = [
    ["add_rgb_cam_node", preview_width, preview_heigth, False],
    ["add_rgb_cam_preview_node"],
    ["add_stereo_cam_node", True],
    ["add_nn_node", "body_detection", "pose_detection_sh6.blob", body_detection_nn_input_size, body_detection_nn_input_size],
    ["add_nn_node", "body_landmarks", "pose_landmark_lite_sh6.blob", body_landmarks_nn_input_size, body_landmarks_nn_input_size],
    ["add_spatial_calculator_node"],
]

oakd_pipeline_worker = CURTCommands.get_worker(
    OAKD_PIPELINE_WORKER
)
config_handler = CURTCommands.config_worker(oakd_pipeline_worker, oakd_pipeline_config)
success = CURTCommands.get_result(config_handler)["dataValue"]["data"]

rgb_camera_worker = CURTCommands.get_worker(
    RGB_CAMERA_WORKER
)

body_landmarks_worker = CURTCommands.get_worker(
    BODY_LANDMARKS_WORKER
)

spatial_calculator_worker = CURTCommands.get_worker(
    SPATIAL_CALCULATOR_WORKER
)

while True:
    rgb_frame_handler = CURTCommands.request(
        rgb_camera_worker, params=["get_rgb_frame"]
    )

    body_landmarks_handler = CURTCommands.request(
        body_landmarks_worker, params=[rgb_frame_handler]
    )

    body_landmarks_results = CURTCommands.get_result(body_landmarks_handler)[
        "dataValue"
    ]["data"]

    if body_landmarks_results is not None:
        body_landmarks_results = np.array(body_landmarks_results)
        body_landmarks_xy = body_landmarks_results[:, :2].tolist()
        body_spatial_location_config_handler = CURTCommands.request(
            spatial_calculator_worker, params=["set_spatial_config", body_landmarks_xy]
        )
        body_spatial_location_handler = CURTCommands.request(
            spatial_calculator_worker, params=["get_spatial_locations"]
        )

        body_spatial_locations = CURTCommands.get_result(body_spatial_location_handler)[
            "dataValue"
        ]["data"]
