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

target_fps = 26
result_queue = queue.Queue()
frame_queue = queue.Queue()
frame_handler_queue = queue.Queue()

CURTCommands.initialize()

charlie_pipeline_config = [
    ["add_rgb_cam_node", 640, 360, False],
    ["add_rgb_cam_preview_node"],
    [
        "add_nn_node_pipeline",
        "face_detection",
        "face-detection-retail-0004_openvino_2021.2_6shave.blob",
        300,
        300,
    ],
    ["add_nn_node", "facemesh", "facemesh_sh6.blob", 192, 192],
]

oakd2_pipeline_config = [["add_nn_node", "facemesh", "facemesh_sh6.blob", 192, 192]]

oakd3_pipeline_config = [["add_nn_node", "facemesh", "facemesh_sh6.blob", 192, 192]]

charlie_pipeline_worker = CURTCommands.get_worker(
    "charlie/vision/oakd_service/oakd_pipeline"
)

oakd2_pipeline_worker = CURTCommands.get_worker(
    "oakd2/vision/oakd_service/oakd_pipeline"
)

oakd3_pipeline_worker = CURTCommands.get_worker(
    "oakd3/vision/oakd_service/oakd_pipeline"
)

CURTCommands.config_worker(charlie_pipeline_worker, charlie_pipeline_config)
CURTCommands.config_worker(oakd2_pipeline_worker, oakd2_pipeline_config)
CURTCommands.config_worker(oakd3_pipeline_worker, oakd3_pipeline_config)


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
        "charlie/vision/oakd_service/oakd_rgb_camera_input"
    )

    face_detection_worker = CURTCommands.get_worker(
        "charlie/vision/oakd_service/oakd_face_detection"
    )

    facemesh_worker1 = CURTCommands.get_worker(
        "charlie/vision/oakd_service/oakd_facemesh"
    )

    facemesh_worker2 = CURTCommands.get_worker(
        "oakd2/vision/oakd_service/oakd_facemesh"
    )

    facemesh_worker3 = CURTCommands.get_worker(
        "oakd3/vision/oakd_service/oakd_facemesh"
    )

    rgb_frame_handler = CURTCommands.request(
        rgb_camera_worker, params=["get_rgb_frame"]
    )

    face_detection_handler = CURTCommands.request(
        face_detection_worker, params=["detect_face_pipeline", 0.6, False]
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
        face_detection_worker, params=["detect_face_pipeline", 0.6, False]
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
        face_detection_worker, params=["detect_face_pipeline", 0.6, False]
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
        face_detection_worker, params=["detect_face_pipeline", 0.6, False]
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
        face_detection_worker, params=["detect_face_pipeline", 0.6, False]
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
            face_detection_worker, params=["detect_face_pipeline", 0.6, False]
        )

        facemesh_handler = CURTCommands.request(
            facemesh_worker, params=[rgb_frame_handler, face_detection_handler]
        )

        frame_handler_queue.put(rgb_frame_handler)

        facemesh_handler_queue.put([facemesh_handler, facemesh_worker])

        time.sleep(1.0 / target_fps)
