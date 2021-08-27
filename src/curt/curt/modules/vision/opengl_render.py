""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Ye Lu <ye.lu@cortic.ca>, 2021

"""

# need to provide file storage
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
from gem import matrix
from gem import vector
from curt.data import triangulation
from curt.modules.vision.base_render import BaseRender


class OpenglRender(BaseRender):
    def __init__(self):
        super().__init__()

    def config_module(self, data):
        result = super().config_module(data)

        self.init_window(self.container_size[0], self.container_size[1])
        self.init_opengl()

        return result

    def render(self, data):
        success = super().render(data)
        glutSwapBuffers()

        return success

    def draw_face_bbox(self, data, window_id):
        window_prop = self.window_properties[window_id]
        img = data["camera_input"]
        self.setup_window(window_id, window_prop, img)
        x_scale, y_scale = self.calc_scale(window_prop, img)

        glColor4f(0.26, 0.74, 0.59, 0.5)
        glBegin(GL_QUADS)
        face_data = data["face_detection"]
        for face in face_data:
            x1 = face["face_coordinates"][1] * x_scale
            y1 = face["face_coordinates"][0] * y_scale
            x2 = face["face_coordinates"][3] * x_scale
            y2 = face["face_coordinates"][2] * y_scale
            glVertex2f(x1, y1)
            glVertex2f(x1, y2)
            glVertex2f(x2, y2)
            glVertex2f(x2, y1)
        glEnd()

        return True

    def draw_face_bbox2(self, data, window_id):
        window_prop = self.window_properties[window_id]
        img = data["camera_input"]
        self.setup_window(window_id, window_prop, img)
        x_scale, y_scale = self.calc_scale(window_prop, img)

        face_data = data["face_detection"]

        return True

    def draw_facemesh(self, data, window_id):
        window_prop = self.window_properties[window_id]
        img = data["camera_input"]
        self.setup_window(window_id, window_prop, img)
        x_scale, y_scale = self.calc_scale(window_prop, img)

        all_face_landmarks = None
        face_mesh_data = data["face_mesh"]
        for face in face_mesh_data:
            # coordinates = face['mesh_coordinates'].copy()
            coordinates = np.array(face["mesh_coordinates"], dtype=np.float32)
            coordinates[:, 0] = coordinates[:, 0] * x_scale
            coordinates[:, 1] = coordinates[:, 1] * y_scale
            coordinates[:, 2] = coordinates[:, 2] * x_scale
            landmarks = coordinates[triangulation]
            if all_face_landmarks is None:
                all_face_landmarks = landmarks
            else:
                all_face_landmarks = np.vstack((all_face_landmarks, landmarks))

        if not all_face_landmarks is None:
            base = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float32)
            vertex_id_array = np.tile(base, (int(all_face_landmarks.shape[0] / 3), 1))
            self.render_facemesh(all_face_landmarks, vertex_id_array, window_prop)

        return True

    def draw_facemesh2(self, data, window_id):
        window_prop = self.window_properties[window_id]
        img = data["camera_input"]
        self.setup_window(window_id, window_prop, img)
        x_scale, y_scale = self.calc_scale(window_prop, img)

        all_face_landmarks = None
        face_mesh_data = data["face_mesh"]
        return True

    def draw_face_bbox_and_text(self, data, window_id):
        face_data = data["face_detection"]
        face_name = data["face_name"]
        pass

    def draw_object_bbox_and_text(self, data, window_id):
        pass

    def init_window(self, width, height):
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)

        glutInitWindowPosition(0, 0)
        glutInitWindowSize(width, height)
        glutCreateWindow("Vision Service")

    def init_opengl(self):
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glClearColor(0.0, 0.0, 0.0, 1.0)

        self.video_program = self.load_shaders(
            os.path.dirname(os.path.realpath(__file__)) + "/shaders/video_vertex.glsl",
            os.path.dirname(os.path.realpath(__file__)) + "/shaders/video_frag.glsl",
        )
        self.facemesh_program = self.load_shaders(
            os.path.dirname(os.path.realpath(__file__))
            + "/shaders/facemesh_vertex.glsl",
            os.path.dirname(os.path.realpath(__file__)) + "/shaders/facemesh_frag.glsl",
        )
        self.vao_list = glGenVertexArrays(2)
        self.texture_list = glGenTextures(2)

    def setup_viewport(self, window_prop):
        window_pos = window_prop["top_left"]
        window_size = window_prop["size"]

        glViewport(
            window_pos[0],
            self.container_size[1] - (window_pos[1] + window_size[1]),
            window_size[0],
            window_size[1],
        )
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, window_size[0], 0, window_size[1])
        glScalef(1, -1, 1)
        glTranslatef(0, -window_size[1], 0)
        glMatrixMode(GL_MODELVIEW)

    def setup_window(self, window_id, window_prop, img):
        window_pos = window_prop["top_left"]
        window_size = window_prop["size"]
        self.setup_viewport(window_prop)
        if not self.video_frame[window_id]:
            self.setup_video(window_size[0], window_size[1])
            # self.draw_frame(img)
            self.video_frame[window_id] = True

    def calc_scale(self, window_prop, img):
        x_scale = window_prop["size"][0] / img.shape[1]
        y_scale = window_prop["size"][1] / img.shape[0]
        return x_scale, y_scale

    def load_shaders(self, vertex_shader, fragment_shader):
        with open(vertex_shader) as vertex_shader:
            vertex_src = vertex_shader.read()
        with open(fragment_shader) as frag_shader:
            frag_src = frag_shader.read()

        vert_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vert_shader, vertex_src)
        glCompileShader(vert_shader)

        if glGetShaderiv(vert_shader, GL_COMPILE_STATUS) != GL_TRUE:
            raise RuntimeError(glGetShaderInfoLog(vert_shader))

        frag_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(frag_shader, frag_src)
        glCompileShader(frag_shader)

        if glGetShaderiv(frag_shader, GL_COMPILE_STATUS) != GL_TRUE:
            raise RuntimeError(glGetShaderInfoLog(frag_shader))

        program = glCreateProgram()

        glAttachShader(program, vert_shader)
        glAttachShader(program, frag_shader)

        glLinkProgram(program)

        return program

    def setup_video(self, width, height):
        glUseProgram(self.video_program)
        vertices = np.array(
            [0.0, 0.0, 0.0, height, width, height, width, 0.0], dtype=np.float32
        )

        tex_coords = np.array(
            [0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0], dtype=np.float32
        )
        itemsize = np.dtype("float32").itemsize

        glBindVertexArray(self.vao_list[0])

        vbo_id = glGenBuffers(3)

        # set the vertex
        # glBindBuffer(GL_ARRAY_BUFFER, vbo_id[0])
        # glBufferData(GL_ARRAY_BUFFER, itemsize *
        #             vertices.size, vertices, GL_STATIC_DRAW)
        # coords_attrib_location = glGetAttribLocation(self.video_program, 'a_vertex')
        # glVertexAttribPointer(coords_attrib_location, 2,
        #                     GL_FLOAT, GL_FALSE, 0, None)
        # glEnableVertexAttribArray(coords_attrib_location)

        # # set the texture coordinates
        # glBindBuffer(GL_ARRAY_BUFFER, vbo_id[2])
        # glBufferData(GL_ARRAY_BUFFER, itemsize *
        #             tex_coords.size, tex_coords, GL_STATIC_DRAW)
        # tex_coords_attrib_location = glGetAttribLocation(
        #     self.video_program, 'a_tex_coord')
        # glVertexAttribPointer(tex_coords_attrib_location, 2,
        #                     GL_FLOAT, GL_FALSE, 0, None)
        # glEnableVertexAttribArray(tex_coords_attrib_location)

        glBindBuffer(GL_ARRAY_BUFFER, vbo_id[0])
        glBufferData(
            GL_ARRAY_BUFFER,
            32,
            np.array(
                [0.0, 0.0, 0.0, 100.0, 100.0, 100.0, 100.0, 0.0], dtype=np.float32
            ),
            GL_STATIC_DRAW,
        )
        # coords_attrib_location = glGetAttribLocation(self.video_program, 'a_vertex')

        # set the projection matrix
        projection_matrix = matrix.orthographic(0.0, width, height, 0.0, -1.0, 1.0)
        projection_matrix_location = glGetUniformLocation(
            self.video_program, "u_projection_matrix"
        )
        glUniformMatrix4fv(
            projection_matrix_location, 1, GL_FALSE, projection_matrix.matrix
        )

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glUseProgram(0)

    def draw_frame(self, img):
        glUseProgram(self.video_program)
        glEnable(GL_TEXTURE_2D)

        glActiveTexture(GL_TEXTURE0)
        texture_location = glGetUniformLocation(self.video_program, "video_texture")
        glUniform1i(texture_location, 0)

        # print("***********************************************")
        # print(img.shape)
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA8,
            img.shape[1],
            img.shape[0],
            0,
            GL_BGR,
            GL_UNSIGNED_BYTE,
            img,
        )
        glBindVertexArray(self.vao_list[0])
        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)
        glDisable(GL_TEXTURE_2D)
        glUseProgram(0)

    def render_facemesh(self, all_face_landmarks, vertex_id_array, window_prop):
        glUseProgram(self.facemesh_program)

        itemsize = np.dtype("float32").itemsize
        glBindVertexArray(self.vao_list[1])

        facemesh_vbo = glGenBuffers(2)

        # set the vertex
        glBindBuffer(GL_ARRAY_BUFFER, facemesh_vbo[0])
        glBufferData(
            GL_ARRAY_BUFFER,
            itemsize * all_face_landmarks.size,
            all_face_landmarks,
            GL_STATIC_DRAW,
        )
        coords_attrib_location = glGetAttribLocation(self.facemesh_program, "a_vertex")
        glVertexAttribPointer(coords_attrib_location, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(coords_attrib_location)

        # set the vertex ids
        glBindBuffer(GL_ARRAY_BUFFER, facemesh_vbo[1])
        glBufferData(
            GL_ARRAY_BUFFER,
            itemsize * vertex_id_array.size,
            vertex_id_array,
            GL_STATIC_DRAW,
        )
        id_attrib_location = glGetAttribLocation(self.facemesh_program, "a_vertex_id")
        glVertexAttribPointer(id_attrib_location, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(id_attrib_location)

        # set the projection matrix
        ortho_matrix = matrix.orthographic(
            0.0, window_prop["size"][0], window_prop["size"][1], 0.0, -100.0, 100.0
        )
        ortho_matrix_location = glGetUniformLocation(
            self.facemesh_program, "u_ortho_matrix"
        )
        glUniformMatrix4fv(ortho_matrix_location, 1, GL_FALSE, ortho_matrix.matrix)

        glDrawArrays(GL_TRIANGLES, 0, all_face_landmarks.shape[0])

        glUseProgram(0)
