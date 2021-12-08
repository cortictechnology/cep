""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""


import tvm
from tvm.contrib import graph_runtime
import numpy as np
import time
import cv2
from curt.modules.vision.utils import *
from skimage import transform as trans
import math
import os
import logging
import shutil

from curt.modules.vision.tvm_processing import TVMProcessing
from curt.data import M_PI


class FaceRecognition(TVMProcessing):

    def __init__(self):
        super().__init__(  "cpu", 
                            "tuned32_2_mobilefacenet_graph.json", 
                            "tuned32_2_mobilefacenet_lib.tar", 
                            "tuned32_2_mobilefacenet_param.params", 
                            "data", 
                            1)
        self.input_width = 112
        self.input_height = 112
        self.ref_face_landmarks = np.array([
            [38.43497931, 52.31110286], 
            [75.87859646, 51.98545311], 
            [55.99915243, 74.61763367], 
            [56.40823808, 93.73636859], 
            [20.25721617, 58.40528653], 
            [96.15278721, 58.09566583]], dtype=np.float32)

        self.ref_face_landmarks = np.expand_dims(self.ref_face_landmarks, axis=0)
        self.face_database = {"Names": [], "Features": []}
        self.load_database("/models/rpi32/database")
        self.modify_face_db__mode = False
        self.friendly_name = "face_recognition_pi"


    def config_worker(self, params):
        if params[0] == "GenDatabase":
            self.generate_database(params[1])
        return True


    def generate_database(self, image_location):
        for dir in os.listdir(image_location):
            item = os.path.join(image_location, dir)
            if os.path.isdir(item):
                for file in os.listdir(item):
                    if not file.endswith(".bin"):
                        image_path = os.path.join(item, file)
                        img = cv2.imread(image_path)
                        detected_faces = self.detect_faces(img)
                        face_features = self.get_face_features(img, detected_faces)[0]
                        face_features.tofile(item+"/features.bin")


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


    def get_aligned_faces(self, img, detected_faces, largest_face_only=False):
        aligned_faces = []
        detections = []
        face_frames = []
        landmarks = []
        largest_face_area = 0
        largest_face = None
        largest_detection = []
        largest_face_landmarks = []
        for face in np.array(detected_faces):
            detection = face['face_coordinates']
            detections.append([detection[0], detection[1], detection[2], detection[3]])

            detection[0] = int(detection[0] * img.shape[1] - img.shape[1] * 0.15)
            detection[1] = int(detection[1] * img.shape[0] - img.shape[0] * 0.15)
            detection[2] = int(detection[2] * img.shape[1] + img.shape[1] * 0.15)
            detection[3] = int(detection[3] * img.shape[0] + img.shape[0] * 0.15)

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

            face_landmarks = np.zeros((6, 2))
            for k in range(6):
                face_landmarks[k, 0] = face['landmark_coordinates'][k*2] * img.shape[1] - detection[0]
                face_landmarks[k, 1] = face['landmark_coordinates'][k*2+1] * img.shape[0] - detection[1]

            if largest_face_only:
                area = (detection[2] - detection[0]) * (detection[3] - detection[1])
                if area > largest_face_area:
                    largest_face_area = area
                    largest_face = face_frame
                    largest_detection = detection
                    largest_face_landmarks = face_landmarks
            else:
                face_frames.append(face_frame)
                landmarks.append(face_landmarks)

        if largest_face_area:
            aligned_face = norm_crop(largest_face, largest_face_landmarks, self.ref_face_landmarks)
            aligned_face = cv2.cvtColor(aligned_face, cv2.COLOR_BGR2RGB)
            aligned_face = aligned_face.transpose((2, 0, 1))
            aligned_face = aligned_face[np.newaxis, :]
            return aligned_face, largest_detection
        else:
            for i in range(len(face_frames)):
                face_frame = face_frames[i]
                face_landmarks = landmarks[i]
                aligned_face = norm_crop(face_frame, face_landmarks, self.ref_face_landmarks)
                aligned_face = cv2.cvtColor(aligned_face, cv2.COLOR_BGR2RGB)
                aligned_face = aligned_face.transpose((2, 0, 1))
                aligned_face = aligned_face[np.newaxis, :]
                aligned_faces.append(aligned_face)
            return aligned_faces, detections


    def preprocess_input(self, params):
        if params[0] == "load_database":
            return self.load_database(params[1])
        elif params[0] == "add_person":
            _, person_name, img, detected_faces = params
            self.modify_face_db__mode = True
            if img is None:
                return False
            if len(detected_faces) == 0:
                return False
            aligned_face, _ = self.get_aligned_faces(
                img, detected_faces, largest_face_only=True
            )
            return aligned_face, person_name
        elif params[0] == "remove_person":
            _, person_name = params
            self.modify_face_db__mode = True
            return person_name
        else:
            _, img, detected_faces = params
            if len(detected_faces) == 0:
                return None
            self.modify_face_db__mode = False
            if img is None:
                return None
            aligned_faces, detections = self.get_aligned_faces(img, detected_faces)
            return aligned_faces, detections


    def process_data(self, preprocessed_data):
        if not self.modify_face_db__mode:
            aligned_faces, detections = preprocessed_data
            all_face_features = self.tvm_process(aligned_faces)
            return all_face_features, detections
        else:
            if isinstance(preprocessed_data, tuple):
                aligned_face, person_name = preprocessed_data
                face_features = self.tvm_process(aligned_face)[0][0]
                return face_features, person_name
            else:
                person_name = preprocessed_data
                return person_name


    def postprocess_result(self, data):
        if not self.modify_face_db__mode:
            all_face_features, detections = data
            identities = {}
            for i in range(len(all_face_features)):
                face_features = all_face_features[i][0]
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
                if best_match_name != "":
                    person_name = best_match_name
                identities[person_name] = detection
            return identities
        else:
            if isinstance(data, tuple):
                face_features, person_name = data
                new_dir = os.path.join("/models/rpi32/database", person_name)
                if not (os.path.exists(new_dir)):
                    try:
                        os.mkdir(new_dir)
                    except OSError:
                        logging.info(
                            "Creation of the directory new person directory failed"
                        )
                        return False
                feature_path = os.path.join(new_dir, "features.bin")
                face_features.tofile(feature_path)
                self.load_database("/models/rpi32/database")
                return True
            else:
                person_name = data
                try:
                    shutil.rmtree("/models/rpi32/database/" + person_name)
                except Exception as e:
                    logging.warning(
                        "Error while removing person, please try again later.."
                    )
                    return False
                self.load_database("/models/rpi32/database")
                return True