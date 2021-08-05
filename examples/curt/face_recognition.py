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
    ],
    [
        "add_nn_node",
        "face_landmarks",
        "landmarks-regression-retail-0009_openvino_2021.2_6shave.blob",
        48,
        48,
    ],
    ["add_nn_node", "face_features", "mobilefacenet.blob", 112, 112],
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

face_recognition_worker = CURTCommands.get_worker(
    "charlie/vision/oakd_service/oakd_face_recognition"
)

success = False
removed = False
recog_count = 0

while True:
    rgb_frame_handler = CURTCommands.request(
        rgb_camera_worker, params=["get_rgb_frame"]
    )

    face_detection_handler = CURTCommands.request(
        face_detection_worker, params=["detect_face_pipeline", 0.6, False]
    )

    if not success:
        face_recognition_handler = CURTCommands.request(
            face_recognition_worker,
            params=["add_person", "Michael", rgb_frame_handler, face_detection_handler],
        )
        success = CURTCommands.get_result(face_recognition_handler)["dataValue"]["data"]
    else:
        if recog_count >= 30:
            if not removed:
                face_recognition_handler = CURTCommands.request(
                    face_recognition_worker,
                    params=["remove_person", "Michael"],
                )
                removed = CURTCommands.get_result(face_recognition_handler)[
                    "dataValue"
                ]["data"]

        face_recognition_handler = CURTCommands.request(
            face_recognition_worker,
            params=["recognize_face", rgb_frame_handler, face_detection_handler],
        )
        identities = CURTCommands.get_result(face_recognition_handler)["dataValue"][
            "data"
        ]
        recog_count = recog_count + 1
        print(identities)
