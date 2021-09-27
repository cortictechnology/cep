import numpy as np
from curt.data import triangulation
from curt.modules.vision.utils import *
from curt.modules.vision.base_render import BaseRender
from curt.modules.vision.utils import decode_image_byte
import cv2
import base64
import time
import os
import threading
import logging

class OpenCVRender(BaseRender):
    def __init__(self):
        super().__init__()
        self.img = None
        self.drawing_data = {
            "Depth Mode": False,
            "Face Detection": [],
            "Face Recognition": [],
            "Face Emotions": [],
            "Face Mesh": [],
            "Object Detection": [],
            "Hand Landmarks": [],
            "Pose Landmarks": [],
        }
        self.drawed = {
            "Face Detection": False, 
            "Face Mesh": False,
            "Face Recognition": False,
            "Face Emotions": False,
            "Object Detection": False,
            "Hand Landmarks": False,
            "Pose Landmarks": False
        }
        self.display_thread = threading.Thread(target=self.display_func, daemon=True)
        self.display_thread.start()


    def config_module(self, data):
        result = super().config_module(data)

    def draw_disconnected_rect(self, img, pt1, pt2, color, thickness):
        width = pt2[0] - pt1[0]
        height = pt2[1] - pt1[1]
        line_width = min(20, width // 4)
        line_height = min(20, height // 4)
        line_length = max(line_width, line_height)
        cv2.line(img, pt1, (pt1[0] + line_length, pt1[1]), color, thickness)
        cv2.line(img, pt1, (pt1[0], pt1[1] + line_length), color, thickness)
        cv2.line(
            img, (pt2[0] - line_length, pt1[1]), (pt2[0], pt1[1]), color, thickness
        )
        cv2.line(
            img, (pt2[0], pt1[1]), (pt2[0], pt1[1] + line_length), color, thickness
        )
        cv2.line(
            img, (pt1[0], pt2[1]), (pt1[0] + line_length, pt2[1]), color, thickness
        )
        cv2.line(
            img, (pt1[0], pt2[1] - line_length), (pt1[0], pt2[1]), color, thickness
        )
        cv2.line(img, pt2, (pt2[0] - line_length, pt2[1]), color, thickness)
        cv2.line(img, (pt2[0], pt2[1] - line_length), pt2, color, thickness)

    def render(self, data):
        success = super().render(data)
        return success

    def draw_face_detection(self, img, bboxes):
        for bbox in bboxes:
            x1 = int(bbox[0])
            y1 = int(bbox[1])
            x2 = int(bbox[2])
            y2 = int(bbox[3])
            x_center = int(x1 + (x2 - x1) / 2)
            if len(bbox) == 5:
                face_distance = bbox[4]
                z_text = f"Distance: {int(face_distance)} mm"
                textSize = ft.getTextSize(z_text, fontHeight=14, thickness=-1)[0]
                cv2.rectangle(
                    img,
                    (x_center - textSize[0] // 2 - 5, y1 - 5),
                    (
                        x_center - textSize[0] // 2 + textSize[0] + 10,
                        y1 - 22,
                    ),
                    COLOR[0],
                    -1,
                )
                ft.putText(
                    img=img,
                    text=z_text,
                    org=(x_center - textSize[0] // 2, y1 - 8),
                    fontHeight=14,
                    color=(255, 255, 255),
                    thickness=-1,
                    line_type=cv2.LINE_AA,
                    bottomLeftOrigin=True,
                )
            self.draw_disconnected_rect(img, (x1, y1), (x2, y2), COLOR[0], 2)
        return img

    def draw_face_recognition(self, img, people):
        image = img.copy()
        if people != "None":
            for name in people:
                detection = people[name]
                x1 = int(detection[0] * image.shape[1])
                y1 = int(detection[1] * image.shape[0])
                x2 = int(detection[2] * image.shape[1])
                y2 = int(detection[3] * image.shape[0])
                x_center = int(x1 + (x2 - x1) / 2)
                color = COLOR[2]
                if name != "Unknown":
                    color = COLOR[1]
                name_text = "Name: " + name
                textSize = ft.getTextSize(name_text, fontHeight=15, thickness=-1)[0]
                if len(detection) == 5:
                    face_distance = detection[4]
                    z_text = f"Distance: {int(face_distance)} mm"
                    textSize = ft.getTextSize(z_text, fontHeight=15, thickness=-1)[0]
                    cv2.rectangle(
                        image,
                        (x_center - textSize[0] // 2 - 5, y1 - 5),
                        (
                            x_center - textSize[0] // 2 + textSize[0] + 10,
                            y1 - 22,
                        ),
                        color,
                        -1,
                    )
                    ft.putText(
                        img=image,
                        text=z_text,
                        org=(x_center - textSize[0] // 2, y1 - 8),
                        fontHeight=14,
                        color=(255, 255, 255),
                        thickness=-1,
                        line_type=cv2.LINE_AA,
                        bottomLeftOrigin=True,
                    )
                if name != "Unknown":
                    self.draw_disconnected_rect(image, (x1, y1), (x2, y2), color, 2)
                    cv2.rectangle(
                        image,
                        (x_center - textSize[0] // 2 - 5, y1 - 22),
                        (
                            x_center - textSize[0] // 2 + textSize[0] + 10,
                            y1 - 39,
                        ),
                        color,
                        -1,
                    )
                    ft.putText(
                        img=image,
                        text=name_text,
                        org=(x_center - textSize[0] // 2, y1 - 25),
                        fontHeight=15,
                        color=(255, 255, 255),
                        thickness=-1,
                        line_type=cv2.LINE_AA,
                        bottomLeftOrigin=True,
                    )
                else:
                    cv2.rectangle(
                        image, (x1, y1), (x2, y2), color, cv2.FONT_HERSHEY_SIMPLEX
                    )
        return image

    def draw_object_detection(self, img, names, coordinates):
        for i in range(len(coordinates)):
            bbox = coordinates[i]
            label = names[i]
            x1 = int(bbox[0])
            y1 = int(bbox[1])
            x2 = int(bbox[2])
            y2 = int(bbox[3])
            obj_distance = bbox[6]
            sub_img = img[y1:y2, x1:x2]
            rect = np.ones(sub_img.shape, dtype=np.uint8)
            rect[:, :, 0] = OBJ_COLOR[label][0]
            rect[:, :, 1] = OBJ_COLOR[label][1]
            rect[:, :, 2] = OBJ_COLOR[label][2]
            res = cv2.addWeighted(sub_img, 0.7, rect, 0.3, 1.0)
            img[y1:y2, x1:x2] = res
            self.draw_disconnected_rect(img, (x1, y1), (x2, y2), (255, 255, 255), 2)
            object_text = (
                object_labels[label] + ", " + str(round(obj_distance / 1000, 1)) + "m"
            )

            textSize = ft.getTextSize(object_text, fontHeight=19, thickness=-1)[0]
            cv2.rectangle(
                img,
                (x1, y1 - 1),
                (x1 + textSize[0] + 10, y1 - 8 - textSize[1] - 16),
                OBJ_COLOR[label],
                -1,
            )
            ft.putText(
                img=img,
                text=object_text,
                org=(x1 + 5, y1 - 14),
                fontHeight=19,
                color=(255, 255, 255),
                thickness=-1,
                line_type=cv2.LINE_AA,
                bottomLeftOrigin=True,
            )
        return img

    def draw_face_emotions(self, img, emotions):
        for emotion in emotions:
            probabilities = emotion[0]
            bbox = emotion[1]
            x1 = int(bbox[0])
            y1 = int(bbox[1])
            x2 = int(bbox[2])
            y2 = int(bbox[3])
            width = x2 - x1
            height = y2 - y1
            self.draw_disconnected_rect(img, (x1, y1), (x2, y2), COLOR[0], 1)
            start_y = y1 + 3
            start_x = x2 + 3
            bar_length = width
            bar_height = int(height - 6) / 5
            bar_space = 4
            for i in range(5):
                x1 = int(start_x)
                x2 = int(x1 + probabilities[i] * bar_length)
                y1 = int(start_y + i * bar_height)
                y2 = int(y1 + bar_height - bar_space)
                cv2.rectangle(
                    img,
                    (x1, y1),
                    (x2, y2),
                    EMOTION_COLORS[i],
                    -1,
                )
                emotion_text = EMOTIONS[i]
                textHeight = int(bar_height * 0.55)
                ft.putText(
                    img=img,
                    text=emotion_text,
                    org=(x1 + 2, y2 - int(bar_height * 0.3)),
                    fontHeight=textHeight,
                    color=(255, 255, 255),
                    thickness=-1,
                    line_type=cv2.LINE_AA,
                    bottomLeftOrigin=True,
                )
        return img

    def draw_facemesh(self, img, facemeshes):
        for facemesh in facemeshes:
            for i in range(int(triangulation.shape[0] / 3)):
                pt1 = np.array(facemesh[triangulation[i * 3]][0:2], np.int32)
                pt2 = np.array(facemesh[triangulation[i * 3 + 1]][0:2], np.int32)
                pt3 = np.array(facemesh[triangulation[i * 3 + 2]][0:2], np.int32)
                cv2.line(img, (pt1[0], pt1[1]), (pt2[0], pt2[1]), COLOR[1], thickness=1)
                cv2.line(img, (pt2[0], pt2[1]), (pt3[0], pt3[1]), COLOR[1], thickness=1)
                cv2.line(img, (pt3[0], pt3[1]), (pt1[0], pt1[1]), COLOR[1], thickness=1)
        return img

    def draw_body_landmarks(self, img, landmark_coordinates):
        if landmark_coordinates is not None:
            for i in range(len(LINES_BODY)):
                line = LINES_BODY[i]
                start_x = int(landmark_coordinates[line[0]][0])
                start_y = int(landmark_coordinates[line[0]][1])
                end_x = int(landmark_coordinates[line[1]][0])
                end_y = int(landmark_coordinates[line[1]][1])
                cv2.line(
                    img,
                    (start_x, start_y),
                    (end_x, end_y),
                    POSE_LINE_COLORS[i],
                    2,
                )
            not_draw_pts = [17, 18, 19, 20, 21, 22]
            for i in range(11, len(landmark_coordinates) - 2):
                if i not in not_draw_pts:
                    landmark = landmark_coordinates[i]
                    cv2.circle(
                        img, (int(landmark[0]), int(landmark[1])), 4, (255, 255, 255), 1
                    )
                    cv2.circle(
                        img,
                        (int(landmark[0]), int(landmark[1])),
                        3,
                        POSE_JOINT_COLOR[i],
                        -1,
                    )
        return img

    def draw_hand_landmarks(self, img, landmark_coordinates):
        list_connections = [
            [0, 1, 2, 3, 4],
            [5, 6, 7, 8],
            [9, 10, 11, 12],
            [13, 14, 15, 16],
            [17, 18, 19, 20],
        ]
        # h, w = img.shape[:2]
        # frame_size = max(h, w)
        # pad_h = int((frame_size - h) / 2)
        # pad_w = int((frame_size - w) / 2)
        # img = cv2.copyMakeBorder(img, pad_h, pad_h, pad_w, pad_w, cv2.BORDER_CONSTANT)
        for lm_xy in landmark_coordinates:
            # for landmark in lm_xy:
            #    landmark[0] = landmark[0] + pad_w
            #    landmark[1] = landmark[1] + pad_h

            palm_line = [np.array([lm_xy[point] for point in [0, 5, 9, 13, 17, 0]])]
            cv2.polylines(img, palm_line, False, (255, 255, 255), 2, cv2.LINE_AA)
            for i in range(len(list_connections)):
                finger = list_connections[i]
                line = [np.array([lm_xy[point] for point in finger])]
                cv2.polylines(img, line, False, FINGER_COLOR[i], 2, cv2.LINE_AA)
                for point in finger:
                    pt = lm_xy[point]
                    cv2.circle(img, (pt[0], pt[1]), 3, JOINT_COLOR[i], -1)
        # return img[pad_h : pad_h + h, pad_w : pad_w + w]
        return img

    def render_results(self, data, window_id):
        if "oakd_rgb_camera_input" in data:
            if isinstance(data["oakd_rgb_camera_input"], str):
                data["oakd_rgb_camera_input"] = decode_image_byte(
                    data["oakd_rgb_camera_input"]
                )
            if data["oakd_rgb_camera_input"] is not None:
                self.img = data["oakd_rgb_camera_input"]
                self.drawed = {
                    "Face Detection": False, 
                    "Face Mesh": False,
                    "Face Recognition": False,
                    "Face Emotions": False,
                    "Object Detection": False,
                    "Hand Landmarks": False,
                    "Pose Landmarks": False
                }
        if "oakd_face_detection" in data:
            if data["oakd_face_detection"] is not None:
                self.drawing_data["Face Detection"] = data
        if "oakd_facemesh" in data:
            if data["oakd_facemesh"] is not None:
                self.drawing_data["Face Mesh"] = data["oakd_facemesh"]
        if "oakd_face_recognition" in data:
            if data["oakd_face_recognition"] is not None:
                self.drawing_data["Face Recognition"] = data["oakd_face_recognition"]
        if "oakd_pose_estimation" in data:
            if data["oakd_pose_estimation"] is not None:
                self.drawing_data["Pose Landmarks"] = data["oakd_pose_estimation"]
        if "oakd_hand_landmarks" in data:
            if data["oakd_hand_landmarks"] is not None:
                hand_landmarks_coordinates = []
                for landmarks in data["oakd_hand_landmarks"]:
                    hand_landmarks_coordinates.append(landmarks[0])
                self.drawing_data["Hand Landmarks"] = hand_landmarks_coordinates     

        return True

    def display_func(self):
        while True:
            if self.img is not None:
                if self.drawing_data["Hand Landmarks"] != [] and not self.drawed["Hand Landmarks"]:
                    self.img = self.draw_hand_landmarks(self.img, self.drawing_data["Hand Landmarks"])
                    self.drawed["Hand Landmarks"] = True
                if self.drawing_data["Face Mesh"] != [] and not self.drawed["Face Mesh"]:
                    self.img = self.draw_facemesh(self.img, self.drawing_data["Face Mesh"])
                    self.drawed["Face Mesh"] = True
                if self.drawing_data["Face Recognition"] != [] and not self.drawed["Face Recognition"]:
                    self.img = self.draw_face_recognition(self.img, self.drawing_data["Face Recognition"])
                    self.drawed["Face Recognition"] = True
                if self.drawing_data["Pose Landmarks"] != [] and not self.drawed["Pose Landmarks"]:
                    self.img = self.draw_body_landmarks(self.img, self.drawing_data["Pose Landmarks"])
                    self.drawed["Pose Landmarks"] = True
                cv2.imshow("Visualization", self.img)
                cv2.waitKey(1)
            else:
                time.sleep(0.001)
