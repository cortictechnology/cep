/* 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021
  
 */

var vision_func = ["cait_enable_drawing_mode",
  "cait_detect_face",
  "cait_draw_detected_face",
  "cait_recognize_face",
  "cait_draw_recognized_face",
  "cait_add_person",
  "cait_delete_person",
  "cait_detect_objects",
  "cait_draw_detected_object",
  "cait_classify_image",
  "cait_face_emotions_estimation",
  "cait_draw_estimated_emotions",
  "cait_facemesh_estimation",
  "cait_draw_estimated_facemesh",
  "cait_get_body_landmarks",
  "cait_draw_estimated_body_landmarks",
  "cait_get_hand_landmarks",
  "cait_draw_estimated_hand_landmarks"
];

var vision_func_dependent_blocks = {
  "cait_enable_drawing_mode": ["add_stereo_cam_node"],
  "cait_detect_face": [["add_rgb_cam_node", "add_stereo_cam_node"], "face_detection"],
  "cait_recognize_face": ["add_rgb_cam_node", "face_detection", "face_features"],
  "cait_add_person": ["add_rgb_cam_node", "face_detection", "face_features"],
  "cait_delete_person": ["add_rgb_cam_node", "face_detection", "face_features"],
  "cait_detect_objects": [["add_rgb_cam_node", "add_stereo_cam_node"], "object_detection"],
  "cait_face_emotions_estimation": ["add_rgb_cam_node", "face_detection", '"add_nn_node", "face_emotions"'],
  "cait_facemesh_estimation": ["add_rgb_cam_node", "face_detection", '"add_nn_node", "facemesh"'],
  "cait_get_body_landmarks": ["add_rgb_cam_node", '"add_nn_node", "body_landmarks'],
  "cait_get_hand_landmarks": ["add_rgb_cam_node", '"add_nn_node", "hand_landmarks"']
}

var speech_func = ["cait_listen",
  "cait_say"];

var nlp_func = ["cait_analyze"];

var control_func = ["cait_rotate_motor",
  "cait_control_motor",
  "cait_control_motor_speed_group",
  "cait_control_motor_degree_group",
  "cait_move", "cait_rotate"];

var smart_home_func = ["cait_control_light",
  "cait_control_media_player"]

var spatial_face_detection = false;
var spatial_object_detection = false;

var current_file_list_root = "";

