""" 
This example demonstrates the use of USB webcam with a Raspberry Pi 
face detector.

""" 

from curt.command import CURTCommands

# Modify these to your own workers
# Format is "<host_name>/<module_type>/<service_name>/<worker_name>"
RGB_CAMERA_WORKER = "charlie/vision/vision_input_service/webcam_input"
FACE_DETECTION_WORKER = "charlie/vision/vision_processor_service/face_detection"

preview_width = 640
preview_heigth = 480

CURTCommands.initialize()

rgb_camera_worker = CURTCommands.get_worker(
    RGB_CAMERA_WORKER
)

rgb_camera_config = {
                     "camera_index": 0,
                     "capture_width": 640,
                     "capture_height": 480
                    }

config_handler = CURTCommands.config_worker(rgb_camera_worker, rgb_camera_config)
success = CURTCommands.get_result(config_handler)["dataValue"]["data"]

face_detection_worker = CURTCommands.get_worker(
    FACE_DETECTION_WORKER
)

while True:
    rgb_frame_handler = CURTCommands.request(
        rgb_camera_worker, params=[False]
    )

    face_detection_handler = CURTCommands.request(
        face_detection_worker, params=[rgb_frame_handler]
    )

    detected_face = CURTCommands.get_result(face_detection_handler)

    print(detected_face)