""" 
This example demostrate how to accelerate a facemesh estimation operation
using multiple oak-d cameras. Frames are grab by one oak-d camera in constant
time. Then they are send to 3 oak-d camera for inference with a offset from each
other. The offset is measured and calculated such that after the first 5 frames,
each result can be retrieved in a constant time. This constant time is shorter
than the original inference time on one single oak-d camera.

"""

import time
import numpy as np
import queue
import threading
import cv2
import base64
from curt.command import CURTCommands

# Modify these to your own workers
# Format is "<host_name>/<module_type>/<service_name>/<worker_name>"
CHARLIE_PIPELINE_WORKER = "charlie/vision/oakd_service/oakd_pipeline"
OAKD2_PIPELINE_WORKER = "oakd2/vision/oakd_service/oakd_pipeline"
OAKD3_PIPELINE_WORKER = "oakd3/vision/oakd_service/oakd_pipeline"
RGB_CAMERA_WORKER = "charlie/vision/oakd_service/oakd_rgb_camera_input"
FACE_DETECTION_WORKER = "charlie/vision/oakd_service/oakd_face_detection"
FACEMESH_WORKER_1 = "charlie/vision/oakd_service/oakd_facemesh"
FACEMESH_WORKER_2 = "oakd2/vision/oakd_service/oakd_facemesh"
FACEMESH_WORKER_3 = "oakd3/vision/oakd_service/oakd_facemesh"

preview_width = 640
preview_heigth = 360

face_detection_nn_input_size = 300
facemesh_nn_input_size = 192

face_detection_confidence = 0.6
detect_largest_face_only = False

target_fps = 25
result_queue = queue.Queue()
frame_queue = queue.Queue()
frame_handler_queue = queue.Queue()

CURTCommands.initialize()

charlie_pipeline_config = [
    ["add_rgb_cam_node", preview_width, preview_heigth, False],
    ["add_rgb_cam_preview_node"],
    [
        "add_nn_node_pipeline",
        "face_detection",
        "face-detection-retail-0004_openvino_2021.2_6shave.blob",
        face_detection_nn_input_size,
        face_detection_nn_input_size,
    ],
    ["add_nn_node", "facemesh", "facemesh_sh6.blob", facemesh_nn_input_size, facemesh_nn_input_size],
]

oakd2_pipeline_config = [["add_nn_node", "facemesh", "facemesh_sh6.blob", facemesh_nn_input_size, facemesh_nn_input_size]]

oakd3_pipeline_config = [["add_nn_node", "facemesh", "facemesh_sh6.blob", facemesh_nn_input_size, facemesh_nn_input_size]]

charlie_pipeline_worker = CURTCommands.get_worker(
    CHARLIE_PIPELINE_WORKER
)

oakd2_pipeline_worker = CURTCommands.get_worker(
    OAKD2_PIPELINE_WORKER
)

oakd3_pipeline_worker = CURTCommands.get_worker(
    OAKD3_PIPELINE_WORKER
)

config_handler_1 = CURTCommands.config_worker(charlie_pipeline_worker, charlie_pipeline_config)
config_handler_2 = CURTCommands.config_worker(oakd2_pipeline_worker, oakd2_pipeline_config)
config_handler_3 = CURTCommands.config_worker(oakd3_pipeline_worker, oakd3_pipeline_config)

success = CURTCommands.get_result(config_handler_1)["dataValue"]["data"]
success = CURTCommands.get_result(config_handler_2)["dataValue"]["data"]
success = CURTCommands.get_result(config_handler_3)["dataValue"]["data"]


def display_func():
    global result_queue
    global frame_queue
    while True:
        frame = frame_queue.get()
        result = result_queue.get()


def grab_frame_func():
    global frame_handler_queue
    global frame_queue
    while True:
        frame_handler = frame_handler_queue.get()
        # print(frame_handler.name)
        image_data = CURTCommands.get_result(frame_handler)
        # print(image_data["dataValue"]["worker"])
        jpg_original = base64.b64decode(image_data["dataValue"]["data"])
        jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
        frame = cv2.imdecode(jpg_as_np, flags=1)
        # print(frame.shape)
        frame_queue.put(frame)


