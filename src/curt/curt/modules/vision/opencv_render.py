""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

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


class OpenCVRender(BaseRender):
    def __init__(self):
        super().__init__()

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
        if people != "None":
            for name in people:
                detection = people[name]
                x1 = int(detection[0])
                y1 = int(detection[1])
                x2 = int(detection[2])
                y2 = int(detection[3])
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
                        img,
                        (x_center - textSize[0] // 2 - 5, y1 - 5),
                        (
                            x_center - textSize[0] // 2 + textSize[0] + 10,
                            y1 - 22,
                        ),
                        color,
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
                if name != "Unknown":
                    self.draw_disconnected_rect(img, (x1, y1), (x2, y2), color, 2)
                    cv2.rectangle(
                        img,
                        (x_center - textSize[0] // 2 - 5, y1 - 22),
                        (
                            x_center - textSize[0] // 2 + textSize[0] + 10,
                            y1 - 39,
                        ),
                        color,
                        -1,
                    )
                    ft.putText(
                        img=img,
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
                        img, (x1, y1), (x2, y2), color, cv2.FONT_HERSHEY_SIMPLEX
                    )
        return img

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
        h, w = img.shape[:2]
        frame_size = max(h, w)
        pad_h = int((frame_size - h) / 2)
        pad_w = int((frame_size - w) / 2)
        img = cv2.copyMakeBorder(img, pad_h, pad_h, pad_w, pad_w, cv2.BORDER_CONSTANT)
        for lm_xy in landmark_coordinates:
            for landmark in lm_xy:
                landmark[0] = landmark[0] + pad_w
                landmark[1] = landmark[1] + pad_h

            palm_line = [np.array([lm_xy[point] for point in [0, 5, 9, 13, 17, 0]])]
            cv2.polylines(img, palm_line, False, (255, 255, 255), 2, cv2.LINE_AA)
            for i in range(len(list_connections)):
                finger = list_connections[i]
                line = [np.array([lm_xy[point] for point in finger])]
                cv2.polylines(img, line, False, FINGER_COLOR[i], 2, cv2.LINE_AA)
                for point in finger:
                    pt = lm_xy[point]
                    cv2.circle(img, (pt[0], pt[1]), 3, JOINT_COLOR[i], -1)
        return img[pad_h : pad_h + h, pad_w : pad_w + w]

    def render_results(self, data, window_id):
        img = None
        if isinstance(data["mirror_oakd_rgb_camera"], str):
            data["mirror_oakd_rgb_camera"] = decode_image_byte(
                data["mirror_oakd_rgb_camera"]
            )
        if data["mirror_oakd_rgb_camera"] is not None:
            img = data["mirror_oakd_rgb_camera"].copy()
            face_data = data["oakd_face_detection"]
            # face_landmarks = data["oakd_face_landmarks"]
            heartrate = data["heartrate_measure"]
            no_face = True
            for detection in face_data:
                no_face = False
                x1 = int(detection[0] * img.shape[1])
                y1 = int(detection[1] * img.shape[0])
                x2 = int(detection[2] * img.shape[1])
                y2 = int(detection[3] * img.shape[0])
                cv2.rectangle(img, (x1, y1), (x2, y2), COLOR[0], 1)

            # for landmarks in face_landmarks:
            #     for pt in landmarks:
            #         cv2.circle(img, (int(pt[0]), int(pt[1])), 2, COLOR[1], -1)

            if not no_face:
                if heartrate == -1:
                    self.draw_object_imgs(
                        img,
                        self.circle_images[self.circle_count],
                        x1,
                        y1 - 35,
                        x1 + 30,
                        y1 + 30,
                    )
                    self.circle_count = self.circle_count + 1
                    if self.circle_count > 39:
                        self.circle_count = 0
                else:
                    self.draw_object_imgs(
                        img,
                        self.heart_images[self.heart_count],
                        x1,
                        y1 - 35,
                        x1 + 30,
                        y1 + 30,
                    )
                    self.heart_count = self.heart_count + 1
                    if self.heart_count > 8:
                        self.heart_count = 0
                    bpm_text = str(int(heartrate)) + " bpm"
                    self.ft.putText(
                        img=img,
                        text=bpm_text,
                        org=(x1 + 35 + 1, y1 - 15 + 1),
                        fontHeight=19,
                        color=(0, 0, 0),
                        thickness=-1,
                        line_type=cv2.LINE_AA,
                        bottomLeftOrigin=True,
                    )
                    self.ft.putText(
                        img=img,
                        text=bpm_text,
                        org=(x1 + 35, y1 - 15),
                        fontHeight=19,
                        color=(255, 255, 255),
                        thickness=-1,
                        line_type=cv2.LINE_AA,
                        bottomLeftOrigin=True,
                    )

        if img is not None:
            # cv2.imshow("img", img)
            # cv2.waitKey(1)
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 40]
            _, buffer = cv2.imencode(".jpg", img, encode_param)
            imgByteArr = base64.b64encode(buffer)
            imgByte = imgByteArr.decode("ascii")
            return (img, imgByte)

        return (None, None)
