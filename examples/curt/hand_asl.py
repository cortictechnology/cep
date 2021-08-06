""" 
This example demostrate the use of a newly implemented oak-d worker: hand_asl
To implement a new worker, please refer to the following steps:
1. Define a new oak-d node type in:
<cep_root>/src/curt/curt/modules/vision/oakd_node_types.py
In this example, the new type is "hand_asl"
2. Implement the actual logic of the worker in: 
<cep_root>/src/curt/curt/modules/vision/oakd_hand_asl.py 
3. Add this new woker in: 
<cep_root>/src/curt/curt/module_configs.json
In this example, a new worker "oakd_hand_asl" and its class 
name "OAKDASL" are added.
4. When curt backend restarts, the newly implemented worker will 
be advertised and use.

The code below demostrate the use of it.
""" 

import time
import numpy as np
from curt.command import CURTCommands

CURTCommands.initialize()

oakd_pipeline_config = [
    ["add_rgb_cam_node", 640, 360],
    ["add_rgb_cam_preview_node"],
    ["add_nn_node", "palm_detection", "palm_detection_6_shaves.blob", 128, 128],
    ["add_nn_node", "hand_landmarks", "hand_landmark_6_shaves.blob", 224, 224],
    ["add_nn_node", "hand_asl", "hand_asl_6_shaves.blob", 224, 224],
]
CURTCommands.config_worker(oakd_pipeline_worker, oakd_pipeline_config)

oakd_pipeline_worker = CURTCommands.get_worker(
    "charlie/vision/oakd_service/oakd_pipeline"
)

rgb_camera_worker = CURTCommands.get_worker(
    "charlie/vision/oakd_service/oakd_rgb_camera_input"
)

hand_landmarks_worker = CURTCommands.get_worker(
    "charlie/vision/oakd_service/oakd_hand_landmarks"
)

hand_asl_worker = CURTCommands.get_worker("charlie/vision/oakd_service/oakd_hand_asl")

rgb_frame_handler = CURTCommands.request(rgb_camera_worker, params=["get_rgb_frame"])
hand_landmarks_handler = CURTCommands.request(
    hand_landmarks_worker, params=[rgb_frame_handler]
)
hand_asl_handler = CURTCommands.request(
    hand_asl_worker, params=[hand_landmarks_handler, rgb_frame_handler]
)
hand_asl_results = CURTCommands.get_result(hand_asl_handler)