""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

from curt.modules.vision.oakd_processing_worker import OAKDProcessingWorker
import depthai as dai
from curt.modules.vision.utils import *
import numpy as np
import logging


class OAKDASL(OAKDProcessingWorker):
    def __init__(self):
        super().__init__()
        self.characters = [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "I",
            "K",
            "L",
            "M",
            "N",
            "O",
            "P",
            "Q",
            "R",
            "S",
            "T",
            "U",
            "V",
            "W",
            "X",
            "Y",
        ]
        self.node_type = "hand_asl"

    def preprocessing(self, params):
        hand_landmarks, img = params
        if img is None:
            return ""
        if self.node_type not in self.oakd_pipeline.xlink_nodes:
            logging.warning("No such node: hand_asl in the pipeline")
            return ""
        self.asl_nn_node_names = self.oakd_pipeline.xlink_nodes[self.node_type]

        self.asl_input_length = self.oakd_pipeline.nn_node_input_sizes[self.node_type][
            0
        ]
        hand_imgs = []
        for landmarks in hand_landmarks:
            hand_bbox = landmarks[1]
            hand_bbox[0] = int(hand_bbox[0] * img.shape[1])
            hand_bbox[1] = int(hand_bbox[1] * img.shape[0])
            hand_bbox[2] = int(hand_bbox[2] * img.shape[1])
            hand_bbox[3] = int(hand_bbox[3] * img.shape[0])
            hand_img = img[hand_bbox[1] : hand_bbox[3], hand_bbox[0] : hand_bbox[2]]
            hand_imgs.append(hand_img)
        return hand_imgs

    def execute_nn_operation(self, preprocessed_data):
        hand_imgs = preprocessed_data
        for hand_img in hand_imgs:
            frame_nn = dai.ImgFrame()
            frame_nn.setWidth(self.oakd_pipeline.nn_node_input_sizes[self.node_type][0])
            frame_nn.setHeight(
                self.oakd_pipeline.nn_node_input_sizes[self.node_type][1]
            )
            frame_nn.setData(
                to_planar(
                    hand_img,
                    (
                        self.oakd_pipeline.nn_node_input_sizes[self.node_type][0],
                        self.oakd_pipeline.nn_node_input_sizes[self.node_type][1],
                    ),
                )
            )
            self.oakd_pipeline.set_input(self.asl_nn_node_names[0], frame_nn)
        raw_asl_results = []
        for i in range(len(hand_imgs)):
            inference = self.oakd_pipeline.get_output(self.asl_nn_node_names[1])
            raw_asl_results.append(inference)
        return raw_asl_results

    def postprocessing(self, inference_result):
        asl_chars = []
        for result in inference_result:
            asl_result = np.array(result.getFirstLayerFp16())
            asl_idx = np.argmax(asl_result)
            asl_char = [self.characters[asl_idx], round(asl_result[asl_idx] * 100, 1)]
            asl_chars.append(asl_char)
        return asl_chars
