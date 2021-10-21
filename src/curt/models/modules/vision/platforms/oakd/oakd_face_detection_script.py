import marshal
from math import sin, cos, atan2, pi, degrees, floor, dist
import time

img_h = ${_img_h}
img_w = ${_img_w}

fd_score_thresh = ${_fd_score_thresh}

buf0 = Buffer(50)
buf1 = Buffer(186)
buf2 = Buffer(322)

lm_input_size = 48

${_TRACE} ("Starting manager script node")

def send_result(buf, type, detected_faces=[], lm=[]):
    result = dict([("type", type), ("detected_faces", detected_faces), ("face_landmarks", lm)])
    result_serial = marshal.dumps(result)
    data_size = len(result_serial)
    buffer = buf
    ${_TRACE} ("len result:"+str(len(result_serial)))  
    if data_size == 50:
        buffer = buf0 
    elif data_size == 186:
        buffer = buf1
    elif data_size == 322:
        buffer = buf2
    buffer.getData()[:] = result_serial  
    node.io['host'].send(buffer)
    ${_TRACE} ("Manager sent result to host")

def send_identities(buf, identities=[]):
    result = dict([("identities", identities)])
    result_serial = marshal.dumps(result)
    data_size = len(result_serial)
    buffer = buf
    ${_TRACE} ("len result:"+str(len(result_serial)))  
    if data_size == 50:
        buffer = buf0 
    elif data_size == 186:
        buffer = buf1
    elif data_size == 322:
        buffer = buf2
    buffer.getData()[:] = result_serial  
    node.io['identities'].send(buffer)
    ${_TRACE} ("Manager sent identities to host")


def filter_bboxes(raw_detections):
    filtered_detections = []
    for i in range(len(raw_detections) // 7):
        detetion = raw_detections[i * 7: (i+1) * 7]
        if detetion[2] >= fd_score_thresh:
            filtered_detections.append(detetion[3:7])
    return filtered_detections


while True:
    raw_detections = node.io['from_fd_nn'].get().getFirstLayerFp16()
    detected_faces = filter_bboxes(raw_detections)
    face_landmarks = []
    #${_TRACE} ("detected faces:" + str(detected_faces))
    for detection in detected_faces:
        cfg = ImageManipConfig()
        cfg.setCropRect(detection[0], detection[1], detection[2], detection[3])
        cfg.setResize(lm_input_size, lm_input_size)
        node.io['pre_lm_manip_cfg'].send(cfg)
        #${_TRACE} ("Manager sent config to pre_lm manip")     
        lm_result = node.io['from_lm_nn'].get().getFirstLayerFp16()
        #${_TRACE} ("detected landmraks:" + str(lm_result))
        for i in range(5):
            lm_result[i * 2] = lm_result[i * 2] * (detection[2] - detection[0]) + detection[0]
            lm_result[i * 2 + 1] = lm_result[i * 2 + 1] * (detection[3] - detection[1]) + detection[1]
        face_landmarks.append(lm_result)        
    send_result(buf1, 0, detected_faces, face_landmarks)