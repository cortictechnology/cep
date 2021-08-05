#version 300 es

in vec3 a_vertex;
in vec3 a_vertex_id;
uniform mat4 u_ortho_matrix;

out vec3 color;
out vec3 barycentric;
out vec3 position;

void main() {
    color = vec3(0.0, 0.8, 1.0);
    barycentric = a_vertex_id;
    position = a_vertex;

    gl_Position = u_ortho_matrix * vec4(a_vertex, 1);
}