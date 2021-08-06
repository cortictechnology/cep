""" 
This example demonstrates the use of a newly implemented oak-d worker: hand_asl
To implement a new worker, please refer to the following steps:
1. Define a new oak-d node type in:
<cep_root>/src/curt/curt/modules/vision/oakd_node_types.py
In this example, the new type is "hand_asl"
2. Implement the actual logic of the worker in: 
<cep_root>/src/curt/curt/modules/vision/oakd_hand_asl.py 
3. Add this new woker in: 
<cep_root>/src/curt/curt/module_configs.json
In this example, a new worker "oakd_hand_asl" and its class 
name "OAKDASL" is added.
4. When curt backend restarts, the newly implemented worker will 
be advertised and use.

The code below demonstrates its use.
""" 

from curt.command import CURTCommands

# Modify these to your own workers
# Format is "<host_name>/<module_type>/<service_name>/<worker_name>"
OAKD_PIPELINE_WORKER = "charlie/vision/oakd_service/oakd_pipeline"
RGB_CAMERA_WORKER = "charlie/vision/oakd_service/oakd_rgb_camera_input"
HAND_LADNMARKS_WORKER = "charlie/vision/oakd_service/oakd_hand_landmarks"
HAND_ASL_WORKER = "charlie/vision/oakd_service/oakd_hand_asl"

preview_width = 640
preview_heigth = 360

palm_detection_nn_input_size = 128
hand_landmarks_nn_input_size = 224
hand_asl_nn_input_size = 224

CURTCommands.initialize()

oakd_pipeline_config = [
    ["add_rgb_cam_node", preview_width, preview_heigth],
    ["add_rgb_cam_preview_node"],
    ["add_nn_node", "palm_detection", "palm_detection_sh6.blob", palm_detection_nn_input_size, palm_detection_nn_input_size],
    ["add_nn_node", "hand_landmarks", "hand_landmark_sh6.blob", hand_landmarks_nn_input_size, hand_landmarks_nn_input_size],
    ["add_nn_node", "hand_asl", "hand_asl_6_shaves.blob", hand_asl_nn_input_size, hand_asl_nn_input_size],
]


oakd_pipeline_worker = CURTCommands.get_worker(
    OAKD_PIPELINE_WORKER
)
config_handler = CURTCommands.config_worker(oakd_pipeline_worker, oakd_pipeline_config)
success = CURTCommands.get_result(config_handler)["dataValue"]["data"]

rgb_camera_worker = CURTCommands.get_worker(
    RGB_CAMERA_WORKER
)

hand_landmarks_worker = CURTCommands.get_worker(
    HAND_LADNMARKS_WORKER
)

hand_asl_worker = CURTCommands.get_worker(HAND_ASL_WORKER)

while True:
    rgb_frame_handler = CURTCommands.request(rgb_camera_worker, params=["get_rgb_frame"])
    hand_landmarks_handler = CURTCommands.request(
        hand_landmarks_worker, params=[rgb_frame_handler]
    )
    hand_asl_handler = CURTCommands.request(
        hand_asl_worker, params=[hand_landmarks_handler, rgb_frame_handler]
    )
    hand_asl_results = CURTCommands.get_result(hand_asl_handler)["dataValue"]["data"]
    print(hand_asl_handler)