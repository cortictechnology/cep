import time
import numpy as np
from curt.command import CURTCommands

CURTCommands.initialize()

oakd_pipeline_config = [
    ["add_rgb_cam_node", 640, 360, False],
    ["add_rgb_cam_preview_node"],
    ["add_stereo_cam_node", True],
    ["add_nn_node", "body_detection", "pose_detection_sh6.blob", 224, 224],
    ["add_nn_node", "body_landmarks", "pose_landmark_lite_sh6.blob", 256, 256],
    ["add_spatial_calculator_node"],
]

oakd_pipeline_worker = CURTCommands.get_worker(
    "charlie/vision/oakd_service/oakd_pipeline"
)
CURTCommands.config_worker(oakd_pipeline_worker, oakd_pipeline_config)
time.sleep(4)

rgb_camera_worker = CURTCommands.get_worker(
    "charlie/vision/oakd_service/oakd_rgb_camera_input"
)

# face_detection_worker = CURTCommands.get_worker(
#     "charlie/vision/oakd_service/oakd_face_detection"
# )

body_landmarks_worker = CURTCommands.get_worker(
    "charlie/vision/oakd_service/oakd_pose_estimation"
)

spatial_calculator_worker = CURTCommands.get_worker(
    "charlie/vision/oakd_service/oakd_spatial_calculator"
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

# oakd_pipeline_config = [
#     ["add_rgb_cam_node", 640, 360, False],
#     ["add_rgb_cam_preview_node"],
#     [
#         "add_nn_node_pipeline",
#         "face_detection",
#         "face-detection-retail-0004_openvino_2021.2_6shave.blob",
#         300,
#         300,
#     ],
# ]

# oakd_pipeline_worker = CURTCommands.get_worker(
#     "charlie/vision/oakd_service/oakd_pipeline"
# )
# CURTCommands.config_worker(oakd_pipeline_worker, oakd_pipeline_config)
# time.sleep(4)

# rgb_camera_worker = CURTCommands.get_worker(
#     "charlie/vision/oakd_service/oakd_rgb_camera_input"
# )

# face_detection_worker = CURTCommands.get_worker(
#     "charlie/vision/oakd_service/oakd_face_detection"
# )

# rgb_frame_handler = CURTCommands.request(rgb_camera_worker, params=["get_rgb_frame"])

# face_detection_handler = CURTCommands.request(
#     face_detection_worker, params=["detect_face_pipeline", 0.6, False]
# )

# face_detection_results = CURTCommands.get_result(face_detection_handler)

# print(face_detection_results)