Blockly.defineBlocksWithJsonArray([
  {
    "type": "setup_block",
    "message0": "%{BKY_SETUP}",
    "message1": "%1",
    "args1": [
      {
        "type": "input_statement",
        "name": "init_blocks"
      }
    ],
    "colour": "#1d8cf7",
    "tooltip": "%{BKY_SETUP_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "main_block",
    "message0": "%{BKY_MAIN}",
    "message1": "%1",
    "args1": [
      {
        "type": "input_statement",
        "name": "main_blocks"
      }
    ],
    "colour": "#1d8cf7",
    "tooltip": "%{BKY_MAIN_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "dispatch_block",
    "message0": "%{BKY_DISPATCH}",
    "args0": [
      {
        "type": "input_dummy",
        "align": "CENTRE"
      },
      {
        "type": "field_dropdown",
        "name": "dispatch_queue",
        "options": [
          [
            "queue 1",
            "queue_1"
          ],
          [
            "queue 2",
            "queue_2"
          ],
          [
            "queue 3",
            "queue_3"
          ],
          [
            "queue 4",
            "queue_4"
          ]
        ]
      },
      {
        "type": "input_dummy",
        "align": "CENTRE"
      },
      {
        "type": "input_statement",
        "name": "dispatch_blocks",
        "align": "CENTRE"
      }
    ],
    "inputsInline": true,
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#d0c43f",
    "tooltip": "%{BKY_DISPATCH_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "main_variables_set",
    "message0": "%{BKY_MAIN_VARIABLES_SET}",
    "args0": [
      {
        "type": "input_value",
        "name": "main_var",
        "align": "CENTRE"
      },
      {
        "type": "input_value",
        "name": "local_var",
        "align": "CENTRE"
      }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#d0c43f",
    "tooltip": "%{BKY_VARIABLES_SET_TOOLTIP}"
  },
  {
    "type": "processing_block",
    "message0": "%{BKY_PROCESSING}",
    "args0": [
      {
        "type": "input_dummy",
        "align": "CENTRE"
      },
      {
        "type": "input_statement",
        "name": "execution_blocks",
        "align": "CENTRE"
      }
    ],
    "inputsInline": true,
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#00A500",
    "tooltip": "%{BKY_PROCESSING_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "set_parameter",
    "message0": "%{BKY_SET_PARAMS}",
    "args0": [
      {
        "type": "input_dummy",
        "align": "CENTRE"
      },
      {
        "type": "field_input",
        "name": "parameter",
        "text": ""
      },
      {
        "type": "input_dummy",
        "align": "CENTRE"
      },
      {
        "type": "input_value",
        "name": "value"
      }
    ],
    "inputsInline": true,
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#1d8cf7",
    "tooltip": "%{BKY_SET_PARAMS_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "sleep",
    "message0": "%{BKY_SLEEP}",
    "args0": [
      {
        "type": "input_dummy",
        "align": "CENTRE"
      },
      {
        "type": "input_value",
        "name": "time"
      }
    ],
    "inputsInline": true,
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#1d8cf7",
    "tooltip": "%{BKY_SLEEP_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "init_vision_pi",
    "message0": "%{BKY_INIT_VISION_PI}",
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#5D0095",
    "tooltip": "%{BKY_INIT_VISION_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "init_vision",
    "message0": "%{BKY_INIT_VISION}",
    "args0": [
      {
        "type": "input_dummy",
        "align": "CENTRE"
      },
      {
        "type": "input_statement",
        "name": "oakd_statements",
        "align": "CENTRE"
      }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#5D0095",
    "tooltip": "%{BKY_INIT_VISION_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "add_pipeline_node",
    "lastDummyAlign0": "CENTRE",
    "message0": "%{BKY_ADD_NODE}",
    "args0": [
      {
        "type": "field_dropdown",
        "name": "node",
        "options": [
          [
            "RGB Camera",
            "rgb"
          ],
          [
            "Stereo",
            "stereo"
          ],
          [
            "Spatial Face Detection",
            "spatial_face_detection"
          ],
          [
            "Face Detection",
            "face_detection"
          ],
          [
            "Face Mesh",
            "face_mesh"
          ],
          [
            "Face Recognition",
            "face_recognition"
          ],
          [
            "Spatial Object Detection",
            "spatial_object_detection"
          ],
          [
            "Object Detection",
            "object_detection"
          ],
          [
            "Face Emotion Estimation",
            "face_emotion"
          ],
          [
            "Human Pose Estimation",
            "pose_estimation"
          ],
          [
            "Hand Landmarks Estimation",
            "hand_landmarks"
          ]
        ]
      }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#5D0095",
    "tooltip": "%{BKY_ADD_NODE_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "init_voice",
    "lastDummyAlign0": "CENTRE",
    "message0": "%{BKY_INIT_VOICE}",
    "args0": [
      {
        "type": "input_dummy",
        "name": "voice_mode",
        "align": "CENTRE"
      },
      {
        "type": "input_dummy",
        "name": "params",
        "align": "CENTRE"
      },
      {
        "type": "input_dummy",
        "name": "cloud_accounts",
        "align": "CENTRE"
      },
      {
        "type": "input_dummy",
        "name": "ending",
        "text": ""
      },
      {
        "type": "field_dropdown",
        "name": "language",
        "options": [
          [
            "English",
            "english"
          ],
          [
            "Française",
            "french"
          ],
          [
            "普通话",
            "chinese"
          ]
        ]
      }

    ],
    "extensions": ["dynamic_voice_mode_extension", "dynamic_cloud_accounts_extension"],
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#019191",
    "tooltip": "%{BKY_INIT_VOICE_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "init_nlp",
    "lastDummyAlign0": "CENTRE",
    "message0": "%{BKY_INIT_NLP}",
    "args0": [
      {
        "type": "input_dummy",
        "name": "model_list",
        "align": "CENTRE"
      },
    ],
    "extensions": ["dynamic_model_list_extension"],
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#3ACFF7",
    "tooltip": "%{BKY_INIT_NLP_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "init_control",
    "lastDummyAlign0": "CENTRE",
    "message0": "%{BKY_INIT_CONTROL}",
    "args0": [
      {
        "type": "input_dummy",
        "align": "CENTRE"
      },
      {
        "type": "input_statement",
        "name": "statements",
        "align": "CENTRE"
      }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#F78C00",
    "tooltip": "%{BKY_INIT_CONTROL_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "add_control_hub",
    "lastDummyAlign0": "CENTRE",
    "message0": "%{BKY_ADD_CONTROL_HUB}",
    "args0": [
      {
        "type": "input_dummy",
        "name": "control_hubs",
        "align": "CENTRE"
      }
    ],
    "extensions": ["dynamic_control_hubs_extension"],
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#F78C00",
    "tooltip": "%{BKY_ADD_CONTROL_HUB_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "init_pid",
    "lastDummyAlign0": "CENTRE",
    "message0": "%{BKY_INIT_PID}",
    "args0": [
      {
        "type": "input_value",
        "name": "kp",
        "check": "Number"
      },
      {
        "type": "input_value",
        "name": "ki",
        "check": "Number"
      },
      {
        "type": "input_value",
        "name": "kd",
        "check": "Number"
      }
    ],
    "inputsInline": true,
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#F78C00",
    "tooltip": "%{BKY_INIT_PID_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "init_smarthome",
    "lastDummyAlign0": "CENTRE",
    "message0": "%{BKY_INIT_HOME}",
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#F70090",
    "tooltip": "%{BKY_INIT_HOME_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "vision_draw_stereo_frame",
    "lastDummyAlign0": "CENTRE",
    "message0": "%{BKY_DRAW_STEREO_FRAME}",
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#5D0095",
    "tooltip": "%{BKY_DRAW_STEREO_FRAME_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "vision_detect_face",
    "message0": "%{BKY_FACE_DETECT}",
    "inputsInline": true,
    "output": "String",
    "colour": "#5D0095",
    "tooltip": "%{BKY_FACE_DETECT_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "vision_detect_face_pi",
    "message0": "%{BKY_FACE_DETECT}",
    "inputsInline": true,
    "output": "String",
    "colour": "#5D0095",
    "tooltip": "%{BKY_FACE_DETECT_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "vision_draw_detected_face",
    "message0": "%{BKY_DRAW_FACE_DETECTED}",
    "args0": [
      {
        "type": "input_value",
        "name": "face",
        "align": "CENTRE"
      }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#5D0095",
    "tooltip": "%{BKY_DRAW_FACE_DETECTED_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "vision_recognize_face",
    "message0": "%{BKY_FACE_RECOGNIZE}",
    "inputsInline": true,
    "output": "String",
    "colour": "#5D0095",
    "tooltip": "%{BKY_FACE_RECOGNIZE_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "vision_draw_recognized_face",
    "message0": "%{BKY_DRAW_FACE_RECOGNIZED}",
    "args0": [
      {
        "type": "input_value",
        "name": "people",
        "align": "CENTRE"
      }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#5D0095",
    "tooltip": "%{BKY_DRAW_FACE_RECOGNIZED_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "vision_add_person",
    "message0": "%{BKY_FACE_ADD}",
    "args0": [
      {
        "type": "input_value",
        "name": "person_name",
        "align": "CENTRE"
      }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#5D0095",
    "tooltip": "%{BKY_FACE_ADD_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "vision_remove_person",
    "message0": "%{BKY_FACE_DELETE}",
    "args0": [
      {
        "type": "input_value",
        "name": "person_name",
        "align": "CENTRE"
      }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#5D0095",
    "tooltip": "%{BKY_FACE_DELETE_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "vision_detect_objects",
    "lastDummyAlign0": "CENTRE",
    "message0": "%{BKY_OBJECT_DETECT}",
    "inputsInline": true,
    "output": null,
    "colour": "#5D0095",
    "tooltip": "%{BKY_OBJECT_DETECT_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "vision_draw_detected_objects",
    "message0": "%{BKY_DRAW_OBJECT_DETECTED}",
    "args0": [
      {
        "type": "input_value",
        "name": "objects",
        "align": "CENTRE"
      }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#5D0095",
    "tooltip": "%{BKY_DRAW_OBJECT_DETECTED_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "vision_classify_image",
    "lastDummyAlign0": "CENTRE",
    "message0": "%{BKY_IMAGE_CLASSIFY}",
    "inputsInline": true,
    "output": null,
    "colour": "#5D0095",
    "tooltip": "%{BKY_IMAGE_CLASSIFY_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "vision_face_emotions",
    "lastDummyAlign0": "CENTRE",
    "message0": "%{BKY_FACE_EMOTIONS}",
    "inputsInline": true,
    "output": null,
    "colour": "#5D0095",
    "tooltip": "%{BKY_FACE_EMOTIONS_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "vision_draw_face_emotions",
    "message0": "%{BKY_DRAW_FACE_EMOTIONS}",
    "args0": [
      {
        "type": "input_value",
        "name": "emotions",
        "align": "CENTRE"
      }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#5D0095",
    "tooltip": "%{BKY_DRAW_FACE_EMOTIONS_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "vision_facemesh",
    "lastDummyAlign0": "CENTRE",
    "message0": "%{BKY_FACEMESH}",
    "inputsInline": true,
    "output": null,
    "colour": "#5D0095",
    "tooltip": "%{BKY_FACEMESH_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "vision_draw_facemesh",
    "message0": "%{BKY_DRAW_FACEMESH}",
    "args0": [
      {
        "type": "input_value",
        "name": "facemesh",
        "align": "CENTRE"
      }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#5D0095",
    "tooltip": "%{BKY_DRAW_FACEMESH_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "vision_age_gender",
    "lastDummyAlign0": "CENTRE",
    "message0": "%{BKY_AGE_GENDER}",
    "inputsInline": true,
    "output": null,
    "colour": "#5D0095",
    "tooltip": "%{BKY_AGE_GENDER_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "vision_human_pose",
    "lastDummyAlign0": "CENTRE",
    "message0": "%{BKY_HUMAN_POSE}",
    "inputsInline": true,
    "output": null,
    "colour": "#5D0095",
    "tooltip": "%{BKY_HUMAN_POSE_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "vision_draw_human_pose",
    "message0": "%{BKY_DRAW_HUMAN_POSE}",
    "args0": [
      {
        "type": "input_value",
        "name": "pose",
        "align": "CENTRE"
      }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#5D0095",
    "tooltip": "%{BKY_DRAW_HUMAN_POSE_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "vision_hand_landmarks",
    "lastDummyAlign0": "CENTRE",
    "message0": "%{BKY_HAND_LANDMARKS}",
    "inputsInline": true,
    "output": null,
    "colour": "#5D0095",
    "tooltip": "%{BKY_HAND_LANDMARKS_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "vision_draw_hand_landmarks",
    "message0": "%{BKY_DRAW_HAND_LANDMARKS}",
    "args0": [
      {
        "type": "input_value",
        "name": "hands",
        "align": "CENTRE"
      }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#5D0095",
    "tooltip": "%{BKY_DRAW_HAND_LANDMARKS_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "listen",
    "lastDummyAlign0": "CENTRE",
    "message0": "%{BKY_LISTEN}",
    "output": null,
    "colour": "#019191",
    "tooltip": "%{BKY_LISTEN_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "say",
    "lastDummyAlign0": "CENTRE",
    "message0": "%{BKY_SAY}",
    "args0": [
      {
        "type": "input_value",
        "name": "text",
        "align": "CENTRE"
      }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#019191",
    "tooltip": "%{BKY_SAY_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "play",
    "lastDummyAlign0": "CENTRE",
    "message0": "%{BKY_PLAY}",
    "args0": [
      {
        "type": "input_value",
        "name": "audio_clip",
        "align": "CENTRE"
      },
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#019191",
    "tooltip": "%{BKY_PLAY_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "create_file_list",
    "lastDummyAlign0": "CENTRE",
    "message0": "%{BKY_FILE_LIST}",
    "args0": [
      {
        "type": "input_value",
        "name": "directory_path",
      }
    ],
    "output": "Array",
    "outputShape": Blockly.OUTPUT_SHAPE_ROUND,
    "style": "list_blocks",
    "tooltip": "%{BKY_FILE_LIST_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "analyze",
    "message0": "%{BKY_ANALYZE}",
    "args0": [
      {
        "type": "input_value",
        "name": "text",
        "align": "CENTRE"
      }
    ],
    "output": null,
    "colour": "#3ACFF7",
    "tooltip": "%{BKY_ANALYZE_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "get_name",
    "message0": "%{BKY_GET_NAME}",
    "args0": [
      {
        "type": "input_value",
        "name": "intention",
        "align": "CENTRE"
      }
    ],
    "inputsInline": true,
    "output": null,
    "colour": "#3252D4",
    "tooltip": "%{BKY_GET_NAME_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "comment",
    "message0": "%{BKY_COMMENT}",
    "args0": [
      {
        "type": "input_value",
        "name": "comment",
        "check": "String"
      }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#B2820B",
    "tooltip": "%{BKY_COMMENT_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "create_empty_dictionary",
    "message0": "%{BKY_EMPTY_DICT}",
    "inputsInline": true,
    "output": null,
    "colour": "#001F4E",
    "tooltip": "%{BKY_EMPTY_DICT_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "dictionary_keys",
    "message0": "%{BKY_DICT_KEYS}",
    "args0": [
      {
        "type": "input_value",
        "name": "dictionary"
      }
    ],
    "inputsInline": true,
    "output": null,
    "colour": "#001F4E",
    "tooltip": "%{BKY_DICT_KEYS_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "dictionary_value",
    "message0": "%{BKY_DICT_VAL}",
    "args0": [
      {
        "type": "input_value",
        "name": "dictionary"
      },
      {
        "type": "input_value",
        "name": "key_name"
      }
    ],
    "inputsInline": true,
    "output": null,
    "colour": "#001F4E",
    "tooltip": "%{BKY_DICT_VAL_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "dictionary_value_set",
    "message0": "%{BKY_DICT_SET_VAL}",
    "args0": [
      {
        "type": "input_value",
        "name": "dictionary"
      },
      {
        "type": "input_value",
        "name": "key_name"
      },
      {
        "type": "input_value",
        "name": "value"
      }
    ],
    "inputsInline": true,
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#001F4E",
    "tooltip": "%{BKY_DICT_SET_VAL_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "dictionary_remove",
    "message0": "%{BKY_DICT_REMOVE_VAL}",
    "args0": [
      {
        "type": "input_value",
        "name": "dictionary"
      },
      {
        "type": "input_value",
        "name": "key_name"
      }
    ],
    "inputsInline": true,
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#001F4E",
    "tooltip": "%{BKY_DICT_REMOVE_VAL_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "dictionary_add",
    "message0": "%{BKY_DICT_ADD_VAL}",
    "args0": [
      {
        "type": "input_value",
        "name": "dictionary"
      },
      {
        "type": "input_value",
        "name": "key_name"
      },
      {
        "type": "input_value",
        "name": "value"
      }
    ],
    "inputsInline": true,
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#001F4E",
    "tooltip": "%{BKY_DICT_ADD_VAL_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "motor_control_block",
    "message0": "%{BKY_SET_MOTOR_GROUP}",
    "args0": [
      {
        "type": "input_dummy",
        "align": "CENTRE"
      },
      {
        "type": "input_statement",
        "name": "statements",
        "align": "CENTRE"
      }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#F78C00",
    "tooltip": "%{BKY_SET_MOTOR_GROUP_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "ev3_motor_block",
    "message0": "%{BKY_EV3_MOTOR}",
    "args0": [
      {
        "type": "field_dropdown",
        "name": "motor_name",
        "options": [
          [
            "A",
            "ev3_motor_A"
          ],
          [
            "B",
            "ev3_motor_B"
          ],
          [
            "C",
            "ev3_motor_C"
          ],
          [
            "D",
            "ev3_motor_D"
          ]
        ]
      }
    ],
    "output": "String",
    "colour": "#F78C00",
    "tooltip": "%{BKY_EV3_MOTOR_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "robot_inventor_motor_block",
    "message0": "%{BKY_RI_MOTOR}",
    "args0": [
      {
        "type": "field_dropdown",
        "name": "motor_name",
        "options": [
          [
            "A",
            "ri_motor_A"
          ],
          [
            "B",
            "ri_motor_B"
          ],
          [
            "C",
            "ri_motor_C"
          ],
          [
            "D",
            "ri_motor_D"
          ],
          [
            "E",
            "ri_motor_E"
          ],
          [
            "F",
            "ri_motor_F"
          ]
        ]
      }
    ],
    "output": "String",
    "colour": "#F78C00",
    "tooltip": "%{BKY_RI_MOTOR_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "motor_control",
    "lastDummyAlign0": "CENTRE",
    "message0": "%{BKY_SET_MOTOR_SPEED}",
    "args0": [
      {
        "type": "input_dummy",
        "name": "added_hubs",
        "align": "CENTRE"
      },
      {
        "type": "input_value",
        "name": "motor",
        "check": "String"
      },
      {
        "type": "input_dummy"
      },
      {
        "type": "input_value",
        "name": "speed",
        "check": "Number"
      },
      {
        "type": "input_value",
        "name": "duration",
        "check": "Number"
      }
    ],
    "extensions": ["dynamic_added_hubs_extension"],
    "inputsInline": true,
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#F78C00",
    "tooltip": "%{BKY_SET_MOTOR_SPEED_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "motor_position",
    "message0": "%{BKY_SET_MOTOR_ANGLE}",
    "args0": [
      {
        "type": "input_dummy",
        "name": "added_hubs",
        "align": "CENTRE"
      },
      {
        "type": "input_value",
        "name": "motor",
        "check": "String"
      },
      {
        "type": "input_dummy"
      },
      {
        "type": "input_value",
        "name": "degree",
        "check": "Number"
      }
    ],
    "extensions": ["dynamic_added_hubs_extension"],
    "inputsInline": true,
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#F78C00",
    "tooltip": "%{BKY_SET_MOTOR_ANGLE_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "motor_rotate",
    "message0": "%{BKY_SET_MOTOR_ROTATE}",
    "args0": [
      {
        "type": "input_dummy",
        "name": "added_hubs",
        "align": "CENTRE"
      },
      {
        "type": "input_value",
        "name": "motor",
        "check": "String"
      },
      {
        "type": "input_dummy"
      },
      {
        "type": "input_value",
        "name": "degree",
        "check": "Number"
      }
    ],
    "extensions": ["dynamic_added_hubs_extension"],
    "inputsInline": true,
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#F78C00",
    "tooltip": "%{BKY_SET_MOTOR_ROTATE_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "motor_power",
    "message0": "%{BKY_SET_MOTOR_POWER}",
    "args0": [
      {
        "type": "input_dummy",
        "name": "added_hubs",
        "align": "CENTRE"
      },
      {
        "type": "input_value",
        "name": "motor",
        "check": "String"
      },
      {
        "type": "input_dummy"
      },
      {
        "type": "input_value",
        "name": "power",
        "check": "Number"
      }
    ],
    "extensions": ["dynamic_added_hubs_extension"],
    "inputsInline": true,
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#F78C00",
    "tooltip": "%{BKY_SET_MOTOR_POWER_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "update_pid",
    "message0": "%{BKY_UPDATE_PID}",
    "args0": [
      {
        "type": "input_value",
        "name": "error",
        "check": "Number"
      }
    ],
    "output": null,
    "colour": "#F78C00",
    "tooltip": "%{BKY_UPDATE_PID_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "lights",
    "message0": "%{BKY_LIGHT_CONTROL}",
    "args0": [
      {
        "type": "input_dummy",
        "name": "light_devices",
        "align": "CENTRE"
      },
      {
        "type": "field_dropdown",
        "name": "operation",
        "options": [
          [
            "turn on",
            "turn_on"
          ],
          [
            "turn off",
            "turn_off"
          ],
          [
            "toggle",
            "toggle"
          ],
          [
            "change colour to",
            "color_name"
          ],
          [
            "set brightness to (0-100)",
            "brightness_pct"
          ]
        ]
      },
      {
        "type": "input_dummy",
        "name": "param_input",
        "align": "CENTRE"
      },
      {
        "type": "input_dummy",
        "name": "ending",
        "text": ""
      }
    ],
    "extensions": ["dynamic_lights_extension"],
    "inputsInline": true,
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#F70090",
    "tooltip": "%{BKY_LIGHT_CONTROL_TOOLTIP}",
    "helpUrl": ""
  },
  {
    "type": "media_player",
    "lastDummyAlign0": "CENTRE",
    "message0": "%{BKY_MEDIA_CONTROL}",
    "args0": [
      {
        "type": "input_dummy",
        "name": "media_players",
        "align": "CENTRE"
      },
      {
        "type": "field_dropdown",
        "name": "operation",
        "options": [
          [
            "play musics",
            "media_play"
          ],
          [
            "pause musics",
            "media_pause"
          ],
          [
            "volume up",
            "volume_up"
          ],
          [
            "volume down",
            "volume_down"
          ]
        ]
      }
    ],
    "extensions": ["dynamic_media_players_extension"],
    "previousStatement": null,
    "nextStatement": null,
    "colour": "#F70090",
    "tooltip": "%{BKY_MEDIA_CONTROL_TOOLTIP}",
    "helpUrl": ""
  }
]);

// var required_modules = [];

Blockly.Extensions.register('dynamic_lights_extension',
  function () {
    this.getInput('light_devices')
      .appendField(new Blockly.FieldDropdown(
        function () {
          var options = [];
          if (light_devices.length > 0) {
            for (i in light_devices) {
              options.push([light_devices[i], light_devices[i]])
            }
          }
          else {
            options.push(['none', 'none']);
          }
          return options;
        }), 'light');
  });

Blockly.Extensions.register('dynamic_media_players_extension',
  function () {
    this.getInput('media_players')
      .appendField(new Blockly.FieldDropdown(
        function () {
          var options = [];
          if (media_players.length > 0) {
            for (i in media_players) {
              options.push([media_players[i], media_players[i]])
            }
          }
          else {
            options.push(['none', 'none']);
          }
          return options;
        }), 'media_player');
  });

Blockly.Extensions.register("dynamic_voice_mode_extension",
  function () {
    this.getInput('voice_mode')
      .appendField(new Blockly.FieldDropdown(
        function () {
          var options = [];
          if (voice_mode.length > 0) {
            for (i in voice_mode) {
              options.push([voice_mode[i], voice_mode[i]])
            }
          }
          else {
            options.push(['none', 'none']);
          }
          return options;
        }), 'mode');
  });

Blockly.Extensions.register('dynamic_cloud_accounts_extension',
  function () {
    this.getInput('cloud_accounts')
      .appendField(new Blockly.FieldDropdown(
        function () {
          var options = [];
          if (cloud_accounts.length > 0) {
            for (i in cloud_accounts) {
              options.push([cloud_accounts[i], cloud_accounts[i]])
            }
          }
          else {
            options.push(['none', 'none']);
          }
          return options;
        }), 'accounts');
    if (cloud_accounts.length < 1 || this.getInput('voice_mode').fieldRow[1].value_ == "on device") {
      this.getInput("cloud_accounts").setVisible(false);
      this.getInput("ending").setVisible(false);
      this.getField("language").setVisible(false);
    }


  });

Blockly.Extensions.register('dynamic_model_list_extension',
  function () {
    this.getInput('model_list')
      .appendField(new Blockly.FieldDropdown(
        function () {
          var options = [];
          if (nlp_models.length > 0) {
            for (i in nlp_models) {
              options.push([nlp_models[i], nlp_models[i]])
            }
          }
          else {
            options.push(['none', 'none']);
          }
          return options;
        }), 'models');
  });


Blockly.Extensions.register('dynamic_control_hubs_extension',
  function () {
    this.getInput('control_hubs')
      .appendField(new Blockly.FieldDropdown(
        function () {
          var options = [];
          if (control_hubs.length > 0) {
            for (i in control_hubs) {
              options.push([control_hubs[i], control_hubs[i]])
            }
          }
          else {
            options.push(['none', 'none']);
          }
          return options;
        }), 'hubs');
  });

Blockly.Extensions.register('dynamic_added_hubs_extension',
  function () {
    this.getInput('added_hubs')
      .appendField(new Blockly.FieldDropdown(
        function () {
          var options = [];
          if (added_hubs.length > 0) {
            for (i in added_hubs) {
              options.push([added_hubs[i], added_hubs[i]])
            }
          }
          else {
            options.push(['none', 'none']);
          }
          return options;
        }), 'available_hubs');
  });

Blockly.JavaScript['setup_block'] = function (block) {
  var statements_main = Blockly.JavaScript.statementToCode(block, 'init_blocks');
  statements_main = statements_main.substring(2, statements_main.length)
  index = statements_main.indexOf("\n");
  while (index != -1) {
    statements_main = statements_main.substring(0, index + 1) + statements_main.substring(index + 3, statements_main.length);
    index = statements_main.indexOf("\n", index + 1);
  }
  var code = "// Initialize and setup different components\n" + statements_main;
  return code;
};

Blockly.Python['setup_block'] = function (block) {
  var statements_main = Blockly.Python.statementToCode(block, 'init_blocks');
  statements_main = statements_main.substring(2, statements_main.length)
  index = statements_main.indexOf("\n");
  while (index != -1) {
    statements_main = statements_main.substring(0, index + 1) + statements_main.substring(index + 3, statements_main.length);
    index = statements_main.indexOf("\n", index + 1);
  }
  var code = "import cait.essentials\nimport threading\n" + "def setup():\n" + statements_main;
  return code;
};

Blockly.JavaScript['main_block'] = function (block) {
  var statements_main = Blockly.JavaScript.statementToCode(block, 'main_blocks');
  statements_main = statements_main.substring(2, statements_main.length)
  index = statements_main.indexOf("\n");
  while (index != -1) {
    statements_main = statements_main.substring(0, index + 1) + statements_main.substring(index + 3, statements_main.length);
    index = statements_main.indexOf("\n", index + 1);
  }
  var code = "// Entry point of program\n" + statements_main;
  return code;
};

Blockly.Python['main_block'] = function (block) {
  var statements_main = Blockly.Python.statementToCode(block, 'main_blocks');
  statements_main = statements_main.substring(2, statements_main.length)
  index = statements_main.indexOf("\n");
  while (index != -1) {
    statements_main = statements_main.substring(0, index + 1) + statements_main.substring(index + 3, statements_main.length);
    index = statements_main.indexOf("\n", index + 1);
  }
  var code = "def main():\n" + statements_main;
  return code;
};

Blockly.JavaScript['set_parameter'] = function (block) {
  var text_parameter = block.getFieldValue('parameter');
  var value_value = Blockly.JavaScript.valueToCode(block, 'value', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "cait_set_module_parameters('" + text_parameter + "', " + value_value + ");\n";
  return code;
};

Blockly.Python['set_parameter'] = function (block) {
  var text_parameter = block.getFieldValue('parameter');
  var value_value = Blockly.Python.valueToCode(block, 'value', Blockly.Python.ORDER_ATOMIC);
  var code = "cait.essentials.set_module_parameters('" + text_parameter + "', " + value_value + ")\n";
  return code;
};

Blockly.JavaScript['dispatch_block'] = function (block) {
  var statements_operation = Blockly.JavaScript.statementToCode(block, 'dispatch_blocks');
  all_statements = [];
  stop_index = statements_operation.indexOf("\n");
  all_statements.push(statements_operation.substring(2, stop_index))
  var start_index = stop_index;
  stop_index = statements_operation.indexOf("\n", start_index + 1);
  while (stop_index != -1) {
    all_statements.push(statements_operation.substring(start_index + 3, stop_index))
    start_index = stop_index
    //statements_main = statements_main.substring(0, index + 1) + statements_main.substring(index + 3, statements_main.length);
    stop_index = statements_operation.indexOf("\n", start_index + 1);
  }
  var statements_operation = '';
  for (var i in all_statements) {
    this_statement = all_statements[i];
    if (this_statement.indexOf("highlightBlock") == -1) {
      statements_operation = statements_operation + this_statement + '\\n';

    }
  }
  all_used_vars = []
  var this_block = block;
  while (this_block.getParent() != null) {
    if (this_block.getParent().type != "main_block" & this_block.getParent().type != "dispatch_block") {
      var parent_block = this_block.getParent();
      if (parent_block.type == "variables_set") {
        all_used_vars.push(Blockly.JavaScript.variableDB_.getName(parent_block.getFieldValue('VAR'), Blockly.Variables.NAME_TYPE));
      }
    }
    this_block = this_block.getParent();
  }

  var value_queue = block.getFieldValue('dispatch_queue');

  var_list = "{";
  for (var i = 0; i < all_used_vars.length; i++) {
    var_list = var_list + "'" + all_used_vars[i] + "': " + all_used_vars[i];
    if (i < all_used_vars.length - 1) {
      var_list = var_list + ", ";
    }
  }
  var_list = var_list + "}";

  var code = 'dispatch_to("' + value_queue + '", "' + statements_operation + '", ' + var_list + ');\n';
  return code;
};

dispatch_count = 0;

Blockly.Python['dispatch_block'] = function (block) {
  var value_queue = Blockly.Python.valueToCode(block, 'dispatch_queue', Blockly.Python.ORDER_ATOMIC);
  var statements_operation = Blockly.Python.statementToCode(block, 'dispatch_blocks');
  all_statements = [];
  stop_index = statements_operation.indexOf("\n");
  all_statements.push(statements_operation.substring(2, stop_index))
  var start_index = stop_index;
  stop_index = statements_operation.indexOf("\n", start_index + 1);
  while (stop_index != -1) {
    all_statements.push(statements_operation.substring(start_index + 3, stop_index))
    start_index = stop_index
    //statements_main = statements_main.substring(0, index + 1) + statements_main.substring(index + 3, statements_main.length);
    stop_index = statements_operation.indexOf("\n", start_index + 1);
  }
  all_used_vars = []
  var this_block = block;
  while (this_block.getParent() != null) {
    if (this_block.getParent().type != "main_block" & this_block.getParent().type != "dispatch_block") {
      var parent_block = this_block.getParent();
      if (parent_block.type == "variables_set") {
        all_used_vars.push(Blockly.Python.variableDB_.getName(parent_block.getFieldValue('VAR'), Blockly.Variables.NAME_TYPE));
      }
    }
    this_block = this_block.getParent();
  }

  code = "# Audo generated dispatch function code\n"
    + "def dispatch_func_" + String(dispatch_count) + "():\n"
  if (all_used_vars.length > 0) {
    code = code + "  global "
    for (var v in all_used_vars) {
      code = code + all_used_vars[v]
      if (v == all_used_vars.length - 1) {
        code = code + "\n"
      }
      else {
        code = code + ", "
      }
    }
  }
  for (var i in all_statements) {
    code = code + "  " + all_statements[i] + "\n";
  }
  code = code + "# End of audo generated dispatch function\n"
  code = code
    + "dispatch_thread_" + String(dispatch_count)
    + " = threading.Thread(target=dispatch_func_" + String(dispatch_count)
    + ", daemon=True)\n"
    + "dispatch_thread_" + String(dispatch_count) + ".start()\n"

  dispatch_count = dispatch_count + 1;
  return code;
};

Blockly.JavaScript['main_variables_set'] = function (block) {
  var main_var = Blockly.JavaScript.valueToCode(block, 'main_var', Blockly.JavaScript.ORDER_ATOMIC);
  var local_var = Blockly.JavaScript.valueToCode(block, 'local_var', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "set_main_var('" + main_var + "', " + local_var + ");\n";

  return code;
};

Blockly.Python['main_variables_set'] = function (block) {
  var main_var = Blockly.Python.valueToCode(block, 'main_var', Blockly.Python.ORDER_ATOMIC);
  var local_var = Blockly.Python.valueToCode(block, 'local_var', Blockly.Python.ORDER_ATOMIC);
  var code = main_var + " = " + local_var + "\n"
  return code;
};

Blockly.JavaScript['processing_block'] = function (block) {
  var statements = Blockly.JavaScript.statementToCode(block, 'execution_blocks');
  var code = ""
    + "while (true) {\n"
    + statements
    + "  if (Object.keys(main_var_dict).length > 0) {\n"
    + "    for (var i in main_var_dict) {\n"
    + "      code = i + ' = main_var_dict[\"' + i + '\"]'\n"
    + "      eval(code);\n"
    + "    }\n"
    + "    main_var_dict = [];\n"
    + "  }\n"
    + "}"
  return code;
};

Blockly.Python['processing_block'] = function (block) {
  var statements = Blockly.Python.statementToCode(block, 'execution_blocks');
  var code = ""
    + "while True:\n"
    + statements
  return code;
};

Blockly.JavaScript['sleep'] = function (block) {
  var time_value = Blockly.JavaScript.valueToCode(block, 'time', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "await cait_sleep(" + time_value + ");\n";
  return code;
};

Blockly.Python['sleep'] = function (block) {
  var time_value = Blockly.Python.valueToCode(block, 'time', Blockly.Python.ORDER_ATOMIC);
  var code = "cait.essentials.sleep(" + time_value + ")\n";
  return code;
};

Blockly.JavaScript['init_vision_pi'] = function (block) {
  var code = "await cait_init_vision();\n";
  return code;
};

Blockly.Python['init_vision_pi'] = function (block) {
  var code = "cait.essentials.initialize_component('vision', processor='local')\n";
  return code;
};


Blockly.JavaScript['init_vision'] = function (block) {
  var statements_statements = Blockly.JavaScript.statementToCode(block, 'oakd_statements');
  var code = "await cait_init_vision('[";
  node_name_idx = statements_statements.indexOf("<", 0);
  var being_idx = node_name_idx + 1;
  while (node_name_idx != -1) {
    var end_idx = statements_statements.indexOf(">", being_idx);
    var node_name = statements_statements.substring(being_idx, end_idx);
    code = code + node_name;
    node_name_idx = statements_statements.indexOf("<", being_idx);
    being_idx = node_name_idx + 1;
    if (node_name_idx != -1) {
      code = code + ",";
    }
  }
  code = code + "]', 'oakd');\n";
  return code;
};

Blockly.Python['init_vision'] = function (block) {
  var statements_statements = Blockly.Python.statementToCode(block, 'oakd_statements');
  var code = "cait.essentials.initialize_component('vision', processor='oakd', mode=[";
  hub_name_idx = statements_statements.indexOf("(", 0);
  var being_idx = hub_name_idx + 1;
  while (hub_name_idx != -1) {
    var end_idx = statements_statements.indexOf(")", being_idx);
    var hub_name = statements_statements.substring(being_idx, end_idx);
    code = code + hub_name;
    hub_name_idx = statements_statements.indexOf("(", being_idx);
    being_idx = hub_name_idx + 1;
    if (hub_name_idx != -1) {
      code = code + ",";
    }
  }
  code = code + "])\n";
  return code;
};

Blockly.JavaScript['add_pipeline_node'] = function (block) {
  var dropdown_node = block.getFieldValue('node');
  if (dropdown_node == "rgb") {
    var code = '<["add_rgb_cam_node", 640, 360], ["add_rgb_cam_preview_node"]>';
  }
  else if (dropdown_node == "stereo") {
    var code = '<["add_stereo_cam_node", False], ["add_stereo_frame_node"]>';
  }
  else if (dropdown_node == "spatial_face_detection") {
    spatial_face_detection = true;
    var code = '<["add_spatial_mobilenetSSD_node", "face_detection", "face-detection-retail-0004_openvino_2021.2_6shave.blob", 300, 300, 0.5]>';
  }
  else if (dropdown_node == "face_detection") {
    spatial_face_detection = false;
    var code = '<["add_nn_node_pipeline", "face_detection", "face-detection-retail-0004_openvino_2021.2_6shave.blob", 300, 300]>';
  }
  else if (dropdown_node == "face_recognition") {
    var code = '<["add_nn_node", "face_landmarks", "landmarks-regression-retail-0009_openvino_2021.2_6shave.blob", 48, 48], ["add_nn_node", "face_features", "mobilefacenet.blob", 112, 112]>';
  }
  else if (dropdown_node == "spatial_object_detection") {
    spatial_object_detection = true;
    var code = '<["add_spatial_mobilenetSSD_node", "object_detection", "ssdlite_mbv2_coco.blob", 300, 300, 0.5]>';
  }
  else if (dropdown_node == "object_detection") {
    spatial_object_detection = false;
    var code = '<["add_mobilenetssd_node_pipeline", "object_detection", "ssdlite_mbv2_coco.blob", 300, 300, 0.5]>';
  }
  else if (dropdown_node == "face_emotion") {
    var code = '<["add_nn_node", "face_emotions", "emotions-recognition-retail-0003.blob", 64, 64]>';
  }
  else if (dropdown_node == "face_mesh") {
    var code = '<["add_nn_node", "facemesh", "facemesh_sh6.blob", 192, 192]>';
  }
  else if (dropdown_node == "pose_estimation") {
    var code = '<["add_nn_node", "body_detection", "pose_detection_sh6.blob", 224, 224], ["add_nn_node", "body_landmarks", "pose_landmark_lite_sh6.blob", 256, 256]>';
  }
  else if (dropdown_node == "hand_landmarks") {
    var code = '<["add_nn_node", "palm_detection", "palm_detection_sh6.blob", 128, 128], ["add_nn_node", "hand_landmarks", "hand_landmark_sh6.blob", 224, 224]>';
  }

  return code;
};

Blockly.Python['add_pipeline_node'] = function (block) {
  var dropdown_node = block.getFieldValue('node');
  if (dropdown_node == "rgb") {
    var code = '(["add_rgb_cam_node", 640, 360], ["add_rgb_cam_preview_node"])';
  }
  else if (dropdown_node == "stereo") {
    var code = '(["add_stereo_cam_node", False], ["add_stereo_frame_node"])';
  }
  else if (dropdown_node == "spatial_face_detection") {
    spatial_face_detection = true;
    var code = '(["add_spatial_mobilenetSSD_node", "face_detection", "face-detection-retail-0004_openvino_2021.2_6shave.blob", 300, 300, 0.5])';
  }
  else if (dropdown_node == "face_detection") {
    spatial_face_detection = false;
    var code = '(["add_nn_node_pipeline", "face_detection", "face-detection-retail-0004_openvino_2021.2_6shave.blob", 300, 300])';
  }
  else if (dropdown_node == "face_recognition") {
    var code = '(["add_nn_node", "face_landmarks", "landmarks-regression-retail-0009_openvino_2021.2_6shave.blob", 48, 48], ["add_nn_node", "face_features", "mobilefacenet.blob", 112, 112])';
  }
  else if (dropdown_node == "spatial_object_detection") {
    spatial_object_detection = true;
    var code = '(["add_spatial_mobilenetSSD_node", "object_detection", "ssdlite_mbv2_coco.blob", 300, 300, 0.5])';
  }
  else if (dropdown_node == "object_detection") {
    spatial_object_detection = false;
    var code = '(["add_mobilenetssd_node_pipeline", "object_detection", "ssdlite_mbv2_coco.blob", 300, 300, 0.5])';
  }
  else if (dropdown_node == "face_emotion") {
    var code = '(["add_nn_node", "face_emotions", "emotions-recognition-retail-0003.blob", 64, 64])';
  }
  else if (dropdown_node == "face_mesh") {
    var code = '(["add_nn_node", "facemesh", "facemesh_sh6.blob", 192, 192])';
  }
  else if (dropdown_node == "pose_estimation") {
    var code = '(["add_nn_node", "body_detection", "pose_detection_sh6.blob", 224, 224], ["add_nn_node", "body_landmarks", "pose_landmark_lite_sh6.blob", 256, 256])';
  }
  else if (dropdown_node == "hand_landmarks") {
    var code = '(["add_nn_node", "palm_detection", "palm_detection_sh4.blob", 128, 128], ["add_nn_node", "hand_landmarks", "hand_landmark_sh4.blob", 224, 224])';
  }

  return code;
};

Blockly.JavaScript['init_voice'] = function (block) {
  var dropdown_mode = block.getFieldValue('mode');
  var dropdown_account = block.getFieldValue('accounts');
  var dropdown_langauage = block.getFieldValue('language');
  var code = "await cait_init_voice('" + dropdown_mode + "', '" + dropdown_account + "', '" + dropdown_langauage + "');\n";
  return code;
};

Blockly.Python['init_voice'] = function (block) {
  var dropdown_mode = block.getFieldValue('mode');
  var dropdown_account = block.getFieldValue('accounts');
  var dropdown_langauage = block.getFieldValue('language');
  if (dropdown_mode == "online") {
    var code = "cait.essentials.initialize_component('voice', mode='online', account='" + dropdown_account + "', language='" + dropdown_langauage + "')\n";
  }
  else {
    var code = "cait.essentials.initialize_component('voice', mode='on_devie')\n";
  }
  return code;
};

Blockly.JavaScript['init_nlp'] = function (block) {
  var dropdown_models = block.getFieldValue('models');
  var code = "await cait_init_nlp('" + dropdown_models + "');\n";
  return code;
};

Blockly.Python['init_nlp'] = function (block) {
  var dropdown_models = block.getFieldValue('models');
  var code = "cait.essentials.initialize_component('nlp', '" + dropdown_models + "')\n";
  return code;
};

Blockly.JavaScript['init_control'] = function (block) {
  var statements_statements = Blockly.JavaScript.statementToCode(block, 'statements');
  var code = "await cait_init_control([";
  hub_name_idx = statements_statements.indexOf("<", 0);
  var being_idx = hub_name_idx + 1;
  while (hub_name_idx != -1) {
    var end_idx = statements_statements.indexOf(">", being_idx);
    var hub_name = statements_statements.substring(being_idx, end_idx);
    code = code + "'" + hub_name + "'";
    hub_name_idx = statements_statements.indexOf("<", being_idx);
    being_idx = hub_name_idx + 1;
    if (hub_name_idx != -1) {
      code = code + ",";
    }
  }
  code = code + "]);\n";
  return code;
};

Blockly.Python['init_control'] = function (block) {
  var statements_statements = Blockly.Python.statementToCode(block, 'statements');
  var code = "cait.essentials.initialize_component('control', [";
  hub_name_idx = statements_statements.indexOf("(", 0);
  var being_idx = hub_name_idx + 1;
  while (hub_name_idx != -1) {
    var end_idx = statements_statements.indexOf(")", being_idx);
    var hub_name = statements_statements.substring(being_idx, end_idx);
    code = code + "'" + hub_name + "'";
    hub_name_idx = statements_statements.indexOf("(", being_idx);
    being_idx = hub_name_idx + 1;
    if (hub_name_idx != -1) {
      code = code + ",";
    }
  }
  code = code + "])\n";
  return code;
};

Blockly.JavaScript['init_pid'] = function (block) {
  var number_kp = Blockly.JavaScript.valueToCode(block, 'kp', Blockly.JavaScript.ORDER_ATOMIC);
  var number_ki = Blockly.JavaScript.valueToCode(block, 'ki', Blockly.JavaScript.ORDER_ATOMIC);
  var number_kd = Blockly.JavaScript.valueToCode(block, 'kd', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "await cait_init_pid(" + String(number_kp) + ", " + String(number_ki) + ", " + String(number_kd) + ");\n";
  return code
};

Blockly.Python['init_pid'] = function (block) {
  var number_kp = Blockly.Python.valueToCode(block, 'kp', Blockly.Python.ORDER_ATOMIC);
  var number_ki = Blockly.Python.valueToCode(block, 'ki', Blockly.Python.ORDER_ATOMIC);
  var number_kd = Blockly.Python.valueToCode(block, 'kd', Blockly.Python.ORDER_ATOMIC);
  var code = "cait.essentials.initialize_pid(" + String(number_kp) + ", " + String(number_ki) + ", " + String(number_kd) + ")\n";
  return code;
};

Blockly.JavaScript['add_control_hub'] = function (block) {
  var dropdown_hub = block.getFieldValue('hubs');
  if (dropdown_hub == "none") {
    throw new Error("The selected hub: " + dropdown_hub + " is not valid, please make sure to select an available hub.");
  }
  var code = "<" + dropdown_hub + ">";
  return code;
};

Blockly.Python['add_control_hub'] = function (block) {
  var dropdown_hub = block.getFieldValue('hubs');
  var code = "(" + dropdown_hub + ")";
  return code;
};

Blockly.JavaScript['init_smarthome'] = function (block) {
  var code = 'await cait_init_smarthome();\n';
  return code;
};

Blockly.Python['init_smarthome'] = function (block) {
  var code = "cait.essentials.initialize_component('smart_home')\n";
  return code;
};

Blockly.JavaScript['create_empty_dictionary'] = function (block) {
  var code = '{}';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['create_empty_dictionary'] = function (block) {
  var code = '{}';
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.JavaScript['dictionary_keys'] = function (block) {
  var value_dictionary = Blockly.JavaScript.valueToCode(block, 'dictionary', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "Object.keys(" + value_dictionary + ")";
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['dictionary_keys'] = function (block) {
  var value_dictionary = Blockly.Python.valueToCode(block, 'dictionary', Blockly.Python.ORDER_ATOMIC);
  var code = "list(" + value_dictionary + ".keys())";
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.JavaScript['dictionary_value'] = function (block) {
  var value_dictionary = Blockly.JavaScript.valueToCode(block, 'dictionary', Blockly.JavaScript.ORDER_ATOMIC);
  var value_key_name = Blockly.JavaScript.valueToCode(block, 'key_name', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "(" + value_dictionary + ")[" + value_key_name + "]";
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['dictionary_value'] = function (block) {
  var value_dictionary = Blockly.Python.valueToCode(block, 'dictionary', Blockly.Python.ORDER_ATOMIC);
  var value_key_name = Blockly.Python.valueToCode(block, 'key_name', Blockly.Python.ORDER_ATOMIC);
  var code = value_dictionary + "[" + value_key_name + "]";
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.JavaScript['dictionary_value_set'] = function (block) {
  var value_dictionary = Blockly.JavaScript.valueToCode(block, 'dictionary', Blockly.JavaScript.ORDER_ATOMIC);
  var value_key_name = Blockly.JavaScript.valueToCode(block, 'key_name', Blockly.JavaScript.ORDER_ATOMIC);
  var value_value = Blockly.JavaScript.valueToCode(block, 'value', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "(" + value_dictionary + ")[" + value_key_name + "] = " + value_value + ";\n";
  return code;
};

Blockly.Python['dictionary_value_set'] = function (block) {
  var value_dictionary = Blockly.Python.valueToCode(block, 'dictionary', Blockly.Python.ORDER_ATOMIC);
  var value_key_name = Blockly.Python.valueToCode(block, 'key_name', Blockly.Python.ORDER_ATOMIC);
  var value_value = Blockly.Python.valueToCode(block, 'value', Blockly.Python.ORDER_ATOMIC);
  var code = value_dictionary + "[" + value_key_name + "] = " + value_value + "\n";
  return code;
};

Blockly.JavaScript['dictionary_remove'] = function (block) {
  var value_dictionary = Blockly.JavaScript.valueToCode(block, 'dictionary', Blockly.JavaScript.ORDER_ATOMIC);
  var value_key_name = Blockly.JavaScript.valueToCode(block, 'key_name', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "delete (" + value_dictionary + ")[" + value_key_name + "];\n";
  return code;
};

Blockly.Python['dictionary_remove'] = function (block) {
  var value_dictionary = Blockly.Python.valueToCode(block, 'dictionary', Blockly.Python.ORDER_ATOMIC);
  var value_key_name = Blockly.Python.valueToCode(block, 'key_name', Blockly.Python.ORDER_ATOMIC);
  var code = value_dictionary + ".pop(" + value_key_name + ")\n";
  return code;
};

Blockly.JavaScript['dictionary_add'] = function (block) {
  var value_dictionary = Blockly.JavaScript.valueToCode(block, 'dictionary', Blockly.JavaScript.ORDER_ATOMIC);
  var value_key_name = Blockly.JavaScript.valueToCode(block, 'key_name', Blockly.JavaScript.ORDER_ATOMIC);
  var value_value = Blockly.JavaScript.valueToCode(block, 'value', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "(" + value_dictionary + ")[" + value_key_name + "] = " + value_value + ";\n";
  return code;
};

Blockly.Python['dictionary_add'] = function (block) {
  var value_dictionary = Blockly.Python.valueToCode(block, 'dictionary', Blockly.Python.ORDER_ATOMIC);
  var value_key_name = Blockly.Python.valueToCode(block, 'key_name', Blockly.Python.ORDER_ATOMIC);
  var value_value = Blockly.Python.valueToCode(block, 'value', Blockly.Python.ORDER_ATOMIC);
  var code = value_dictionary + "[" + value_key_name + "] = " + value_value + "\n";
  return code;
};

Blockly.JavaScript['vision_detect_face'] = function (block) {
  var code = "await cait_detect_face('oakd')";
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['vision_detect_face'] = function (block) {
  var code = "cait.essentials.detect_face(processor='oakd')";
  if (spatial_face_detection) {
    var code = "cait.essentials.detect_face(processor='oakd', spatial=True)";
  }

  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.JavaScript['vision_detect_face_pi'] = function (block) {
  var code = "await cait_detect_face('pi')";
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['vision_detect_face_pi'] = function (block) {
  var code = "cait.essentials.detect_face(processor='pi')";
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.JavaScript['vision_draw_stereo_frame'] = function (block) {
  var code = "await cait_enable_drawing_mode('Depth Mode');\n";
  return code;
};

Blockly.Python['vision_draw_stereo_frame'] = function (block) {
  var code = "cait.essentials.enable_drawing_mode('Depth Mode')\n";
  return code;
};

Blockly.JavaScript['vision_draw_detected_face'] = function (block) {
  var value_face = Blockly.JavaScript.valueToCode(block, 'face', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "await cait_draw_detected_face(" + String(value_face) + "); \n";
  return code;
};

Blockly.Python['vision_draw_detected_face'] = function (block) {
  var value_face = Blockly.Python.valueToCode(block, 'face', Blockly.Python.ORDER_ATOMIC);
  var code = "cait.essentials.draw_detected_face(" + String(value_face) + ")\n";
  return code;
};

Blockly.JavaScript['vision_recognize_face'] = function (block) {
  var code = "await cait_recognize_face()";
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.JavaScript['vision_draw_recognized_face'] = function (block) {
  var value_people = Blockly.JavaScript.valueToCode(block, 'people', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "await cait_draw_recognized_face(" + String(value_people) + "); \n";
  return code;
};

Blockly.Python['vision_draw_recognized_face'] = function (block) {
  var value_people = Blockly.Python.valueToCode(block, 'people', Blockly.Python.ORDER_ATOMIC);
  var code = "cait.essentials.draw_recognized_face(" + String(value_people) + ")\n";
  return code;
};

Blockly.Python['vision_recognize_face'] = function (block) {
  var code = "cait.essentials.recognize_face()";
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.JavaScript['vision_add_person'] = function (block) {
  var value_person_name = Blockly.JavaScript.valueToCode(block, 'person_name', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "await cait_add_person(" + String(value_person_name) + ");\n";
  return code;
};

Blockly.Python['vision_add_person'] = function (block) {
  var value_person_name = Blockly.Python.valueToCode(block, 'person_name', Blockly.Python.ORDER_ATOMIC);
  var code = "cait.essentials.add_person(" + String(value_person_name) + ")\n";
  return code;
};

Blockly.JavaScript['vision_remove_person'] = function (block) {
  var value_person_name = Blockly.JavaScript.valueToCode(block, 'person_name', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "await cait_delete_person(" + String(value_person_name) + ");\n";
  return code;
};

Blockly.Python['vision_remove_person'] = function (block) {
  var value_person_name = Blockly.Python.valueToCode(block, 'person_name', Blockly.Python.ORDER_ATOMIC);
  var code = "cait.essentials.remove_person(" + String(value_person_name) + ")\n";
  return code;
};

Blockly.JavaScript['vision_detect_objects'] = function (block) {
  var code = 'await cait_detect_objects()';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['vision_detect_objects'] = function (block) {
  var code = 'cait.essentials.detect_objects()';
  if (spatial_object_detection) {
    var code = "cait.essentials.detect_objects(spatial=True)";
  }
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.JavaScript['vision_draw_detected_objects'] = function (block) {
  var value_objects = Blockly.JavaScript.valueToCode(block, 'objects', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "await cait_draw_detected_objects(" + String(value_objects) + "); \n";
  return code;
};

Blockly.Python['vision_draw_detected_objects'] = function (block) {
  var value_objects = Blockly.Python.valueToCode(block, 'objects', Blockly.Python.ORDER_ATOMIC);
  var code = "cait.essentials.draw_detected_objects(" + String(value_objects) + ")\n";
  return code;
};

Blockly.JavaScript['vision_classify_image'] = function (block) {
  var code = 'await cait_classify_image()';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['vision_classify_image'] = function (block) {
  var code = 'cait.essentials.classify_image()';
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.JavaScript['vision_face_emotions'] = function (block) {
  var code = "await cait_face_emotions_estimation()";
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['vision_face_emotions'] = function (block) {
  var code = "cait.essentials.face_emotions_estimation()";
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.JavaScript['vision_draw_face_emotions'] = function (block) {
  var value_emotions = Blockly.JavaScript.valueToCode(block, 'emotions', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "await cait_draw_estimated_emotions(" + String(value_emotions) + "); \n";
  return code;
};

Blockly.Python['vision_draw_face_emotions'] = function (block) {
  var value_emotions = Blockly.Python.valueToCode(block, 'emotions', Blockly.Python.ORDER_ATOMIC);
  var code = "cait.essentials.draw_estimated_emotions(" + String(value_emotions) + ")\n";
  return code;
};

Blockly.JavaScript['vision_facemesh'] = function (block) {
  var code = "await cait_facemesh_estimation()";
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['vision_facemesh'] = function (block) {
  var code = "cait.essentials.facemesh_estimation()";
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.JavaScript['vision_draw_facemesh'] = function (block) {
  var value_facemesh = Blockly.JavaScript.valueToCode(block, 'facemesh', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "await cait_draw_estimated_facemesh(" + String(value_facemesh) + "); \n";
  return code;
};

Blockly.Python['vision_draw_facemesh'] = function (block) {
  var value_facemesh = Blockly.Python.valueToCode(block, 'facemesh', Blockly.Python.ORDER_ATOMIC);
  var code = "cait.essentials.draw_estimated_facemesh(" + String(value_facemesh) + ")\n";
  return code;
};


Blockly.JavaScript['vision_human_pose'] = function (block) {
  var code = "await cait_get_body_landmarks()";
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['vision_human_pose'] = function (block) {
  var code = "cait.essentials.get_body_landmarks()";
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.JavaScript['vision_draw_human_pose'] = function (block) {
  var value_pose = Blockly.JavaScript.valueToCode(block, 'pose', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "await cait_draw_estimated_body_landmarks(" + String(value_pose) + "); \n";
  return code;
};

Blockly.Python['vision_draw_human_pose'] = function (block) {
  var value_pose = Blockly.Python.valueToCode(block, 'pose', Blockly.Python.ORDER_ATOMIC);
  var code = "cait.essentials.draw_estimated_body_landmarks(" + String(value_pose) + ")\n";
  return code;
};


Blockly.JavaScript['vision_hand_landmarks'] = function (block) {
  var code = "await cait_get_hand_landmarks()";
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['vision_hand_landmarks'] = function (block) {
  var code = "cait.essentials.get_hand_landmarks()";
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.JavaScript['vision_draw_hand_landmarks'] = function (block) {
  var value_hands = Blockly.JavaScript.valueToCode(block, 'hands', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "await cait_draw_estimated_hand_landmarks(" + String(value_hands) + "); \n";
  return code;
};

Blockly.Python['vision_draw_hand_landmarks'] = function (block) {
  var value_hands = Blockly.Python.valueToCode(block, 'hands', Blockly.Python.ORDER_ATOMIC);
  var code = "cait.essentials.draw_estimated_hand_landmarks(" + String(value_hands) + ")\n";
  return code;
};

Blockly.JavaScript['listen'] = function (block) {
  var code = "await cait_listen()";
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['listen'] = function (block) {
  var code = "cait.essentials.listen()";
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.JavaScript['say'] = function (block) {
  var value_text = Blockly.JavaScript.valueToCode(block, 'text', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "await cait_say(" + value_text + ");\n";
  return code;
};

Blockly.Python['say'] = function (block) {
  var value_text = Blockly.Python.valueToCode(block, 'text', Blockly.Python.ORDER_ATOMIC);
  var code = "cait.essentials.say(" + value_text + ")\n";
  return code;
};

Blockly.JavaScript['create_file_list'] = function (block) {
  var value_text = Blockly.JavaScript.valueToCode(block, 'directory_path', Blockly.JavaScript.ORDER_ATOMIC);
  current_file_list_root = value_text.substring(1, value_text.length - 1);
  var code = "await cait_create_file_list(" + value_text + ")";
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['create_file_list'] = function (block) {
  var value_text = Blockly.Python.valueToCode(block, 'directory_path', Blockly.Python.ORDER_ATOMIC);
  current_file_list_root = value_text.substring(1, value_text.length - 1);
  var code = "cait.essentials.create_file_list(" + value_text + ")['file_list']";
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.JavaScript['play'] = function (block) {
  var value_text = Blockly.JavaScript.valueToCode(block, 'audio_clip', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "await cait_play_audio('" + current_file_list_root + "/' + String(" + value_text + "));\n";
  return code;
};

Blockly.Python['play'] = function (block) {
  var value_text = Blockly.Python.valueToCode(block, 'audio_clip', Blockly.Python.ORDER_ATOMIC);
  var code = "cait.essentials.play_audio('" + current_file_list_root + "/' + str(" + value_text + "))\n";
  return code;
};

Blockly.JavaScript['analyze'] = function (block) {
  var value_text = Blockly.JavaScript.valueToCode(block, 'text', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "await cait_analyze(" + value_text + ")";
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['analyze'] = function (block) {
  var value_text = Blockly.Python.valueToCode(block, 'text', Blockly.Python.ORDER_ATOMIC);
  var code = "cait.essentials.analyse_text(" + value_text + ")";
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.JavaScript['get_name'] = function (block) {
  var value_intention = Blockly.JavaScript.valueToCode(block, 'intention', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "await cait_get_name(" + value_intention + ")";
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['get_name'] = function (block) {
  var value_intention = Blockly.Python.valueToCode(block, 'intention', Blockly.Python.ORDER_ATOMIC);
  var code = "get_name(" + value_intention + ")";
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.JavaScript['comment'] = function (block) {
  var value_comment = String(Blockly.JavaScript.valueToCode(block, 'comment', Blockly.JavaScript.ORDER_ATOMIC));
  value_comment = value_comment.substring(1, value_comment.length - 1);
  var code = "//" + value_comment + "\n";
  return code;
};

Blockly.Python['comment'] = function (block) {
  var value_comment = String(Blockly.Python.valueToCode(block, 'comment', Blockly.Python.ORDER_ATOMIC));
  value_comment = value_comment.substring(1, value_comment.length - 1);
  var code = "#" + value_comment + "\n";
  return code;
};

Blockly.JavaScript['ev3_motor_block'] = function (block) {
  var motor_name = block.getFieldValue('motor_name');
  return [motor_name, Blockly.JavaScript.ORDER_NONE];
}

Blockly.Python['ev3_motor_block'] = function (block) {
  var motor_name = block.getFieldValue('motor_name');
  return [motor_name, Blockly.Python.ORDER_NONE];
}

Blockly.JavaScript['robot_inventor_motor_block'] = function (block) {
  var motor_name = block.getFieldValue('motor_name');
  return [motor_name, Blockly.JavaScript.ORDER_NONE];
}

Blockly.Python['robot_inventor_motor_block'] = function (block) {
  var motor_name = block.getFieldValue('motor_name');
  return [motor_name, Blockly.Python.ORDER_NONE];
}

Blockly.JavaScript['motor_position'] = function (block) {
  var hub_name = block.getFieldValue('available_hubs');
  var index = added_hubs.indexOf(hub_name);
  if (index == -1) {
    throw new Error("The selected hub: " + hub_name + " is not available, please make sure the selection is valid");
  }
  var motor_name = Blockly.JavaScript.valueToCode(block, 'motor', Blockly.JavaScript.ORDER_ATOMIC);
  if (hub_name.indexOf("EV3") != -1) {
    if (motor_name.indexOf("ev3") == -1) {
      throw new Error("EV3 Hub must use EV3 motors only");
    }
  } else if (hub_name.indexOf("Robot Inventor") != -1) {
    if (motor_name.indexOf("ri") == -1) {
      throw new Error("Robot Inventor Hub must use Robot Inventor motors only");
    }
  }
  motor_name = motor_name.substring(motor_name.indexOf("_") + 1, motor_name.length - 1)
  var number_degree = Blockly.JavaScript.valueToCode(block, 'degree', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "await cait_set_motor_position('" + hub_name + "', '" + motor_name + "', " + String(number_degree) + ");\n";
  return code;
};

Blockly.Python['motor_position'] = function (block) {
  var hub_name = block.getFieldValue('available_hubs');
  var motor_name = Blockly.Python.valueToCode(block, 'motor', Blockly.Python.ORDER_ATOMIC);
  motor_name = motor_name.substring(motor_name.indexOf("_") + 1, motor_name.length - 1)
  var number_degree = Blockly.Python.valueToCode(block, 'degree', Blockly.Python.ORDER_ATOMIC);
  var code = "cait.essentials.set_motor_position('" + hub_name + "', '" + motor_name + "', " + String(number_degree) + ")\n";
  return code;
};

Blockly.JavaScript['motor_power'] = function (block) {
  var hub_name = block.getFieldValue('available_hubs');
  var index = added_hubs.indexOf(hub_name);
  if (index == -1) {
    throw new Error("The selected hub: " + hub_name + " is not available, please make sure the selection is valid");
  }
  var motor_name = Blockly.JavaScript.valueToCode(block, 'motor', Blockly.JavaScript.ORDER_ATOMIC);
  if (hub_name.indexOf("EV3") != -1) {
    if (motor_name.indexOf("ev3") == -1) {
      throw new Error("EV3 Hub must use EV3 motors only");
    }
  } else if (hub_name.indexOf("Robot Inventor") != -1) {
    if (motor_name.indexOf("ri") == -1) {
      throw new Error("Robot Inventor Hub must use Robot Inventor motors only");
    }
  }
  motor_name = motor_name.substring(motor_name.indexOf("_") + 1, motor_name.length - 1)
  var number_power = Blockly.JavaScript.valueToCode(block, 'power', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "await cait_set_motor_power('" + hub_name + "', '" + motor_name + "', " + String(number_power) + ");\n";
  return code;
};

Blockly.Python['motor_power'] = function (block) {
  var hub_name = block.getFieldValue('available_hubs');
  var motor_name = Blockly.Python.valueToCode(block, 'motor', Blockly.Python.ORDER_ATOMIC);
  motor_name = motor_name.substring(motor_name.indexOf("_") + 1, motor_name.length - 1)
  var number_power = Blockly.Python.valueToCode(block, 'power', Blockly.Python.ORDER_ATOMIC);
  var code = "cait.essentials.set_motor_power('" + hub_name + "', '" + motor_name + "', " + String(number_power) + ")\n";
  return code;
};

Blockly.JavaScript['motor_rotate'] = function (block) {
  var hub_name = block.getFieldValue('available_hubs');
  var index = added_hubs.indexOf(hub_name);
  if (index == -1) {
    throw new Error("The selected hub: " + hub_name + " is not available, please make sure the selection is valid");
  }
  var motor_name = Blockly.JavaScript.valueToCode(block, 'motor', Blockly.JavaScript.ORDER_ATOMIC);
  if (hub_name.indexOf("EV3") != -1) {
    if (motor_name.indexOf("ev3") == -1) {
      throw new Error("EV3 Hub must use EV3 motors only");
    }
  } else if (hub_name.indexOf("Robot Inventor") != -1) {
    if (motor_name.indexOf("ri") == -1) {
      throw new Error("Robot Inventor Hub must use Robot Inventor motors only");
    }
  }
  motor_name = motor_name.substring(motor_name.indexOf("_") + 1, motor_name.length - 1)
  var number_degree = Blockly.JavaScript.valueToCode(block, 'degree', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "await cait_rotate_motor('" + hub_name + "', '" + motor_name + "', " + String(number_degree) + ");\n";
  return code;
};

Blockly.Python['motor_rotate'] = function (block) {
  var hub_name = block.getFieldValue('available_hubs');
  var motor_name = Blockly.Python.valueToCode(block, 'motor', Blockly.Python.ORDER_ATOMIC);
  motor_name = motor_name.substring(motor_name.indexOf("_") + 1, motor_name.length - 1)
  var number_degree = Blockly.Python.valueToCode(block, 'degree', Blockly.Python.ORDER_ATOMIC);
  var code = "cait.essentials.rotate_motor('" + hub_name + "', '" + motor_name + "', " + String(number_degree) + ")\n";
  return code;
};

Blockly.JavaScript['motor_control'] = function (block) {
  var hub_name = block.getFieldValue('available_hubs');
  var index = added_hubs.indexOf(hub_name);
  if (index == -1) {
    throw new Error("The selected hub: " + hub_name + " is not available, please make sure the selection is valid");
  }
  var motor_name = Blockly.JavaScript.valueToCode(block, 'motor', Blockly.JavaScript.ORDER_ATOMIC);
  if (hub_name.indexOf("EV3") != -1) {
    if (motor_name.indexOf("ev3") == -1) {
      throw new Error("EV3 Hub must use EV3 motors only");
    }
  } else if (hub_name.indexOf("Robot Inventor") != -1) {
    if (motor_name.indexOf("ri") == -1) {
      throw new Error("Robot Inventor Hub must use Robot Inventor motors only");
    }
  }
  motor_name = motor_name.substring(motor_name.indexOf("_") + 1, motor_name.length - 1)
  var number_speed = Blockly.JavaScript.valueToCode(block, 'speed', Blockly.JavaScript.ORDER_ATOMIC);
  var number_duration = Blockly.JavaScript.valueToCode(block, 'duration', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "await cait_control_motor('" + hub_name + "', '" + motor_name + "', " + String(number_speed) + ", " + String(number_duration) + ");\n";
  return code;
};

Blockly.Python['motor_control'] = function (block) {
  var hub_name = block.getFieldValue('available_hubs');
  var motor_name = Blockly.Python.valueToCode(block, 'motor', Blockly.Python.ORDER_ATOMIC);
  motor_name = motor_name.substring(motor_name.indexOf("_") + 1, motor_name.length - 1)
  var number_speed = Blockly.Python.valueToCode(block, 'speed', Blockly.Python.ORDER_ATOMIC);
  var number_duration = Blockly.Python.valueToCode(block, 'duration', Blockly.Python.ORDER_ATOMIC);
  var code = "cait.essentials.control_motor('" + hub_name + "', '" + motor_name + "', " + String(number_speed) + ", " + String(number_duration) + ")\n";
  return code;
};

Blockly.JavaScript['motor_control_block'] = function (block) {
  var statements_statements = Blockly.JavaScript.statementToCode(block, 'statements');
  var code = "await cait_control_motor_group([\n";
  motor_speed_idx = statements_statements.indexOf("control_motor", 0);
  init_speed_idx = motor_speed_idx;
  motor_rotate_idx = statements_statements.indexOf("rotate_motor", 0);
  init_rotate_idx = motor_rotate_idx;
  motor_power_idx = statements_statements.indexOf("set_motor_power", 0);
  var speed_being_idx = motor_speed_idx + 13;
  var degree_being_idx = motor_rotate_idx + 12;
  var power_being_idx = motor_power_idx + 15;
  //console.log(statements_statements);
  while (motor_speed_idx != -1) {
    hub_name_begin_idx = statements_statements.indexOf("('", speed_being_idx) + 2
    hub_name_end_idx = statements_statements.indexOf("', ", hub_name_begin_idx)
    motor_name_begin_idx = statements_statements.indexOf("'", hub_name_end_idx + 1) + 1
    motor_name_end_idx = statements_statements.indexOf("'", motor_name_begin_idx + 1)
    speed_begin_idx = motor_name_end_idx + 3;
    speed_end_idx = statements_statements.indexOf(",", speed_begin_idx)
    duration_begin_idx = speed_end_idx + 2;
    duration_end_idx = statements_statements.indexOf(")", duration_begin_idx);

    hub_name = statements_statements.substring(hub_name_begin_idx, hub_name_end_idx);
    motor_name = statements_statements.substring(motor_name_begin_idx, motor_name_end_idx);
    speed = statements_statements.substring(speed_begin_idx, speed_end_idx);
    duration = statements_statements.substring(duration_begin_idx, duration_end_idx);

    code_line = "{'hub_name': '" + hub_name + "', 'motor_name': '" + motor_name + "', 'speed': " + speed + ", 'duration': " + duration + "}"
    code = code + code_line;

    motor_speed_idx = statements_statements.indexOf("control_motor", speed_being_idx);
    if (motor_speed_idx != -1) {
      code = code + ",\n";
    }
    speed_being_idx = motor_speed_idx + 13;
  }
  if (init_speed_idx != -1 && motor_rotate_idx != -1) {
    code = code + ",";
  }
  while (motor_rotate_idx != -1) {
    hub_name_begin_idx = statements_statements.indexOf("('", motor_rotate_idx) + 2
    hub_name_end_idx = statements_statements.indexOf("', ", hub_name_begin_idx)
    motor_name_begin_idx = statements_statements.indexOf("'", hub_name_end_idx + 1) + 1
    motor_name_end_idx = statements_statements.indexOf("'", motor_name_begin_idx + 1)
    angle_begin_idx = motor_name_end_idx + 3;
    angle_end_idx = statements_statements.indexOf(");", angle_begin_idx);

    hub_name = statements_statements.substring(hub_name_begin_idx, hub_name_end_idx);
    motor_name = statements_statements.substring(motor_name_begin_idx, motor_name_end_idx);
    angle = statements_statements.substring(angle_begin_idx, angle_end_idx);

    code_line = "{'hub_name': '" + hub_name + "', 'motor_name': '" + motor_name + "', 'angle': " + angle + "}"
    code = code + code_line;

    motor_rotate_idx = statements_statements.indexOf("rotate_motor", degree_being_idx);
    if (motor_rotate_idx != -1) {
      code = code + ",\n";
    }
    degree_being_idx = motor_rotate_idx + 12;
  }
  if (init_rotate_idx != -1 && motor_power_idx != -1) {
    code = code + ",";
  }
  while (motor_power_idx != -1) {
    hub_name_begin_idx = statements_statements.indexOf("('", motor_power_idx) + 2
    hub_name_end_idx = statements_statements.indexOf("', ", hub_name_begin_idx)
    motor_name_begin_idx = statements_statements.indexOf("'", hub_name_end_idx + 1) + 1
    motor_name_end_idx = statements_statements.indexOf("'", motor_name_begin_idx + 1)
    power_begin_idx = motor_name_end_idx + 3;
    power_end_idx = statements_statements.indexOf(");", power_begin_idx);

    hub_name = statements_statements.substring(hub_name_begin_idx, hub_name_end_idx);
    motor_name = statements_statements.substring(motor_name_begin_idx, motor_name_end_idx);
    power = statements_statements.substring(power_begin_idx, power_end_idx);

    code_line = "{'hub_name': '" + hub_name + "', 'motor_name': '" + motor_name + "', 'power': " + power + "}"
    code = code + code_line;

    motor_power_idx = statements_statements.indexOf("set_motor_power", power_being_idx);
    if (motor_power_idx != -1) {
      code = code + ",\n";
    }
    power_being_idx = motor_power_idx + 15;
  }

  code = code + "\n]);"
  return code;
};

Blockly.Python['motor_control_block'] = function (block) {
  var statements_statements = Blockly.Python.statementToCode(block, 'statements');
  var code = "cait.essentials.control_motor_group(" + "'{" + '"operation_list" :[';
  motor_speed_idx = statements_statements.indexOf("control_motor", 0);
  init_speed_idx = motor_speed_idx;
  motor_rotate_idx = statements_statements.indexOf("rotate_motor", 0);
  init_rotate_idx = motor_rotate_idx;
  motor_power_idx = statements_statements.indexOf("set_motor_power", 0);
  var speed_being_idx = motor_speed_idx + 13;
  var degree_being_idx = motor_rotate_idx + 12;
  var power_being_idx = motor_power_idx + 15;
  while (motor_speed_idx != -1) {
    hub_name_begin_idx = statements_statements.indexOf("('", motor_speed_idx) + 2
    hub_name_end_idx = statements_statements.indexOf("', ", hub_name_begin_idx)
    motor_name_begin_idx = statements_statements.indexOf("'", hub_name_end_idx + 1) + 1
    motor_name_end_idx = statements_statements.indexOf("'", motor_name_begin_idx + 1)
    speed_begin_idx = motor_name_end_idx + 3;
    speed_end_idx = statements_statements.indexOf(",", speed_begin_idx)
    duration_begin_idx = speed_end_idx + 2;
    duration_end_idx = statements_statements.indexOf(")", duration_begin_idx);

    hub_name = statements_statements.substring(hub_name_begin_idx, hub_name_end_idx);
    motor_name = statements_statements.substring(motor_name_begin_idx, motor_name_end_idx);
    speed = statements_statements.substring(speed_begin_idx, speed_end_idx);
    speed = speed.replace('(', '')
    speed = speed.replace(')', '')
    duration = statements_statements.substring(duration_begin_idx, duration_end_idx);

    code_line = '{"hub_name": "' + hub_name + '", "motor_name": "' + motor_name + '", "speed": "\' + str(' + speed + ') + \'", "duration": "\' + str(' + duration + ') + \'"}'
    code = code + code_line;

    motor_speed_idx = statements_statements.indexOf("control_motor", speed_being_idx);
    if (motor_speed_idx != -1) {
      code = code + ",";
    }
    speed_being_idx = motor_speed_idx + 13;
  }
  if (init_speed_idx != -1 && motor_rotate_idx != -1) {
    code = code + ",";
  }
  while (motor_rotate_idx != -1) {
    hub_name_begin_idx = statements_statements.indexOf("('", motor_rotate_idx) + 2
    hub_name_end_idx = statements_statements.indexOf("', ", hub_name_begin_idx)
    motor_name_begin_idx = statements_statements.indexOf("'", hub_name_end_idx + 1) + 1
    motor_name_end_idx = statements_statements.indexOf("'", motor_name_begin_idx + 1)
    angle_begin_idx = motor_name_end_idx + 3;
    angle_end_idx = statements_statements.indexOf(")", angle_begin_idx);

    hub_name = statements_statements.substring(hub_name_begin_idx, hub_name_end_idx);
    motor_name = statements_statements.substring(motor_name_begin_idx, motor_name_end_idx);
    angle = statements_statements.substring(angle_begin_idx, angle_end_idx);
    angle = angle.replace('(', '')
    angle = angle.replace(')', '')

    code_line = '{"hub_name": "' + hub_name + '", "motor_name": "' + motor_name + '", "angle": "\' + str(' + angle + ') + \'"}'
    code = code + code_line;

    motor_rotate_idx = statements_statements.indexOf("rotate_motor", degree_being_idx);
    if (motor_rotate_idx != -1) {
      code = code + ",";
    }
    degree_being_idx = motor_rotate_idx + 12;
  }
  if (init_rotate_idx != -1 && motor_power_idx != -1) {
    code = code + ",";
  }
  while (motor_power_idx != -1) {
    hub_name_begin_idx = statements_statements.indexOf("('", motor_power_idx) + 2
    hub_name_end_idx = statements_statements.indexOf("', ", hub_name_begin_idx)
    motor_name_begin_idx = statements_statements.indexOf("'", hub_name_end_idx + 1) + 1
    motor_name_end_idx = statements_statements.indexOf("'", motor_name_begin_idx + 1)
    power_begin_idx = motor_name_end_idx + 3;
    power_end_idx = statements_statements.indexOf(")", power_begin_idx);

    hub_name = statements_statements.substring(hub_name_begin_idx, hub_name_end_idx);
    motor_name = statements_statements.substring(motor_name_begin_idx, motor_name_end_idx);
    power = statements_statements.substring(power_begin_idx, power_end_idx);
    power = power.replace('(', '')
    power = power.replace(')', '')


    code_line = '{"hub_name": "' + hub_name + '", "motor_name": "' + motor_name + '", "power": "\' + str(' + power + ') + \'"}'
    code = code + code_line;

    motor_power_idx = statements_statements.indexOf("set_motor_power", power_being_idx);
    if (motor_power_idx != -1) {
      code = code + ",";
    }
    power_being_idx = motor_power_idx + 15;
  }

  code = code + "]}')\n"
  return code;
};

Blockly.JavaScript['move'] = function (block) {
  var value_motors = Blockly.JavaScript.valueToCode(block, 'motors', Blockly.JavaScript.ORDER_ATOMIC);
  var dropdown_direction = block.getFieldValue('direction');
  var code = "await cait_move(" + value_motors + ", '" + dropdown_direction + "');\n";
  return code;
};

Blockly.Python['move'] = function (block) {
  var value_motors = Blockly.Python.valueToCode(block, 'motors', Blockly.Python.ORDER_ATOMIC);
  var dropdown_direction = block.getFieldValue('direction');
  var code = "move(" + value_motors + ", '" + dropdown_direction + "')\n";
  return code;
};

Blockly.JavaScript['turn'] = function (block) {
  var value_motors = Blockly.JavaScript.valueToCode(block, 'motors', Blockly.JavaScript.ORDER_ATOMIC);
  var number_degree = block.getFieldValue('degree');
  var code = "await cait_rotate(" + value_motors + ", " + number_degree + ");\n";
  return code;
};

Blockly.Python['turn'] = function (block) {
  var value_motors = Blockly.Python.valueToCode(block, 'motors', Blockly.Python.ORDER_ATOMIC);
  var number_degree = block.getFieldValue('degree');
  var code = "turn(" + value_motors + ", " + number_degree + ")\n";
  return code;
};

Blockly.JavaScript['update_pid'] = function (block) {
  var number_error = Blockly.JavaScript.valueToCode(block, 'error', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "await cait_update_pid(" + String(number_error) + ")";
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['update_pid'] = function (block) {
  var number_error = Blockly.Python.valueToCode(block, 'error', Blockly.Python.ORDER_ATOMIC);
  var code = "cait.essentials.update_pid(" + String(number_error) + ")['value']";
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.JavaScript['lights'] = function (block) {
  var dropdown_light = block.getFieldValue('light');
  var dropdown_operation = block.getFieldValue('operation');
  var text_parameter = block.getFieldValue('parameter');
  if (text_parameter != null) {
    var code = "await cait_control_light('" + dropdown_light + "', '" + dropdown_operation + "', '" + text_parameter + "');\n";
  }
  else {
    var code = "await cait_control_light('" + dropdown_light + "', '" + dropdown_operation + "', 'none');\n";
  }
  return code;
};

Blockly.Python['lights'] = function (block) {
  var dropdown_light = block.getFieldValue('light');
  var dropdown_operation = block.getFieldValue('operation');
  var text_parameter = block.getFieldValue('parameter');
  if (text_parameter != null) {
    var code = "cait.essentials.control_light('light." + dropdown_light + "', '" + dropdown_operation + "', '" + text_parameter + "')\n";
  }
  else {
    var code = "cait.essentials.control_light('light." + dropdown_light + "', '" + dropdown_operation + "')\n";
  }
  return code;
};

Blockly.JavaScript['media_player'] = function (block) {
  var dropdown_media_player = block.getFieldValue('media_player');
  var dropdown_operation = block.getFieldValue('operation');
  var code = "await cait_control_media_player('" + dropdown_media_player + "', '" + dropdown_operation + "');\n";
  return code;
};

Blockly.Python['media_player'] = function (block) {
  var dropdown_media_player = block.getFieldValue('media_player');
  var dropdown_operation = block.getFieldValue('operation');
  var code = "cait.essentials.control_media_player('media_player." + dropdown_media_player + "', '" + dropdown_operation + "')\n";
  return code;
};
