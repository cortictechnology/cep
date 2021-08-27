""" 
This example demonstrates how to use OAK-D to obtain a heart rate
estimation of a person. Face detected by the oakd face detection
worker is passed to a heart rate estimation worker. The heart rate
is returned once a steady signal is identified.

"""

from curt.command import CURTCommands

# Modify these to your own workers
# Format is "<host_name>/<module_type>/<service_name>/<worker_name>"
OAKD_PIPELINE_WORKER = "charlie/vision/oakd_service/oakd_pipeline"
RGB_CAMERA_WORKER = "charlie/vision/oakd_service/oakd_rgb_camera_input"
FACE_DETECTION_WORKER = "charlie/vision/oakd_service/oakd_face_detection"
HEARTRATE_MEASURE_WORKER = "charlie/vision/vision_processor_service/heartrate_measure"

preview_width = 640
preview_heigth = 360

face_detection_nn_input_size = 300

face_detection_confidence = 0.6
detect_largest_face_only = False

CURTCommands.initialize()

oakd_pipeline_config = [
    ["add_rgb_cam_node", preview_width, preview_heigth],
    ["add_rgb_cam_preview_node"],
    [
        "add_nn_node_pipeline",
        "face_detection",
        "face-detection-retail-0004_openvino_2021.2_6shave.blob",
        face_detection_nn_input_size,
        face_detection_nn_input_size,
    ]
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

heartrate_measure_worker = CURTCommands.get_worker(
    HEARTRATE_MEASURE_WORKER
)

while True:
    rgb_frame_handler = CURTCommands.request(
        rgb_camera_worker, params=["get_rgb_frame"]
    )

    face_detection_handler = CURTCommands.request(
        face_detection_worker, params=["detect_face_pipeline", face_detection_confidence, detect_largest_face_only]
    )

    heartrate_measure_handler = CURTCommands.request(
        heartrate_measure_worker, params=[rgb_frame_handler, face_detection_handler]
    )

    heartrate = CURTCommands.get_result(heartrate_measure_handler)["dataValue"]["data"]

    print(heartrate)