if __name__ == "__main__":

    display_thread = threading.Thread(target=display_func, daemon=True)
    grab_frame_thread = threading.Thread(target=grab_frame_func, daemon=True)

    display_thread.start()
    grab_frame_thread.start()

    facemesh_handler_queue = queue.Queue()

    rgb_camera_worker = CURTCommands.get_worker(
        RGB_CAMERA_WORKER
    )

    face_detection_worker = CURTCommands.get_worker(
        FACE_DETECTION_WORKER
    )

    facemesh_worker1 = CURTCommands.get_worker(
        FACEMESH_WORKER_1
    )

    facemesh_worker2 = CURTCommands.get_worker(
        FACEMESH_WORKER_2
    )

    facemesh_worker3 = CURTCommands.get_worker(
        FACEMESH_WORKER_3
    )

    rgb_frame_handler = CURTCommands.request(
        rgb_camera_worker, params=["get_rgb_frame"]
    )

    face_detection_handler = CURTCommands.request(
        face_detection_worker, params=["detect_face_pipeline", face_detection_confidence, detect_largest_face_only]
    )

    facemesh_handler_1 = CURTCommands.request(
        facemesh_worker1,
        params=[rgb_frame_handler, face_detection_handler],
        listen_to_handler=True,
    )

    frame_handler_queue.put(rgb_frame_handler)

    facemesh_handler_queue.put([facemesh_handler_1, facemesh_worker1])

    time.sleep(1.0 / target_fps)

    rgb_frame_handler = CURTCommands.request(
        rgb_camera_worker, params=["get_rgb_frame"]
    )

    face_detection_handler = CURTCommands.request(
        face_detection_worker, params=["detect_face_pipeline", face_detection_confidence, detect_largest_face_only]
    )

    facemesh_handler_2 = CURTCommands.request(
        facemesh_worker2, params=[rgb_frame_handler, face_detection_handler]
    )

    frame_handler_queue.put(rgb_frame_handler)

    facemesh_handler_queue.put([facemesh_handler_2, facemesh_worker2])

    time.sleep(1.0 / target_fps)

    rgb_frame_handler = CURTCommands.request(
        rgb_camera_worker, params=["get_rgb_frame"]
    )

    face_detection_handler = CURTCommands.request(
        face_detection_worker, params=["detect_face_pipeline", face_detection_confidence, detect_largest_face_only]
    )

    facemesh_handler_1 = CURTCommands.request(
        facemesh_worker1, params=[rgb_frame_handler, face_detection_handler]
    )

    frame_handler_queue.put(rgb_frame_handler)

    facemesh_handler_queue.put([facemesh_handler_1, facemesh_worker1])

    time.sleep(1.0 / target_fps)

    rgb_frame_handler = CURTCommands.request(
        rgb_camera_worker, params=["get_rgb_frame"]
    )

    face_detection_handler = CURTCommands.request(
        face_detection_worker, params=["detect_face_pipeline", face_detection_confidence, detect_largest_face_only]
    )

    facemesh_handler_3 = CURTCommands.request(
        facemesh_worker3, params=[rgb_frame_handler, face_detection_handler]
    )

    frame_handler_queue.put(rgb_frame_handler)

    facemesh_handler_queue.put([facemesh_handler_3, facemesh_worker3])

    time.sleep(1.0 / target_fps)

    rgb_frame_handler = CURTCommands.request(
        rgb_camera_worker, params=["get_rgb_frame"]
    )

    face_detection_handler = CURTCommands.request(
        face_detection_worker, params=["detect_face_pipeline", face_detection_confidence, detect_largest_face_only]
    )

    facemesh_handler_1 = CURTCommands.request(
        facemesh_worker1, params=[rgb_frame_handler, face_detection_handler]
    )

    frame_handler_queue.put(rgb_frame_handler)

    facemesh_handler_queue.put([facemesh_handler_1, facemesh_worker1])

    frame_count = 0
    start_time = time.time()

    while not facemesh_handler_queue.empty():
        elapsed_time = time.time() - start_time
        if elapsed_time >= 1:
            print("FPS:", frame_count / elapsed_time)
            frame_count = 0
            start_time = time.time()

        facemesh_handler, facemesh_worker = facemesh_handler_queue.get()
        facemesh_result = CURTCommands.get_result(facemesh_handler)["dataValue"]["data"]
        frame_count = frame_count + 1
        result_queue.put(facemesh_result)

        rgb_frame_handler = CURTCommands.request(
            rgb_camera_worker, params=["get_rgb_frame"]
        )

        face_detection_handler = CURTCommands.request(
            face_detection_worker, params=["detect_face_pipeline", face_detection_confidence, detect_largest_face_only]
        )

        facemesh_handler = CURTCommands.request(
            facemesh_worker, params=[rgb_frame_handler, face_detection_handler]
        )

        frame_handler_queue.put(rgb_frame_handler)

        facemesh_handler_queue.put([facemesh_handler, facemesh_worker])

        time.sleep(1.0 / target_fps)
