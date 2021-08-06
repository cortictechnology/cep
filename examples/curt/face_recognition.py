""" 
This example demonstrates how to add and delete a person from the face recognition 
worker's database. A new person is first addedto the database. Then the face 
recognition worker can recognizethis person. The person is then deleted after 30 
frames of recognition.

"""

from curt.command import CURTCommands

# Modify these to your own workers
# Format is "<host_name>/<module_type>/<service_name>/<worker_name>"
OAKD_PIPELINE_WORKER = "charlie/vision/oakd_service/oakd_pipeline"
RGB_CAMERA_WORKER = "charlie/vision/oakd_service/oakd_rgb_camera_input"
FACE_DETECTION_WORKER = "charlie/vision/oakd_service/oakd_face_detection"
FACE_RECOGNITION_WORKER = "charlie/vision/oakd_service/oakd_face_recognition"

person_name_to_add = "Michael"

preview_width = 640
preview_heigth = 360

face_detection_nn_input_size = 300
face_landmarks_nn_input_size = 48
face_feature_nn_input_size = 112

face_detection_confidence = 0.6
detect_largest_face_only = False

CURTCommands.initialize()

oakd_pipeline_config = [
    ["add_rgb_cam_node", preview_width, preview_heigth, False],
    ["add_rgb_cam_preview_node"],
    [
        "add_nn_node_pipeline",
        "face_detection",
        "face-detection-retail-0004_openvino_2021.2_6shave.blob",
        face_detection_nn_input_size,
        face_detection_nn_input_size,
    ],
    [
        "add_nn_node",
        "face_landmarks",
        "landmarks-regression-retail-0009_openvino_2021.2_6shave.blob",
        face_landmarks_nn_input_size,
        face_landmarks_nn_input_size,
    ],
    ["add_nn_node", "face_features", "mobilefacenet.blob", face_feature_nn_input_size, face_feature_nn_input_size],
]

oakd_pipeline_worker = CURTCommands.get_worker(
    OAKD_PIPELINE_WORKER
)
config_handler = CURTCommands.config_worker(oakd_pipeline_worker, oakd_pipeline_config)
success = CURTCommands.get_result(config_handler)["dataValue"]["data"]

rgb_camera_worker = CURTCommands.get_worker(
    RGB_CAMERA_WORKER
)

face_detection_worker = CURTCommands.get_worker(
    FACE_DETECTION_WORKER
)

face_recognition_worker = CURTCommands.get_worker(
    FACE_RECOGNITION_WORKER
)

success = False
removed = False
recog_count = 0

while True:
    rgb_frame_handler = CURTCommands.request(
        rgb_camera_worker, params=["get_rgb_frame"]
    )

    face_detection_handler = CURTCommands.request(
        face_detection_worker, params=["detect_face_pipeline", face_detection_confidence, detect_largest_face_only]
    )

    if not success:
        face_recognition_handler = CURTCommands.request(
            face_recognition_worker,
            params=["add_person", person_name_to_add, rgb_frame_handler, face_detection_handler],
        )
        success = CURTCommands.get_result(face_recognition_handler)["dataValue"]["data"]
    else:
        if recog_count >= 30:
            if not removed:
                face_recognition_handler = CURTCommands.request(
                    face_recognition_worker,
                    params=["remove_person", person_name_to_add],
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
