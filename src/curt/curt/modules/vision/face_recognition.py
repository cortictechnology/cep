""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""


import tvm
from tvm.contrib import graph_runtime
import numpy as np
import time
import cv2
# from skimage import transform as trans
import math
import os
import logging

from curt.modules.vision.base_vision_processing import BaseVisionProcessing
from curt.data import M_PI


class FaceRecognition(BaseVisionProcessing):

    def __init__(self):
        super().__init__(  "cpu", 
                            "tuned_mobilefacenet_graph.json", 
                            "tuned_mobilefacenet_lib.tar", 
                            "tuned_mobilefacenet_param.params", 
                            "data", 
                            1)
        self.input_width = 112
        self.input_height = 112
        self.ref_landmarks = np.array([
            [38.43497931, 52.31110286], 
            [75.87859646, 51.98545311], 
            [55.99915243, 74.61763367], 
            [56.40823808, 93.73636859], 
            [20.25721617, 58.40528653], 
            [96.15278721, 58.09566583]], dtype=np.float32)
        self.ref_landmarks = np.expand_dims(self.ref_landmarks, axis=0)
        self.face_database = {"Names": [], "Features": None}
        self.database_loaded = False


    def config_module(self, params):
        if params["Mode"] == "LoadDatabase":
            self.load_database(params['Data'])
        elif params["Mode"] == "GenDatabase":
            self.generate_database(params['Data'])
        return True

    
    def estimate_norm(self, lmk, image_size):
        assert lmk.shape == (6, 2)
        tform = trans.SimilarityTransform()
        lmk_tran = np.insert(lmk, 2, values=np.ones(6), axis=1)
        min_M = []
        min_index = []
        min_error = float('inf')
        src = self.ref_landmarks / self.input_width
        src = src * float(image_size)
        
        for i in np.arange(src.shape[0]):
            tform.estimate(lmk, src[i])
            M = tform.params[0:2, :]
            results = np.dot(M, lmk_tran.T)
            results = results.T
            error = np.sum(np.sqrt(np.sum((results - src[i]) ** 2, axis=1)))
            if error < min_error:
                min_error = error
                min_M = M
                min_index = i
        return min_M, min_index


    def norm_crop(self, img, landmark, image_size=112):
        M, pose_index = self.estimate_norm(landmark, image_size)
        warped = cv2.warpAffine(img, M, (image_size, image_size), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        return warped


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
        for dir in os.listdir(database_location):
            item = os.path.join(database_location, dir)
            if os.path.isdir(item):
                for file in os.listdir(item):
                    if file.endswith(".bin"):
                        self.face_database["Names"].append(dir)
                        feature = np.fromfile(item+"/features.bin", np.float32)
                        if self.face_database["Features"] is None:
                            self.face_database["Features"] = feature
                        else:
                            self.face_database["Features"] = np.vstack((self.face_database["Features"], feature))


    def preprocess_input(self, input_data):
        preprocessed_data = []
        if self.database_loaded:
            img = input_data[0]
            detected_faces = input_data[1]
            if len(detected_faces) == 0:
                return []
            for face in detected_faces:
                ymin = int(face['face_coordinates'][0] - img.shape[0] * 0.15)
                xmin = int(face['face_coordinates'][1] - img.shape[1] * 0.15)
                ymax = int(face['face_coordinates'][2] + img.shape[0] * 0.15)
                xmax = int(face['face_coordinates'][3] + img.shape[1] * 0.15)
                if ymin < 0:
                    ymin = 0
                if xmin < 0:
                    xmin = 0
                if ymax >= img.shape[0]:
                    ymax = img.shape[0] - 1
                if xmax >= img.shape[1]:
                    xmax = img.shape[1] - 1
                crop_img = img[ymin:ymax, xmin:xmax, :]
                face_landmarks = np.zeros((6, 2))
                for k in range(6):
                    face_landmarks[k, 0] = face['landmark_coordinates'][k*2] - xmin
                    face_landmarks[k, 1] = face['landmark_coordinates'][k*2+1] - ymin
                warp_img = self.norm_crop(crop_img, face_landmarks)
                warp_img = cv2.cvtColor(warp_img, cv2.COLOR_BGR2RGB)
                warp_img = warp_img.transpose((2, 0, 1))
                warp_img = warp_img[np.newaxis, :]
                preprocessed_data.append(warp_img)
        else:
            logging.warning("Face database is not loaded.")
        return preprocessed_data


    def get_best_match_identity(self, similarity_scores, threshold=0.7):
        sort_idx = np.argsort(-similarity_scores)
        #print(sort_idx)
        if similarity_scores[sort_idx[0]] >= threshold:
            return self.face_database["Names"][sort_idx[0]]
        else:
            return "Unknown"


    def postprocess(self, inference_outputs, index=0):
        face_features = inference_outputs[0]
        similarity = np.dot(self.face_database["Features"], face_features.T).squeeze()
        similarity = 1.0 / (1 + np.exp(-1 * (similarity - 0.38) * 10))
        person_name = self.get_best_match_identity(similarity)
        face_info = {}
        face_info['name'] = person_name
        return face_info
