""" 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

import paho.mqtt.client as mqtt
import logging
import cv2
import socket
import base64
import numpy as np
from .core_data import *

logging.getLogger().setLevel(logging.INFO)

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def connect_mqtt(client, address):
    try:
        client.connect(address, 1883, 60)
        logging.info("Connected to broker")
        client.loop_start()
        return True
    except:
        logging.info("Broker: (" + address + ") not up yet, retrying...")
        return False


def decode_image_byte(image_data):
    jpg_original = base64.b64decode(image_data)
    jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
    image = cv2.imdecode(jpg_as_np, flags=1)
    return image


def draw_disconnected_rect(img, pt1, pt2, color, thickness):
    width = pt2[0] - pt1[0]
    height = pt2[1] - pt1[1]
    line_width = min(20, width // 4)
    line_height = min(20, height // 4)
    line_length = max(line_width, line_height)
    cv2.line(img, pt1, (pt1[0] + line_length, pt1[1]), color, thickness)
    cv2.line(img, pt1, (pt1[0], pt1[1] + line_length), color, thickness)
    cv2.line(img, (pt2[0] - line_length, pt1[1]), (pt2[0], pt1[1]), color, thickness)
    cv2.line(img, (pt2[0], pt1[1]), (pt2[0], pt1[1] + line_length), color, thickness)
    cv2.line(img, (pt1[0], pt2[1]), (pt1[0] + line_length, pt2[1]), color, thickness)
    cv2.line(img, (pt1[0], pt2[1] - line_length), (pt1[0], pt2[1]), color, thickness)
    cv2.line(img, pt2, (pt2[0] - line_length, pt2[1]), color, thickness)
    cv2.line(img, (pt2[0], pt2[1] - line_length), pt2, color, thickness)


def draw_face_detection(img, bboxes):
    for bbox in bboxes:
        if isinstance(bbox, dict):
            bbox = bbox["face_coordinates"]
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
        draw_disconnected_rect(img, (x1, y1), (x2, y2), COLOR[0], 2)
    return img


def draw_face_recognition(img, names, coordinates):
    for i in range(len(names)):
        name = names[i]
        detection = coordinates[i]
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
            draw_disconnected_rect(img, (x1, y1), (x2, y2), color, 2)
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
                img,
                (x1, y1),
                (
                    x2,
                    y1 - 18,
                ),
                color,
                -1,
            )
            ft.putText(
                img=img,
                text="Unknown",
                org=(x1 + 3, y1 - 3),
                fontHeight=15,
                color=(255, 255, 255),
                thickness=-1,
                line_type=cv2.LINE_AA,
                bottomLeftOrigin=True,
            )
            cv2.rectangle(img, (x1, y1), (x2, y2), color, cv2.FONT_HERSHEY_SIMPLEX)
    return img


def draw_object_detection(img, names, coordinates):
    for i in range(len(names)):
        bbox = coordinates[i]
        label = names[i]
        x1 = int(bbox[0])
        y1 = int(bbox[1])
        x2 = int(bbox[2])
        y2 = int(bbox[3])
        if x1 < 0:
            x1 = 0
        if y1 < 0:
            y1 = 0
        if x2 >= img.shape[1]:
            x2 = img.shape[1] - 1
        if y2 >= img.shape[1]:
            y2 = img.shape[1] - 1

        sub_img = img[y1:y2, x1:x2]
        rect = np.ones(sub_img.shape, dtype=np.uint8)
        label_idx = object_labels.index(label)
        rect[:, :, 0] = OBJ_COLOR[label_idx][0]
        rect[:, :, 1] = OBJ_COLOR[label_idx][1]
        rect[:, :, 2] = OBJ_COLOR[label_idx][2]
        res = cv2.addWeighted(sub_img, 0.7, rect, 0.3, 1.0)
        img[y1:y2, x1:x2] = res
        draw_disconnected_rect(img, (x1, y1), (x2, y2), (255, 255, 255), 2)
        object_text = label
        if len(bbox) > 4:
            obj_distance = bbox[6]
            object_text = label + ", " + str(round(obj_distance / 1000, 1)) + "m"

        textSize = ft.getTextSize(object_text, fontHeight=19, thickness=-1)[0]
        cv2.rectangle(
            img,
            (x1, y1 - 1),
            (x1 + textSize[0] + 10, y1 - 8 - textSize[1] - 26),
            OBJ_COLOR[label_idx],
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

def draw_image_classification(img, names):
    logging.warning(str(names))
    for i in range(len(names)):
        name = names[i][0]
        prob = names[i][1]
        text = "{:.1f}".format(prob * 100) + "% - " + name
        ft.putText(
            img=img,
            text=text,
            org=(9, 30+30*i-1),
            fontHeight=25,
            color=(0, 0, 0),
            thickness=-1,
            line_type=cv2.LINE_AA,
            bottomLeftOrigin=True,
        )
        ft.putText(
            img=img,
            text=text,
            org=(10, 30+30*i),
            fontHeight=25,
            color=(255,255,255),
            thickness=-1,
            line_type=cv2.LINE_AA,
            bottomLeftOrigin=True,
        )

    return img

def draw_face_emotions(img, emotions):
    for emotion in emotions:
        probabilities = emotion[0]
        bbox = emotion[1]
        x1 = int(bbox[0])
        y1 = int(bbox[1])
        x2 = int(bbox[2])
        y2 = int(bbox[3])
        width = x2 - x1
        height = y2 - y1
        draw_disconnected_rect(img, (x1, y1), (x2, y2), COLOR[0], 2)
        start_y = y1 + 3
        start_x = x2 + 3
        bar_length = width
        bar_height = int(height - 6) / 5
        bar_space = 4
        for i in range(5):
            x1 = int(start_x)
            x2 = int(x1 + probabilities[emotion_types[i]] * bar_length)
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


def draw_facemesh(img, facemeshes):
    for facemesh in facemeshes:
        for i in range(int(triangulation.shape[0] / 3)):
            pt1 = np.array(facemesh[triangulation[i * 3]][0:2], np.int32)
            pt2 = np.array(facemesh[triangulation[i * 3 + 1]][0:2], np.int32)
            pt3 = np.array(facemesh[triangulation[i * 3 + 2]][0:2], np.int32)
            cv2.line(img, (pt1[0], pt1[1]), (pt2[0], pt2[1]), COLOR[1], thickness=1)
            cv2.line(img, (pt2[0], pt2[1]), (pt3[0], pt3[1]), COLOR[1], thickness=1)
            cv2.line(img, (pt3[0], pt3[1]), (pt1[0], pt1[1]), COLOR[1], thickness=1)
    return img


def draw_body_landmarks(img, landmark_coordinates):
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
                    img,
                    (int(landmark[0] * img.shape[1]), int(landmark[1])),
                    4,
                    (255, 255, 255),
                    1,
                )
                cv2.circle(
                    img,
                    (int(landmark[0] * img.shape[1]), int(landmark[1])),
                    3,
                    POSE_JOINT_COLOR[i],
                    -1,
                )
    return img


def draw_hand_landmarks(img, landmark_coordinates):
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
    for lm in landmark_coordinates:
        lm_xy = []
        for landmark in lm:
            lm_xy.append([int(landmark[0]), int(landmark[1])])
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
