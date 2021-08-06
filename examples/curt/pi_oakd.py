""" 
This example demonstrates the use of OAK-D camera with a Raspberry Pi 
face detector.

""" 

from curt.command import CURTCommands

# Modify these to your own workers
# Format is "<host_name>/<module_type>/<service_name>/<worker_name>"
OAKD_PIPELINE_WORKER = "charlie/vision/oakd_service/oakd_pipeline"
RGB_CAMERA_WORKER = "charlie/vision/oakd_service/oakd_rgb_camera_input"
FACE_DETECTION_WORKER = "charlie/vision/vision_processor_service/face_detection"

preview_width = 640
preview_heigth = 360

CURTCommands.initialize()

oakd_pipeline_config = [
    ["add_rgb_cam_node", preview_width, preview_heigth, False],
    ["add_rgb_cam_preview_node"]
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

while True:
    rgb_frame_handler = CURTCommands.request(
        rgb_camera_worker, params=["get_rgb_frame"]
    )

    face_detection_handler = CURTCommands.request(
        face_detection_worker, params=[rgb_frame_handler]
    )

    detected_face = CURTCommands.get_result(face_detection_handler)

    print(detected_face)