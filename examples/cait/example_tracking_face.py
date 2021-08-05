import cait.essentials

face_coordinate = None
screen_center = None
greeted = None
x1 = None
follow_face = None
x2 = None
face_center = None
result = None
rotate_power = None
coordinates = None
name = None

"""Describe this function...
"""
def follow_face2(face_coordinate):
    global screen_center, greeted, x1, follow_face, x2, face_center, result, rotate_power, coordinates, name
    screen_center = 640 / 2
    x1 = face_coordinate[0]
    x2 = face_coordinate[2]
    face_center = x1 + (x2 - x1) / 2
    rotate_power = cait.essentials.update_pid((screen_center - face_center))
    cait.essentials.control_motor_group('{"operation_list" :[{"hub_name": "Robot Inventor: A8:E2:C1:9B:EF:3B", "motor_name": "motor_A", "power": "rotate_power"},{"hub_name": "Robot Inventor: A8:E2:C1:9B:EF:3B", "motor_name": "motor_E", "power": "rotate_power"}]}')
    
    
def setup():
    cait.essentials.initialize_component('vision', processor='oakd', mode=[["add_rgb_cam_node", 640, 360], ["add_rgb_cam_preview_node"],["add_stereo_cam_node", False], ["add_stereo_frame_node"],["add_nn_node_pipeline", "face_detection", "face-detection-retail-0004_openvino_2021.2_6shave.blob", 300, 300],["add_nn_node", "face_landmarks", "landmarks-regression-retail-0009_openvino_2021.2_6shave.blob", 48, 48], ["add_nn_node", "face_features", "mobilefacenet.blob", 112, 112]])
    cait.essentials.initialize_component('control', ['Robot Inventor: A8:E2:C1:9B:EF:3B'])
    cait.essentials.initialize_pid(0.05, 0.00001, 0)
    
def main():
    global face_coordinate, screen_center, greeted, x1, follow_face, x2, face_center, result, rotate_power, coordinates, name
    greeted = False
    follow_face = False
    while True:
        result = cait.essentials.recognize_face()
        cait.essentials.draw_recognized_face(result)
        coordinates = result['coordinate']
        name = result['name']
        if name == 'Michael':
            follow_face2(coordinates)

if __name__ == "__main__":
    setup()
    main()