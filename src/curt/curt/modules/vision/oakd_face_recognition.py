""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

from curt.modules.vision.oakd_processing import OAKDProcessingWorker
import depthai as dai
from curt.modules.vision.utils import *
from curt.modules.vision.utils import decode_image_byte
import numpy as np
import logging
import os
import shutil


class OAKDFaceRecognition(OAKDProcessingWorker):
    def __init__(self):
        super().__init__()
        self.ref_face_landmarks = np.array(
            [
                [38.2946, 51.6963],
                [73.5318, 51.5014],
                [56.0252, 71.7366],
                [41.5493, 92.3655],
                [70.7299, 92.2041],
            ],
            dtype=np.float32,
        )
        self.ref_face_landmarks = np.expand_dims(self.ref_face_landmarks, axis=0)

        self.face_database = {"Names": [], "Features": []}
        self.load_database("/models/database")
        self.modify_face_db__mode = False

    def get_aligned_faces(self, img, detected_faces, largest_face_only=False):
        aligned_faces = []
        detections = []
        face_frames = []
        largest_face_area = 0
        largest_face = None
        largest_detection = []
        for detection in np.array(detected_faces):
            detections.append([detection[0], detection[1], detection[2], detection[3]])

            detection[0] = int(detection[0] * img.shape[1])
            detection[1] = int(detection[1] * img.shape[0])
            detection[2] = int(detection[2] * img.shape[1])
            detection[3] = int(detection[3] * img.shape[0])

            if detection[0] < 0:
                detection[0] = 0
            if detection[1] < 0:
                detection[1] = 0
            if detection[2] > img.shape[1]:
                detection[2] = img.shape[1] - 1
            if detection[3] > img.shape[0]:
                detection[3] = img.shape[0] - 1

            face_frame = img[
                int(detection[1]) : int(detection[3]),
                int(detection[0]) : int(detection[2]),
            ]

            if largest_face_only:
                area = (detection[2] - detection[0]) * (detection[3] - detection[1])
                if area > largest_face_area:
                    largest_face_area = area
                    largest_face = face_frame
                    largest_detection = detection
            else:
                face_frames.append(face_frame)

        if largest_face_area:
            face_landmarks = self.get_face_landmarks(
                self.fl_nn_node_names, largest_face
            )
            for i in range(5):
                face_landmarks[i * 2] = face_landmarks[i * 2] + largest_detection[0]
                face_landmarks[i * 2 + 1] = (
                    face_landmarks[i * 2 + 1] + largest_detection[1]
                )
            face_landmarks = face_landmarks.reshape((-1, 2))
            aligned_face = norm_crop(img, face_landmarks, self.ref_face_landmarks)
            return aligned_face
        else:
            for face_frame in face_frames:
                face_landmarks = self.get_face_landmarks(
                    self.fl_nn_node_names, face_frame
                )
                for i in range(5):
                    face_landmarks[i * 2] = face_landmarks[i * 2] + detection[0]
                    face_landmarks[i * 2 + 1] = face_landmarks[i * 2 + 1] + detection[1]
                face_landmarks = face_landmarks.reshape((-1, 2))
                aligned_face = norm_crop(img, face_landmarks, self.ref_face_landmarks)
                aligned_faces.append(aligned_face)
            return aligned_faces, detections

    def preprocess_input(self, params):
        # if params[0] == "generate_database":
        #     return self.generate_database(params[1], params[2], params[3], params[4])
        if params[0] == "load_database":
            return self.load_database(params[1])
        elif params[0] == "add_person":
            _, person_name, img, detected_faces = params

            self.modify_face_db__mode = True
            if img is None:
                return False
            if len(detected_faces) == 0:
                return False
            if "face_landmarks" not in self.oakd_pipeline.xlink_nodes:
                logging.warning("No such node: face_landmarks in the pipeline")
                return False
            if "face_features" not in self.oakd_pipeline.xlink_nodes:
                logging.warning("No such node: face_features in the pipeline")
                return False
            self.fl_nn_node_names = self.oakd_pipeline.xlink_nodes["face_landmarks"]
            self.ff_nn_node_names = self.oakd_pipeline.xlink_nodes["face_features"]

            aligned_face = self.get_aligned_faces(
                img, detected_faces, largest_face_only=True
            )

            return aligned_face, person_name
        elif params[0] == "remove_person":
            _, person_name = params
            self.modify_face_db__mode = True
            return person_name
        else:
            _, img, detected_faces = params
            self.modify_face_db__mode = False
            if img is None:
                return None
            if "face_landmarks" not in self.oakd_pipeline.xlink_nodes:
                logging.warning("No such node: face_landmarks in the pipeline")
                return None
            if "face_features" not in self.oakd_pipeline.xlink_nodes:
                logging.warning("No such node: face_features in the pipeline")
                return None

            self.fl_nn_node_names = self.oakd_pipeline.xlink_nodes["face_landmarks"]
            self.ff_nn_node_names = self.oakd_pipeline.xlink_nodes["face_features"]

            aligned_faces, detections = self.get_aligned_faces(img, detected_faces)

            return aligned_faces, detections

    def execute_nn_operation(self, preprocessed_data):
        if not self.modify_face_db__mode:
            aligned_faces, detections = preprocessed_data
            all_face_features = []
            for aligned_face in aligned_faces:
                face_features = self.get_face_features(
                    self.ff_nn_node_names, aligned_face
                )
                all_face_features.append(face_features)
            return all_face_features, detections
        else:
            if isinstance(preprocessed_data, tuple):
                aligned_face, person_name = preprocessed_data
                face_features = self.get_face_features(
                    self.ff_nn_node_names, aligned_face
                )
                return face_features, person_name
            else:
                person_name = preprocessed_data
                return person_name

    def postprocess_result(self, inference_results):
        if not self.modify_face_db__mode:
            all_face_features, detections = inference_results
            identities = {}
            for i in range(len(all_face_features)):
                face_features = all_face_features[i]
                detection = detections[i]
                person_name = "Unknown"
                best_match_name = ""
                best_match_confidence = 0.39
                for i in range(len(self.face_database["Names"])):
                    name = self.face_database["Names"][i]
                    features = self.face_database["Features"][i]
                    similarity = np.dot(features, face_features.T).squeeze()
                    if not isinstance(similarity, np.ndarray):
                        similarity = np.array([similarity])
                    similarity = 1.0 / (1 + np.exp(-1 * (similarity - 0.38) * 10))
                    highest_similarity = np.amax(similarity)
                    if highest_similarity > best_match_confidence:
                        best_match_name = name
                        best_match_confidence = highest_similarity
                        # print(highest_similarity)
                if best_match_name != "":
                    person_name = best_match_name
                identities[person_name] = detection
            return identities
        else:
            if isinstance(inference_results, tuple):
                face_features, person_name = inference_results
                new_dir = os.path.join("/models/database", person_name)
                try:
                    os.mkdir(new_dir)
                except OSError:
                    logging.info(
                        "Creation of the directory new person directory failed"
                    )
                    return False
                feature_path = os.path.join(new_dir, "features.bin")
                face_features.tofile(feature_path)
                self.load_database("/models/database")
                return True
            else:
                person_name = inference_results
                try:
                    shutil.rmtree("/models/database/" + person_name)
                except:
                    logging.warning(
                        "Error while removing person, please try again later.."
                    )
                    return False
                self.load_database("/models/database")
                return True

    # def generate_database(
    #     self,
    #     face_detect_nn_node_name,
    #     face_landmark_nn_node_name,
    #     face_feature_node_name,
    #     image_location,
    # ):
    #     for dir in os.listdir(image_location):
    #         item = os.path.join(image_location, dir)
    #         if os.path.isdir(item):
    #             for file_ in os.listdir(item):
    #                 if not file_.endswith(".bin"):
    #                     image_path = os.path.join(item, file_)
    #                     img = cv2.imread(image_path)
    #                     detected_face = self.oakd_pipeline.detect_face(
    #                         face_detect_nn_node_name, img
    #                     )
    #                     if detected_face is not None:
    #                         bbox = frame_norm(img, detected_face)
    #                         face_frame = img[bbox[1] : bbox[3], bbox[0] : bbox[2]]
    #                         face_landmarks = self.oakd_pipeline.get_face_landmarks(
    #                             face_landmark_nn_node_name, face_frame
    #                         )
    #                         for i in range(5):
    #                             face_landmarks[i * 2] = face_landmarks[i * 2] + bbox[0]
    #                             face_landmarks[i * 2 + 1] = (
    #                                 face_landmarks[i * 2 + 1] + bbox[1]
    #                             )
    #                         face_landmarks = face_landmarks.reshape((-1, 2))
    #                         aligned_face = norm_crop(
    #                             img,
    #                             face_landmarks,
    #                             self.ref_face_landmarks,
    #                         )
    #                         face_features = self.oakd_pipeline.get_face_features(
    #                             face_feature_node_name, aligned_face
    #                         )
    #                         face_features.tofile(item + "/features.bin")
    #             print("Done processing:", item)
    #     return True

    def load_database(self, database_location):
        self.face_database = {"Names": [], "Features": []}
        for dir in os.listdir(database_location):
            item = os.path.join(database_location, dir)
            if os.path.isdir(item):
                for file in os.listdir(item):
                    if file.endswith(".bin"):
                        try:
                            feature = np.fromfile(item + "/" + file, np.float32)
                            self.face_database["Names"].append(dir)
                            if len(self.face_database["Features"]) < len(
                                self.face_database["Names"]
                            ):
                                self.face_database["Features"].append(feature)
                            else:
                                self.face_database["Features"][-1] = np.vstack(
                                    (self.face_database["Features"][-1], feature)
                                )
                        except:
                            continue
        return True

    def get_face_landmarks(self, nn_node_names, face_frame):
        frame_lm = dai.ImgFrame()
        frame_lm.setWidth(self.oakd_pipeline.nn_node_input_sizes["face_landmarks"][0])
        frame_lm.setHeight(self.oakd_pipeline.nn_node_input_sizes["face_landmarks"][1])
        frame_lm.setData(
            to_planar(
                face_frame,
                (
                    self.oakd_pipeline.nn_node_input_sizes["face_landmarks"][0],
                    self.oakd_pipeline.nn_node_input_sizes["face_landmarks"][1],
                ),
            )
        )
        self.oakd_pipeline.set_input(nn_node_names[0], frame_lm)
        face_landmarks = self.oakd_pipeline.get_output(
            nn_node_names[1]
        ).getFirstLayerFp16()
        face_landmarks = frame_norm(face_frame, face_landmarks)
        return np.array(face_landmarks)

    def get_face_features(self, nn_node_names, aligned_face):

        frame_fr = dai.ImgFrame()
        frame_fr.setWidth(self.oakd_pipeline.nn_node_input_sizes["face_features"][0])
        frame_fr.setHeight(self.oakd_pipeline.nn_node_input_sizes["face_features"][1])
        frame_fr.setData(
            to_planar(
                aligned_face,
                (
                    self.oakd_pipeline.nn_node_input_sizes["face_features"][0],
                    self.oakd_pipeline.nn_node_input_sizes["face_features"][1],
                ),
            )
        )
        self.oakd_pipeline.set_input(nn_node_names[0], frame_fr)
        face_features = np.array(
            self.oakd_pipeline.get_output(nn_node_names[1]).getFirstLayerFp16()
        ).astype(np.float32)
        face_features_norm = np.linalg.norm(face_features)
        face_features = face_features / face_features_norm
        return face_features
