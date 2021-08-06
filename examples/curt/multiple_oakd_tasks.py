""" 
This example demonstrates how to use multiple oakds to process different inferences
on one frame concurrently. A frame is first grabbed from one OAK-D camera. The frame 
is sent to 3 OAK-D cameras to perform facemesh estimation, pose estimation
and hand landmarks estimation. The results are rendered in a rendering worker. One
thing to note is some of the workers are not defined at the start of the program, instead,
CURT will search for the most suitable worker and assign the task to it automatically.

"""

from curt.command import CURTCommands

# Modify these to your own workers
# Format is "<host_name>/<module_type>/<service_name>/<worker_name>"
OAKD1_PIPELINE_WORKER = "charlie/vision/oakd_service/oakd_pipeline"
OAKD2_PIPELINE_WORKER = "oakd2/vision/oakd_service/oakd_pipeline"
OAKD3_PIPELINE_WORKER = "oakd3/vision/oakd_service/oakd_pipeline"
RGB_CAMERA_WORKER = "oakd2/vision/oakd_service/oakd_rgb_camera_input"
VISION_RENDER_WORKER = "michael-linux/vision/vision_render_service/opencv_render"
FACE_DETECTION_WORKER = "charlie/vision/oakd_service/oakd_face_detection"

preview_width = 640
preview_heigth = 360

face_detection_nn_input_size = 300
facemesh_nn_input_size = 192

body_detection_nn_input_size = 224
body_landmarks_nn_input_size = 256

palm_detection_nn_input_size = 128
hand_landmarks_nn_input_size = 224

face_detection_confidence = 0.6
detect_largest_face_only = False

CURTCommands.initialize()

OAKD1_pipeline_config = [
    ["add_nn_node", "facemesh", "facemesh_sh6.blob", facemesh_nn_input_size, facemesh_nn_input_size]
]

OAKD2_pipeline_config = [
    ["add_rgb_cam_node", preview_width, preview_heigth],
    ["add_rgb_cam_preview_node"],
    ["add_nn_node_pipeline",
        "face_detection",
        "face-detection-retail-0004_openvino_2021.2_6shave.blob",
        face_detection_nn_input_size,
        face_detection_nn_input_size
        ],
    ["add_nn_node", "palm_detection", "palm_detection_sh6.blob", palm_detection_nn_input_size, palm_detection_nn_input_size],
    ["add_nn_node", "hand_landmarks", "hand_landmark_sh6.blob", hand_landmarks_nn_input_size, hand_landmarks_nn_input_size],
]

OAKD3_pipeline_config = [
    ["add_nn_node", "body_detection", "pose_detection_sh6.blob", body_detection_nn_input_size, body_detection_nn_input_size],
    ["add_nn_node", "body_landmarks", "pose_landmark_lite_sh6.blob", body_landmarks_nn_input_size, body_landmarks_nn_input_size],
    
]

OAKD1_pipeline_worker = CURTCommands.get_worker(OAKD1_PIPELINE_WORKER)
OAKD2_pipeline_worker = CURTCommands.get_worker(OAKD2_PIPELINE_WORKER)
OAKD3_pipeline_worker = CURTCommands.get_worker(OAKD3_PIPELINE_WORKER)

CURTCommands.config_worker(OAKD1_pipeline_worker, OAKD1_pipeline_config)
CURTCommands.config_worker(OAKD2_pipeline_worker, OAKD2_pipeline_config)
CURTCommands.config_worker(OAKD3_pipeline_worker, OAKD3_pipeline_config)

rgb_camera_worker = CURTCommands.get_worker(RGB_CAMERA_WORKER)

vision_render_worker = CURTCommands.get_worker(VISION_RENDER_WORKER)
CURTCommands.config_worker(
    vision_render_worker,
    {
        "windows": {"Visualization": {"top_left": [0, 0], "size": [640, 360]}},
        "modes": {"render_results": ["Visualization"]},
    },
)

def main():
    while True:
        rgb_frame_handler = CURTCommands.request(rgb_camera_worker, params=["get_rgb_frame"])
        face_detection_handler = CURTCommands.request(
            "oakd_face_detection", 
            params=["detect_face_pipeline", face_detection_confidence, detect_largest_face_only]
        )
        facemesh_handler = CURTCommands.request(
            "oakd_facemesh", 
            params=[rgb_frame_handler, 
            face_detection_handler]
        )
        body_landmarks_handler = CURTCommands.request(
            "oakd_pose_estimation", 
            params=[rgb_frame_handler]
        )
        hand_landmarks_handler = CURTCommands.request(
            "oakd_hand_landmarks", 
            params=[rgb_frame_handler]
        )

        rendering_config = {
            "Visualization": [
                rgb_frame_handler,
                facemesh_handler,
                hand_landmarks_handler,
                body_landmarks_handler
            ],
            "sync_handler": hand_landmarks_handler
        }

        rendering_handler = CURTCommands.request(
            vision_render_worker, params=rendering_config
        )

        rendering_result = CURTCommands.get_result(rendering_handler)
        
if __name__ == "__main__":
    main()